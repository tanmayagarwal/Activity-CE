#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from workflow.models import (WorkflowLevel1, WorkflowLevel2,)
from indicators.models import (Indicator, IndicatorResult)
from activity.models import (Country,)


class Report(models.Model):
    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.SET_NULL)
    workflow_level1 = models.ForeignKey(
        WorkflowLevel1, null=True, blank=True, on_delete=models.SET_NULL)
    workflow_level2 = models.ForeignKey(
        WorkflowLevel2, null=True, blank=True, on_delete=models.SET_NULL)
    indicator = models.ForeignKey(
        Indicator, null=True, blank=True, on_delete=models.SET_NULL)
    collected = models.ForeignKey(
        IndicatorResult, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.CharField(
        "Status Description", max_length=200, blank=True)
    shared = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.program.name


class ReportAdmin(admin.ModelAdmin):
    list_display = ('country', 'workflow_level1', 'description',
                    'create_date', 'edit_date')
    display = 'Project Status'
