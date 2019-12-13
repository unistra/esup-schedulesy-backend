from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=32)
    username = models.CharField(max_length=32)


class Info(models.Model):
    data = models.CharField(max_length=32)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
