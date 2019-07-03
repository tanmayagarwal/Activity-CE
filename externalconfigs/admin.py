from django.contrib import admin

from .models import *
# Register your models here.


@admin.register(IatiAidType)
class IatiAidTypeAdmin(admin.ModelAdmin):
    list_display = ('aid_type', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI Aid Types'


@admin.register(IatiFinanceType)
class IatiFinanceTypeAdmin(admin.ModelAdmin):
    list_display = ('finance_type', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI Finance Types'


@admin.register(IatiFlowType)
class IatiFlowTypeAdmin(admin.ModelAdmin):
    list_display = ('flow_type', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI Flow Types'


@admin.register(IatiCondition)
class IatiConditionAdmin(admin.ModelAdmin):
    list_display = ('condition', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI Conditions'


@admin.register(IatiTiedStatus)
class IatiTiedStatusAdmin(admin.ModelAdmin):
    list_display = ('tied_status', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI Tied Status Types'


@admin.register(IatiCollaborationType)
class IatiCollaborationTypeAdmin(admin.ModelAdmin):
    list_display = ('collaboration_type', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI Collaboration Types'


@admin.register(IatiProjectStatus)
class IatiProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('project_status', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI Project Statuses'


@admin.register(Iati)
class IatiAdmin(admin.ModelAdmin):
    list_display = ('activity_identifier', 'created_by', 'create_date')
    list_filter = ('created_by',)
    display = 'IATI'

