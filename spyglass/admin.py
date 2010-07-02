
from django.contrib import admin

from spyglass.models import HttpSession, HttpRedirect


class HttpSessionAdmin(admin.ModelAdmin):
    pass


admin.site.register(HttpSession, HttpSessionAdmin)
admin.site.register(HttpRedirect)
