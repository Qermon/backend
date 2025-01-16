from django.contrib.auth.models import User
from django.db import models


class CompanyName(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    company_name = models.ForeignKey(CompanyName, on_delete=models.PROTECT)
    full_address = models.CharField(max_length=100)

    def __str__(self):
        return f'Client:{self.user}, Company{self.company_name}'


