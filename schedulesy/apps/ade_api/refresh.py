import logging
import re
import time
import uuid
from collections import OrderedDict

from django.conf import settings
from django.db import IntegrityError
from sentry_sdk import capture_exception

from schedulesy.libs.api.client import get_geolocations, to_ade_id
from schedulesy.libs.decorators import (
    MemoizeWithTimeout,
    async_log,
    refresh_if_necessary,
)

from .ade import ADEWebAPI, Config
from .models import Fingerprint, Resource

logger = logging.getLogger(__name__)


class Flatten:
    def __init__(self, data):
        self.data = data
        self.f_data = OrderedDict()
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
                    me.append(
                        {
                            'id': item['id'],
                            'name': item['name'],
                            'code': item.get('code', ''),
                        }
                    )
                ref = self._flatten(child, me)
                if ref:
                    children_ref.append(ref)

        if 'id' in item:
            key = item['id']
            if key in self.f_data:
                print(f"Double key {key}")
            else:
                tmp = item.copy()
                if genealogy:
                    tmp['parent'] = genealogy[-1]['id']
                    tmp['genealogy'] = genealogy
                if len(children_ref) > 0:
                    tmp['children'] = children_ref
                self.f_data[key] = tmp
            result = OrderedDict()
            result.update(
                {'id': key, 'name': item['name'], 'code': item.get('code', '')}
            )
            result['has_children'] = len(children_ref) > 0
            return result

        return None


