class DBRouter:

    _alias = 'ade_legacy'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self._alias:
            return 'ade'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self._alias:
            return 'ade'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self._alias or \
           obj2._meta.app_label == self._alias:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self._alias:
            return db == 'ade'
        return None
