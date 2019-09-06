class DBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ade_legacy':
            return 'ade'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ade_legacy':
            return 'ade'
        return 'default'
