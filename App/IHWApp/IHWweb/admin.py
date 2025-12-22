from django.contrib import admin

from .models import ApxCountry, ApxObsCodes

# Register your models here.
admin.site.register(ApxCountry)
admin.site.register(ApxObsCodes)
