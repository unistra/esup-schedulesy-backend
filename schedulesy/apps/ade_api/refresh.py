import json
import time

from django.conf import settings

from schedulesy.models import Resource, Fingerprint
from .ade import ADEWebAPI, Config

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
                # if len(children_ref) > 0:
                tmp['children'] = children_ref
                self.f_data[key] = tmp
            return {'id': key, 'name': item['name']}

        return None


class Refresh:
    def __init__(self):
        config = Config.create(url=settings.ADE_WEB_API['HOST'],
                               login=settings.ADE_WEB_API['USER'],
                               password=settings.ADE_WEB_API['PASSWORD'])
        myade = ADEWebAPI(**config)
        myade.connect()
        myade.setProject(5)
        method = 'getResources'
        self.data = {}
        for r_type in ['classroom', 'instructor', 'trainee', 'category5']:
            tree = myade.getResources(category=r_type, detail=3, tree=True, hash=True)
            n_fp = tree['hash']

            try:
                o_fp = Fingerprint.objects.all().get(ext_id=r_type, method=method)
            except:
                o_fp = None

            key = "{}-{}".format(method, r_type)
            self.data[key] = {'status': 'unchanged', 'fingerprint': n_fp}

            if not o_fp or o_fp.fingerprint != n_fp:
                start = time.clock()
                Resource.objects.all().filter(fields__category=r_type).delete()
                test = Flatten(tree['data']).f_data

                count = 0
                for k, v in test.items():
                    resource = Resource(ext_id=k, fields=v)
                    resource.save()
                    count += 1
                if o_fp:
                    o_fp.fingerprint = n_fp
                else:
                    o_fp=Fingerprint(ext_id=r_type, method=method, fingerprint=n_fp)
                o_fp.save()
                elapsed = time.clock() - start
                self.data[key]['status'] = 'updated'
                self.data[key]['count'] = count
                self.data[key]['elapsed'] = elapsed