class Refresh:
    METHOD_GET_RESOURCE = "getResources"
    EVENTS_ATTRIBUTE_FILTERS = (
        'id',
        'activityId',
        'name',
        'endHour',
        'startHour',
        'date',
        'duration',
        'lastUpdate',
        'category',
        'color',
        'note',
    )

    def __init__(self):
        self.data = {}
        self.myade = ade_connection()

    def refresh_single_resource(self, ext_id, operation_id):
        resource = None
        logger.debug(f"{operation_id} / Refreshing resource {ext_id}")
        try:
            resource = Resource.objects.get(ext_id=ext_id)
            self._simple_resource_refresh(resource, operation_id)
        except (Resource.DoesNotExist, KeyError):
            logger.debug(f"Didn't find {ext_id}")
            # Fingerprint.objects.update(fingerprint='toRefresh')
            self.refresh_all()

        if isinstance(ext_id, int) or re.fullmatch(r'[0-9]*', ext_id):
            r = self.myade.getEvents(
                resources=ext_id,
                detail=0,
                attribute_filter=self.EVENTS_ATTRIBUTE_FILTERS,
            )

            if resource is None:
                resource = Resource.objects.get(ext_id=ext_id)

            events = self._reformat_events(r['data'])
            resource.events = events
            resource.save()

    @staticmethod
    def _simple_resource_refresh(resource, operation_id):
        """
        :param Resource resource:
        :return:
        """
        if resource.fields is not None and 'category' in resource.fields:
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
        else:
            logger.warning(f'Inconsistent resource {resource.id} : {resource.fields}')

    def _reformat_events(self, data):
        events = []
        classrooms = {}
        resources = {}

        if 'children' in data:
            for element in data['children']:
                element.pop('tag', None)
                element['color'] = '#' + ''.join(
                    f'{int(x):02x}' for x in element['color'].split(',')
                )
                children = element.get('children', [])
                if len(children) and 'children' in children[0]:
                    local_resources = {}
                    for resource in children[0]['children']:
                        # TODO improve plural
                        r_id = resource['id']
                        c_name = f'{resource["category"]}s'
                        tmp_r = {'name': resource['name']}

                        # Adding building to resource
                        self._add_building(classrooms, r_id, c_name, tmp_r)

                        resources.setdefault(c_name, {})[r_id] = tmp_r
                        local_resources.setdefault(c_name, []).append(r_id)

                    element.update(local_resources)
                    element.pop('children')
                events.append(element)
        result = {'events': events, **resources}
        return result

    def _add_building(self, classrooms, r_id, c_name, tmp_r, *args, **kwargs):
        # tmp_r is a reference and should not be reassigned
        if c_name == 'classrooms':
            if r_id not in classrooms:
                classrooms[r_id] = Resource.objects.get(ext_id=r_id)
            parents = []
            geolocation = []
            for index, x in enumerate(classrooms[r_id].fields['genealogy']):
                parents.append(x['name'])
                if index >= 2:
                    code = to_ade_id(x['code'])
                    local_geolocation = get_geolocations().get(code, [])
                    geolocation = (
                        local_geolocation if local_geolocation else geolocation
                    )

            tmp_r['genealogy'] = parents[1:]
            tmp_r['geolocation'] = geolocation

    def refresh_all(self):
        for r_type in ('classroom', 'instructor', 'trainee', 'category5'):
            self.refresh_category(r_type)

    @refresh_if_necessary
    def refresh_category(self, r_type):
        logger.debug(f"Refreshing category {r_type}")
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
            start = time.time()
            all_ext_ids = Resource.objects.all().values_list('ext_id', flat=True)
            resources = Resource.objects.filter(fields__category=r_type)
            indexed_resources = {r.ext_id: r for r in resources}
            # Dict id reversed to preserve links of parenthood

            test = OrderedDict(reversed(list(Flatten(tree['data']).f_data.items())))

            nb_created = 0
            nb_updated = 0
            nb_deleted = 0

            def update(to_update, data):
                if to_update.fields != data:
                    to_update.fields = data
                    if "parent" in data:
                        try:
                            to_update.parent = indexed_resources[data["parent"]]
                        except KeyError:
                            logger.warning(
                                f"Missing parent resource for {to_update.ext_id}"
                            )
                    to_update.save()
                    return True
                return False

            def create(ext_id, data):
                # Non existing elements
                r = Resource(ext_id=ext_id, fields=data)
                logger.debug(f'Creating resource {ext_id} : {data}')
                if "parent" in data:
                    r.parent = indexed_resources[data["parent"]]
                try:
                    r.save()
                except IntegrityError as error:
                    logger.error(error)
                indexed_resources[ext_id] = r

            # Fixes errors
            for resource in [
                r
                for r in Resource.objects.filter(fields__isnull=True)
                if r.ext_id in test
            ]:
                v = test[resource.ext_id]
                logger.debug(f'Fixing missing fields for {resource.ext_id}')
                if update(resource, v):
                    nb_updated += 1

            for k, v in test.items():
                if k not in indexed_resources and k not in all_ext_ids:
                    create(k, v)
                    nb_created += 1
                else:
                    # Existing elements
                    try:
                        resource = indexed_resources[k]
                        if update(resource, v):
                            nb_updated += 1
                    except KeyError:
                        logger.warning(f"Fixing inconsistency for resource {k}")
                        r_del = Resource.objects.get(ext_id=k)
                        logger.info(
                            "Resource {} - {} to delete".format(
                                r_del.ext_id, r_del.fields['name']
                            )
                        )
                        r_del.delete()
                        nb_deleted += 1
                        create(k, v)
                        nb_created += 1

            # Clean resources
            for resource in [
                v for k, v in indexed_resources.items() if k not in test.keys()
            ]:
                logger.info(
                    "Resource {} - {} to delete".format(
                        resource.ext_id, resource.fields['name']
                    )
                )
                resource.delete()
                nb_deleted += 1

            if o_fp:
                o_fp.fingerprint = n_fp
            else:
                o_fp = Fingerprint(ext_id=r_type, method=method, fingerprint=n_fp)
            o_fp.save()
            elapsed = time.time() - start
            self.data[key].update(
                {
                    'status': 'modified',
                    'updated': nb_updated,
                    'created': nb_created,
                    'deleted': nb_deleted,
                    'elapsed': elapsed,
                }
            )

    def refresh_event(self, ext_id, activity_id, resources, operation_id):
        # {'instructors': ['2', '3']}>
        logger.debug(f"{operation_id} / {activity_id}")
        old_resources = {
            str(r.pk): r
            for r in Resource.objects.filter(events__events__contains=[{'id': ext_id}])
        }
        new_resources = {
            str(r.pk): r for r in Resource.objects.filter(ext_id__in=resources)
        }

        if len(new_resources) != len(resources):
            # TODO: create new resources if missing ?
            capture_exception('Some resources are missing in the event refresh')

        all_resources = dict(**old_resources, **new_resources)
        for r_id, resource in all_resources.items():
            r = self.myade.getEvents(
                resources=resource.ext_id,
                detail=0,
                attribute_filter=self.EVENTS_ATTRIBUTE_FILTERS,
            )
            events = self._reformat_events(r['data'])
            resource.events = events
            resource.save()


@MemoizeWithTimeout(timeout=30)
def ade_connection():
    config = Config.create(
        url=settings.ADE_WEB_API['HOST'],
        login=settings.ADE_WEB_API['USER'],
        password=settings.ADE_WEB_API['PASSWORD'],
    )
    connection = ADEWebAPI(**config)
    connection.connect()
    connection.setProject(settings.ADE_WEB_API['PROJECT_ID'])
    return connection


@MemoizeWithTimeout(timeout=30)
def ade_resources(category, operation_id='standard'):
    return ade_connection().getResources(
        category=category, detail=11, tree=True, hash=True
    )
