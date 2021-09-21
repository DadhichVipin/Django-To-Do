from django.contrib import admin
from .models import Task

# here we register our models
admin.site.register(Task)
