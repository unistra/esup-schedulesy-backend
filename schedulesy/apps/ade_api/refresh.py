import json

from schedulesy.models import Resource
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
        config = Config.create(url='https://adeweb.unistra.fr/jsp/webapi', login='toto', password='toto')
        myade = ADEWebAPI(**config)
        myade.connect()
        myade.setProject(5)
        for r_type in ['classroom', 'instructor', 'trainee', 'category5']:
            Resource.objects.all().filter(fields__category=r_type).delete()
            tree = myade.getResources(category=r_type, detail=3, tree=True, hash=True)
            open("{}.json".format(r_type), 'w').write(json.dumps(tree))
            print(tree['hash'])
            test = Flatten(tree['data']).f_data

            for key, value in test.items():
                resource = Resource(ext_id=key, fields=value)
                resource.save()

        self.data = test
        print("done")