from django.contrib import admin

from clients.models import Client, CompanyName

# Register your models here.
admin.site.register(Client)
admin.site.register(CompanyName)