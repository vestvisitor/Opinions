from django.contrib import admin

from .models import CaseTag, Case, Opinion, CaseOpinion

admin.site.register(CaseTag)
admin.site.register(Case)
admin.site.register(Opinion)
admin.site.register(CaseOpinion)
