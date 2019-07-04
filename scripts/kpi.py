#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
import json data from API
IMPORTANT!! you must turn off pagination for this to work from a URL
and get all country records
Install module django-extensions
Runs twice via function calls at bottom once
"""
from indicators.models import Indicator, IndicatorLevel
from workflow.models import WorkflowLevel1
from django.db import connection

cursor = connection.cursor()


def run():
    print("Setting KPI")


for program in WorkflowLevel1.objects.all():
    kpi_count = 0
    for indicator in Indicator.objects.all().filter(program__id=program.id):
        if indicator.key_performance_indicator:
            kpi_count = kpi_count + 1
    # if the program has no kpis update goal level indicators to be kpi
    if kpi_count == 0:
        # get_level = IndicatorLevel.objects.get(name="Goal")
        get_level = IndicatorLevel.objects.get(name="Impact")
        Indicator.objects.all().filter(program__id=program.id,
                                       level=get_level).update(
            key_performance_indicator=True)
    print(program)
    print(kpi_count)
