from django.contrib import admin

from .models import CaseTag, Case, Opinion

admin.site.register(CaseTag)
admin.site.register(Case)
admin.site.register(Opinion)
