import json
import os
import time

from django.conf import settings
from django.db.models import Q
from psycopg2._psycopg import IntegrityError
from sentry_sdk import capture_exception

from .ade import ADEWebAPI, Config
from .decorators import MemoizeWithTimeout
from .models import Resource, Fingerprint


class Flatten:
    def __init__(self, data):
        self.data = data
        self.f_data = {}
        self._flatten()

    def _flatten(self, item=None, genealogy=None):
        if not item:
            item = self.data

        if item['tag'] == 'category':
            item['id'] = item['category']
            item['name'] = item['category']

        children_ref = []
        if 'children' in item:
            for child in item['children']:
                me = None
                if 'id' in item:
                    me = list(genealogy) if genealogy is not None else []
                    me.append({'id': item['id'], 'name': item['name']})
                ref = self._flatten(child, me)
                if ref:
                    children_ref.append(ref)

        if 'id' in item:
            key = item['id']
            if key in self.f_data:
                print("Double key {}".format(key))
            else:
                tmp = item.copy()
                if genealogy:
                    tmp['parent'] = genealogy[-1]['id']
                    tmp['genealogy'] = genealogy
                if len(children_ref) > 0:
                    tmp['children'] = children_ref
                self.f_data[key] = tmp
            result = {'id': key, 'name': item['name']}
            result['has_children'] = len(children_ref) > 0
            return result

        return None


class Refresh:
    METHOD_GET_RESOURCE = "getResources"
    EVENTS_ATTRIBUTE_FILTERS = (
        'id', 'activityId', 'name', 'endHour', 'startHour', 'date', 'duration',
        'lastUpdate', 'category', 'color'
    )

    def __init__(self):
        self.data = {}
        self.myade = ade_connection()

    def refresh_resource(self, ext_id, operation_id):
        resource = None
        try:
            resource = Resource.objects.get(ext_id=ext_id)
            self._simple_resource_refresh(resource, operation_id)
        except Resource.DoesNotExist:
            Fingerprint.objects.update(fingerprint='toRefresh')
            self.refresh_all()

        r = self.myade.getEvents(
            resources=ext_id, detail=0,
            attribute_filter=self.EVENTS_ATTRIBUTE_FILTERS)

        if resource is None:
            resource = Resource.objects.get(ext_id=ext_id)

        events = self._reformat_events(r['data'])
        resource.events = events
        resource.save()

    def _simple_resource_refresh(self, resource, operation_id):
        """
        :param Resource resource:
        :return:
        """
        tree = ade_resources(resource.fields['category'], operation_id)
        ade_data = dict(reversed(list(Flatten(tree['data']).f_data.items())))
        v = ade_data[resource.ext_id]
        if resource.fields != v:
            resource.fields = v
            # TODO: check if parent are different to prevent useless query ?
            if "parent" in v:
                if not resource.parent_id or resource.parent_id != v["parent"]:
                    resource.parent = Resource.objects.get(ext_id=v["parent"])
            else:
                resource.parent = None
            resource.save()

    def _reformat_events(self, data):
        events = []
        classrooms = {}
        resources = {}
        if 'children' in data:
            for element in data['children']:
                element.pop('tag', None)
                element['color'] = '#' + ''.join(f'{int(x):02x}' for x in element['color'].split(','))
                children = element.get('children', [])
                if len(children) and 'children' in children[0]:
                    local_resources = {}
                    for resource in children[0]['children']:
                        # TODO improve plural
                        r_id = resource['id']
                        c_name = f'{resource["category"]}s'
                        tmp_r = {'name': resource['name']}

                        # Adding building to resource
                        if c_name == 'classrooms':
                            if r_id not in classrooms:
                                classrooms[r_id] = Resource.objects.get(ext_id=r_id)
                            tmp_r['genealogy'] = [x['name'] for x in classrooms[r_id].fields['genealogy']][1:]

                        resources.setdefault(c_name, {})[r_id] = tmp_r
                        local_resources.setdefault(c_name, []).append(r_id)

                    element.update(local_resources)
                    element.pop('children')
                events.append(element)
        result = {'events': events, **resources}
        return result

    def refresh_all(self):
        for r_type in ('classroom', 'instructor', 'trainee', 'category5'):
            self.refresh_category(r_type)

    def refresh_category(self, r_type):
        method = Refresh.METHOD_GET_RESOURCE

        tree = ade_resources(r_type)
        n_fp = tree['hash']

        try:
            o_fp = Fingerprint.objects.get(ext_id=r_type, method=method)
        except Fingerprint.DoesNotExist:
            o_fp = None

        key = f'{method}-{r_type}'
        self.data[key] = {'status': 'unchanged', 'fingerprint': n_fp}

        if not o_fp or o_fp.fingerprint != n_fp:
            start = time.clock()
            resources = Resource.objects.filter(fields__category=r_type)
            indexed_resources = {r.ext_id: r for r in resources}
            # Dict id reversed to preserve links of parenthood

            test = dict(reversed(list(Flatten(tree['data']).f_data.items())))

            nb_created = 0
            nb_updated = 0

            for k, v in test.items():
                if k not in indexed_resources:
                    # Non existing elements
                    resource = Resource(ext_id=k, fields=v)
                    if "parent" in v:
                        resource.parent = indexed_resources[v["parent"]]
                    try:
                        resource.save()
                    except IntegrityError as error:
                        # Should not happen
                        capture_exception(error)
                    indexed_resources[k] = resource
                    nb_created += 1
                else:
                    # Existing elements
                    resource = indexed_resources[k]
                    if resource.fields != v:
                        resource.fields = v
                        if "parent" in v:
                            resource.parent = indexed_resources[v["parent"]]
                        resource.save()
                        indexed_resources[k] = resource
                        nb_updated += 1
            if o_fp:
                o_fp.fingerprint = n_fp
            else:
                o_fp = Fingerprint(ext_id=r_type, method=method, fingerprint=n_fp)
            o_fp.save()
            elapsed = time.clock() - start
            self.data[key].update({
                'status': 'modified',
                'updated': nb_updated,
                'created': nb_created,
                'elapsed': elapsed
            })

    def refresh_event(self, ext_id, activity_id, resources, operation_id):
        # {'instructors': ['2', '3']}>
        old_resources = (
            {str(r.pk): r for r in Resource.objects
             .filter(events__events__contains=[{'id': ext_id}])})
        new_resources = (
            {str(r.pk): r for r in Resource.objects
             .filter(ext_id__in=resources)})

        if len(new_resources) != len(resources):
            # TODO: create new resources if missing ?
            capture_exception('Some resources are missing in the event refresh')

        all_resources = dict(**old_resources, **new_resources)
        for r_id, resource in all_resources.items():
            r = self.myade.getEvents(
                resources=resource.ext_id, detail=0,
                attribute_filter=self.EVENTS_ATTRIBUTE_FILTERS)
            events = self._reformat_events(r['data'])
            resource.events = events
            resource.save()


@MemoizeWithTimeout()
def ade_connection():
    config = Config.create(url=settings.ADE_WEB_API['HOST'],
                           login=settings.ADE_WEB_API['USER'],
                           password=settings.ADE_WEB_API['PASSWORD'])
    connection = ADEWebAPI(**config)
    connection.connect()
    connection.setProject(settings.ADE_WEB_API['PROJECT_ID'])
    return connection


@MemoizeWithTimeout()
def ade_resources(category, operation_id='standard'):
    return ade_connection().getResources(category=category, detail=3, tree=True, hash=True)
