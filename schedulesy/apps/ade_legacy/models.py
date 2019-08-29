from django.db import models


# Create your models here.
class Customization(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    display_configuration = models.CharField(max_length=60, db_column='configuration_affichage', blank=True)
    resources = models.CharField(max_length=300, db_column='ressources', blank=True)
    directory_id = models.CharField(max_length=32, db_column='uds_directory_id')
    rh_id = models.CharField(max_length=15, db_column='code_harp', blank=True)
    creation_date = models.DateTimeField(db_column='date_creation', blank=True, null=True, auto_now_add=True)
    customization_date = models.DateTimeField(db_column='date_personnalisation', blank=True, null=True, auto_now=True)
    username = models.CharField(max_length=32, db_column='uid', blank=True)

    class Meta:
        managed = False
        db_table = 'w_edtperso'
