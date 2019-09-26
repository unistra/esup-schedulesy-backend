import json
import time

from django.conf import settings

from .ade import ADEWebAPI, Config
from .models import Resource, Fingerprint


class Flatten:
    def __init__(self, data):
        self.data = data
        self.f_data = {}
        self._flatten()

    def _flatten(self, item=None):
        if not item:
            item = self.data

        if item['tag'] == 'category':
            item['id'] = item['category']
            item['name'] = item['category']

        children_ref = []
        if 'children' in item:
            for child in item['children']:
                ref = self._flatten(child)
                if ref:
                    children_ref.append(ref)

        if 'id' in item:
            key = item['id']
            if key in self.f_data:
                print("Double key {}".format(key))
            else:
                tmp = item.copy()
                if len(children_ref) > 0:
                    tmp['children'] = children_ref
                self.f_data[key] = tmp
            result = {'id': key, 'name': item['name']}
            result['has_children'] = len(children_ref) > 0
            return result

        return None


class Refresh:
    METHOD_GET_RESOURCE = "getResources"

    def __init__(self):
        config = Config.create(url=settings.ADE_WEB_API['HOST'],
                               login=settings.ADE_WEB_API['USER'],
                               password=settings.ADE_WEB_API['PASSWORD'])
        self.myade = ADEWebAPI(**config)
        self.myade.connect()
        self.myade.setProject(settings.ADE_WEB_API['PROJECT_ID'])
        self.data = {}

    def refresh_resource(self, ext_id):
        try:
            resource = Resource.objects.get(ext_id=ext_id)
            print("{}".format(resource.fields))
            print("pouet")
            fingerprint = Fingerprint.objects.get(ext_id=resource.fields['category'])
            # May seems brutal but ADE API doesn't give children if object is called individually
            fingerprint.fingerprint = "toRefresh"
            fingerprint.save()
            self.refresh_category(resource.fields['category'])
        except Resource.DoesNotExist:
            for fingerprint in Fingerprint.objects.all():
                fingerprint.fingerprint = "toRefresh"
                fingerprint.save()
                self.refresh_all()

    def refresh_all(self):
        for r_type in ['classroom', 'instructor', 'trainee', 'category5']:
            self.refresh_category(r_type)

    def refresh_category(self, r_type):
        method = Refresh.METHOD_GET_RESOURCE

        tree = self.myade.getResources(category=r_type, detail=3, tree=True, hash=True)
        n_fp = tree['hash']

        try:
            o_fp = Fingerprint.objects.all().get(ext_id=r_type, method=method)
        except:
            o_fp = None

        key = "{}-{}".format(method, r_type)
        self.data[key] = {'status': 'unchanged', 'fingerprint': n_fp}

        if not o_fp or o_fp.fingerprint != n_fp:
            start = time.clock()
            resources = Resource.objects.all().filter(fields__category=r_type)
            test = Flatten(tree['data']).f_data

            nb_created = 0
            nb_updated = 0
            for k, v in test.items():
                resource, created = resources.get_or_create(ext_id=k, defaults={'fields': v})
                if not created:
                    if resource.fields != v:
                        resource.fields = v
                        resource.save()
                        nb_updated += 1
                else:
                    nb_created += 1
            if o_fp:
                o_fp.fingerprint = n_fp
            else:
                o_fp=Fingerprint(ext_id=r_type, method=method, fingerprint=n_fp)
            o_fp.save()
            elapsed = time.clock() - start
            self.data[key]['status'] = 'modified'
            self.data[key]['updated'] = nb_updated
            self.data[key]['created'] = nb_created
            self.data[key]['elapsed'] = elapsed
