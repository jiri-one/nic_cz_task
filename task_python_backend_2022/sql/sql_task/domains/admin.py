from django.contrib import admin

from .models import *

for model in [Domain, DomainFlag]:
    admin.site.register(model)
