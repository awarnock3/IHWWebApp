from django.db import models

# Create your models here.
class ApxCountry(models.Model):
    id = models.IntegerField(primary_key = True)
    code = models.IntegerField()
    country = models.CharField(max_length = 40)
    template = models.CharField(max_length = 8)

class ApxObsCodes(models.Model):
    id = models.IntegerField(primary_key = True)
    system = models.CharField(max_length = 8)
    observatory = models.CharField(max_length = 40)
    location = models.CharField(max_length = 40)
    instrument = models.CharField(max_length = 60)
    lon = models.FloatField()
    lat = models.FloatField()
    subdiscipline = models.CharField(max_length = 6)
    telescope = models.CharField(max_length = 40)
    aperture = models.FloatField()
    note = models.TextField()
