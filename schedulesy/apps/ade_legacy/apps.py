from django.apps import AppConfig


class AdeLegacyConfig(AppConfig):
    name = 'schedulesy.apps.ade_legacy'

    def ready(self):
        from health_check.plugins import plugin_dir

        from schedulesy.apps.ade_legacy.backends import (
            ADECheckBackend,
            ADEWebAPI,
            WorkerBackend,
        )

        plugin_dir.register(ADECheckBackend)
        plugin_dir.register(WorkerBackend)
        plugin_dir.register(ADEWebAPI)
