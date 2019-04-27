from __future__ import absolute_import
from django.contrib import admin

from .models import Report, ReportAdmin


admin.site.register(Report, ReportAdmin)







