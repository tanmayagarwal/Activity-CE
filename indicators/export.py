#!/usr/bin/python3
# -*- coding: utf-8 -*-

from import_export import resources
from .models import Indicator, IndicatorResult, WorkflowLevel1, Sector, ReportingPeriod
from workflow.models import WorkflowLevel2, WorkflowLevel2, ActivityUser
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from import_export import fields


class IndicatorResource(resources.ModelResource):

    indicator_type = fields.Field(
        column_name='indicator types', attribute='indicator_types')
    objectives = fields.Field(column_name='objectives',
                              attribute='objectives_list')
    strategic_objectives = fields.Field(
        column_name='strategic objectives',
        attribute='strategicobjectives_list')
    program = fields.Field(column_name='program', attribute='programs')
    sector = fields.Field(column_name='sector', attribute='sector',
                          widget=ForeignKeyWidget(Sector, 'sector'))
    reporting_frequency = fields.Field(column_name='reporting_frequency',
                                       attribute='reporting_frequency',
                                       widget=ForeignKeyWidget(
                                           ReportingPeriod, 'frequency'))
    level = fields.Field(column_name='levels', attribute='levels')
    disaggregation = fields.Field(
        column_name='disaggregation', attribute='disaggregations')
    approval_submitted_by = fields.Field(column_name='approval submitted by',
                                         attribute='approval_submitted_by',
                                         widget=ForeignKeyWidget(ActivityUser,
                                                                 'name'))
    approved_by = fields.Field(
        column_name='approved by', attribute='approved_by',
        widget=ForeignKeyWidget(ActivityUser, 'name'))

    class Meta:
        model = Indicator
        exclude = ('create_date', 'edit_date', 'owner',
                   'id', 'strategic_objective', 'objective')


class IndicatorAdmin(ImportExportModelAdmin):
    resource_class = IndicatorResource


class CollectedDataResource(resources.ModelResource):

    indicator = fields.Field(column_name='indicator', attribute='indicator',
                             widget=ForeignKeyWidget(Indicator, 'name_clean'))
    indicator_number = fields.Field(
        column_name='indicator_number', attribute='indicator',
        widget=ForeignKeyWidget(Indicator, 'number'))
    indicator_level = fields.Field(
        column_name='indicator_level', attribute='indicator',
        widget=ForeignKeyWidget(Indicator, 'levels'))
    agreement = fields.Field(column_name='agreement', attribute='agreement',
                             widget=ForeignKeyWidget(
                                 WorkflowLevel2, 'project_name_clean'))
    complete = fields.Field(column_name='complete', attribute='complete',
                            widget=ForeignKeyWidget(
                                WorkflowLevel2, 'project_name_clean'))
    program = fields.Field(column_name='program', attribute='program',
                           widget=ForeignKeyWidget(WorkflowLevel1, 'name'))
    disaggregations = fields.Field(
        column_name='dissaggregations', attribute='disaggregations')

    class Meta:
        model = IndicatorResult
        exclude = ('create_date', 'edit_date')


class CollectedDataAdmin(ImportExportModelAdmin):
    resource_class = CollectedDataResource
