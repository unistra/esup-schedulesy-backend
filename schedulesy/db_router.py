class DBRouter:  # pragma: no cover

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
        db_list = ('default', 'ade')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
