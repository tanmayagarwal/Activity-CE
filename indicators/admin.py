#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .models import *
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin


# class IndicatorResource(resources.ModelResource):
#
#     indicator_type = ManyToManyWidget(
#         IndicatorType, separator=" | ", field="indicator_type")
#     objective = ManyToManyWidget(
#         Objective, separator=" | ", field="objective"),
#     strategic_objective = ManyToManyWidget(
#         Objective, separator=" | ", field="strategic_objective")
#     level = ManyToManyWidget(IndicatorLevel, separator=" | ", field="level")
#     reporting_frequency = fields.Field(
#         column_name='reporting_frequency',
#         attribute='reporting_frequency',
#         widget=ForeignKeyWidget(ReportingPeriod, 'frequency'))
#     sector = fields.Field(column_name='sector', attribute='sector',
#                           widget=ForeignKeyWidget(Sector, 'sector'))
#     program = ManyToManyWidget(WorkflowLevel1, separator=" | ", field="name")
#
#     class Meta:
#         model = Indicator
#         fields = (
#             'id', 'indicator_type', 'level', 'objective',
#             'strategic_objective', 'name', 'number', 'source', 'definition',
#             'justification', 'unit_of_measure', 'baseline', 'lop_target',
#             'rationale_for_target', 'means_of_verification',
#             'data_collection_method', 'data_collection_frequency',
#             'data_points', 'responsible_person', 'method_of_analysis',
#             'information_use', 'reporting_frequency', 'quality_assurance',
#             'data_issues', 'indicator_changes', 'comments', 'disaggregation',
#             'sector', 'program', 'key_performance_indicator')


# class IndicatorAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
#     resource_class = IndicatorResource
#     list_display = ('indicator_types', 'name', 'sector',
#                     'key_performance_indicator')
#     search_fields = ('name', 'number', 'program__name')
#     list_filter = ('program', 'key_performance_indicator', 'sector')
#     display = 'Indicators'
#     filter_horizontal = ('program', 'objectives',
#                          'strategic_objectives', 'disaggregation', 'program')
#     pass


class ActivityTableResource(resources.ModelResource):

    class Meta:
        model = ActivityTable
        fields = ('id', 'name', 'table_id', 'owner', 'remote_owner', 'url')


class ActivityTableAdmin(ImportExportModelAdmin):
    list_display = ('name', 'owner', 'url', 'create_date', 'edit_date')
    search_fields = ('country__country', 'name')
    list_filter = ('country__country',)
    display = 'Activity Table'
    pass


admin.site.register(DisaggregationType, DisaggregationTypeAdmin)
admin.site.register(DisaggregationLabel, DisaggregationLabelAdmin)
admin.site.register(ExternalService, ExternalServiceAdmin)
admin.site.register(ExternalServiceRecord, ExternalServiceRecordAdmin)
admin.site.register(ActivityTable, ActivityTableAdmin)


# New Models
@admin.register(IndicatorLevel)
class IndicatorLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'created_by', 'create_date')
    list_filter = ('level', 'created_by')
    display = 'Indicator Types'


@admin.register(Objective)
class StrategicObjectiveAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'create_date', 'parent')
    list_filter = ('parent', 'name', 'organization')
    display = 'Objectives'


@admin.register(IndicatorType)
class IndicatorTypeAdmin(admin.ModelAdmin):
    # list_display = ('type', 'created_by', 'create_date')
    # list_filter = ('type', 'created_by')
    display = 'Indicator Types'


@admin.register(IndicatorTag)
class IndicatorTagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'Indicator Tags'


@admin.register(Indicator)
class Indicator1Admin(admin.ModelAdmin):
    list_display = ('name', 'type', 'key_performance_indicator')
    list_filter = ('name', 'level', 'workflow_level1')
    display = 'Indicators'


@admin.register(IndicatorLibrary)
class IndicatorLibraryAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ('name',)
    display = 'Indicator Library'


@admin.register(IndicatorResult)
class IndicatorResultsAdmin(admin.ModelAdmin):
    list_display = ()
    list_filter = ('indicator',)
    display = 'Indicator Library'

