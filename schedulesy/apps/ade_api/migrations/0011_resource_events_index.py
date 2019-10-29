from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ade_api', '0010_localcustomization_configuration'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE INDEX IF NOT EXISTS ade_api_resource_expr_idx
            ON public.ade_api_resource
            USING gin
            ((events -> 'events'::text) jsonb_path_ops)
            """,
            'DROP INDEX IF EXISTS public.ade_api_resource_expr_idx'
        ),
    ]
