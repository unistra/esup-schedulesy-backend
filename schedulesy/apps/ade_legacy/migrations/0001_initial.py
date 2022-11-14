# Generated by Django 3.2.16 on 2022-11-07 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customization',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('display_configuration', models.CharField(db_column='configuration_affichage', default='', max_length=60)),
                ('resources', models.CharField(blank=True, db_column='ressources', default='', max_length=300)),
                ('directory_id', models.CharField(db_column='uds_directory_id', max_length=32, unique=True)),
                ('rh_id', models.CharField(db_column='code_harp', default='', max_length=15)),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_column='date_creation')),
                ('customization_date', models.DateTimeField(auto_now=True, db_column='date_personnalisation')),
                ('username', models.CharField(db_column='uid', max_length=32)),
            ],
            options={
                'verbose_name': 'Customization',
                'verbose_name_plural': 'Customizations',
                'db_table': 'w_edtperso',
                'managed': True,
            },
        ),
    ]
