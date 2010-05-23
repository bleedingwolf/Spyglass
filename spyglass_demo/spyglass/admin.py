
from django.contrib import admin

from spyglass.models import HttpSession


class HttpSessionAdmin(admin.ModelAdmin):
    pass


admin.site.register(HttpSession, HttpSessionAdmin)
