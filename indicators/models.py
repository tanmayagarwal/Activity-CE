#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

import uuid
from simple_history.models import HistoricalRecords
from decimal import Decimal
from datetime import datetime, timedelta

from workflow.models import (Documentation, ActivityUser, Organization, Sector,
                             WorkflowLevel1, WorkflowLevel2, Approval)

from activity.middlewares.get_current_user import get_request


class ActivityTable(models.Model):
    name = models.CharField(max_length=255, blank=True)
    table_id = models.IntegerField(blank=True, null=True)
    owner = models.ForeignKey(ActivityUser, on_delete=models.CASCADE)
    remote_owner = models.CharField(max_length=255, blank=True)
    country = models.ManyToManyField('activity.Country', blank=True)
    url = models.CharField(max_length=255, blank=True)
    unique_count = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ActivityTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'owner',
                    'url', 'create_date', 'edit_date')
    search_fields = ('country', 'name')
    list_filter = ('country__country',)
    display = 'Activity Table'


class Objective(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    country = models.ForeignKey('activity.Country', null=True, blank=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)
    description = models.TextField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('country', 'name')

    def __str__(self):
        return self.name

    def save(self):
        if self.create_date is None:
            self.create_date = datetime.now()
        super(Objective, self).save()


class IndicatorLevel(models.Model):
    name = models.CharField(max_length=135, blank=True)
    description = models.TextField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self):
        if self.create_date is None:
            self.create_date = datetime.now()
        super(IndicatorLevel, self).save()


class LevelAdmin(admin.ModelAdmin):
    list_display = 'name'
    display = 'Levels'


class DisaggregationType(models.Model):
    disaggregation_type = models.CharField(max_length=135, blank=True)
    description = models.CharField(max_length=765, blank=True)
    country = models.ForeignKey(
        '.activity.Country', null=True, blank=True, on_delete=models.SET_NULL)
    standard = models.BooleanField(
        default=False, verbose_name="Standard (Activity Admins Only)")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.disaggregation_type


class DisaggregationTypeAdmin(admin.ModelAdmin):
    list_display = ('disaggregation_type', 'country',
                    'standard', 'description')
    list_filter = ('country', 'standard', 'disaggregation_type')
    display = 'Disaggregation Type'


class DisaggregationLabel(models.Model):
    disaggregation_type = models.ForeignKey(
        DisaggregationType, on_delete=models.CASCADE)
    label = models.CharField(max_length=765, blank=True)
    customsort = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.label


class DisaggregationLabelAdmin(admin.ModelAdmin):
    list_display = ('disaggregation_type', 'customsort', 'label',)
    display = 'Disaggregation Label'
    list_filter = ('disaggregation_type__disaggregation_type',)


class DisaggregationValue(models.Model):
    disaggregation_label = models.ForeignKey(
        DisaggregationLabel, on_delete=models.CASCADE)
    value = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.value


class DisaggregationValueAdmin(admin.ModelAdmin):
    list_display = ('disaggregation_label', 'value',
                    'create_date', 'edit_date')
    list_filter = (
        'disaggregation_label__disaggregation_type__disaggregation_type',
        'disaggregation_label')
    display = 'Disaggregation Value'


class ExternalService(models.Model):
    name = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=765, blank=True)
    feed_url = models.CharField(max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ExternalServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'feed_url', 'create_date', 'edit_date')
    display = 'External Indicator Data Service'


class ExternalServiceRecord(models.Model):
    external_service = models.ForeignKey(
        ExternalService, blank=True, null=True, on_delete=models.SET_NULL)
    full_url = models.CharField(max_length=765, blank=True)
    record_id = models.CharField("Unique ID", max_length=765, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.full_url


class ExternalServiceRecordAdmin(admin.ModelAdmin):
    list_display = ('external_service', 'full_url',
                    'record_id', 'create_date', 'edit_date')
    display = 'External Indicator Data Service'


# NEW MODELS


class ReportingPeriod(models.Model):
    period_uuid = models.UUIDField('Periodic Target UUID', editable=False, default=uuid.uuid4, unique=True)
    period = models.CharField('Reporting Period', max_length=65)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='period_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='period_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Reporting Periods'

    # displayed in admin templates
    def __str__(self):
        return self.period or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(ReportingPeriod, self).save(*args, **kwargs)


class IndicatorLevel(models.Model):
    """
    Indicator IndicatorLevel Model
    """
    indicator_level_uuid = models.UUIDField('Indicator IndicatorLevel UUID', editable=False, default=uuid.uuid4, unique=True)
    level = models.CharField('Indicator IndicatorLevel', max_length=100, unique=True)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='indicator_level_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='indicator_level_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Indicator Levels'

    # displayed in admin templates
    def __str__(self):
        return self.level or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IndicatorLevel, self).save(*args, **kwargs)


class IndicatorTag(models.Model):
    """
    Indicator Tag Model
    """
    indicator_tag_uuid = models.UUIDField('Indicator Tag UUID', editable=False, default=uuid.uuid4, unique=True)
    tag = models.CharField('Indicator Tag', max_length=100, unique=True)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='tag_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='tag_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('tag',)
        verbose_name_plural = 'Indicator Tags'

    # displayed in admin templates
    def __str__(self):
        return self.level or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IndicatorTag, self).save(*args, **kwargs)


class IndicatorType(models.Model):
    """
    Indicator Type Model
    """
    indicator_type_uuid = models.UUIDField('Indicator Type UUID', editable=False, default=uuid.uuid4, unique=True)
    type = models.CharField('Indicator Type', max_length=100, unique=True)
    description = models.TextField('Indicator Type Description', max_length=765, blank=True)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='indicator_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='indicator_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Indicator Types'

    # displayed in admin templates
    def __str__(self):
        return self.type or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IndicatorType, self).save(*args, **kwargs)


class AdditionalField(models.Model):
    """
    Additional Fields Model
    """
    additional_field_uuid = models.UUIDField('Additional Field UUID', editable=False, default=uuid.uuid4, unique=True)
    field = models.CharField('Field', max_length=255, unique=True)
    field_type = models.CharField('Additional Field Type', max_length=100, default='text')
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='add_field_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='add_field_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Additional Fields'

    # displayed in admin templates
    def __str__(self):
        return self.filed or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(AdditionalField, self).save(*args, **kwargs)


DIRECTION_CHOICES = (
        ('increasing', 'Increasing'),
        ('decreasing', 'Decreasing')
    )


class Indicator(models.Model):
    """
    Indicator Model
    """
    indicator_uuid = models.UUIDField('Indicator UUID', editable=False, default=uuid.uuid4, unique=True)
    name = models.TextField('Indicator Name', max_length=255)
    type = models.ForeignKey(IndicatorType, verbose_name='Indicator Type', null=True, on_delete=models.SET_NULL)
    objective = models.ForeignKey(Objective, verbose_name='WorkflowLevel1 Objective', null=True, on_delete=models.SET_NULL)
    level = models.ForeignKey(IndicatorLevel, verbose_name='Indicator IndicatorLevel', null=True, on_delete=models.SET_NULL)
    sector = models.ForeignKey(Sector, verbose_name='Indicator Sector', null=True, on_delete=models.SET_NULL)
    definition = models.TextField('Indicator Definition', blank=True)
    key_performance_indicator = models.BooleanField('Key Performance Indicator?', default=0)
    justification = models.TextField(max_length=500, null=True, blank=True,
                                     verbose_name='Rationale or Justification for Indicator')
    unit_of_measure = models.TextField('Unit of Measure', max_length=500, blank=True,)
    disaggregation = models.ManyToManyField(DisaggregationType)
    direction_of_change = models.CharField('Direction of Change', max_length=100, blank=True, choices=DIRECTION_CHOICES,
                                           default='increasing')
    baseline = models.DecimalField('Baseline', null=True, decimal_places=4, default=Decimal('0.0000'), max_digits=25)
    overall_target = models.DecimalField('Overall Target', null=True, default=Decimal('0.0000'), decimal_places=4,
                                         max_digits=25)
    rationale_for_target = models.TextField('Rationale for Target', max_length=500, blank=True)
    number_of_target_periods = models.IntegerField('Number of Periodic Target', default=0)
    periodic_targets = models.ManyToManyField(ReportingPeriod, verbose_name='Periodic Target')
    target_frequency = models.ForeignKey(ReportingPeriod, verbose_name='Target Frequencies', null=True, max_length=100,
                                         on_delete=models.SET_NULL)
    source = models.CharField('Source', max_length=255, blank=True)
    means_of_verification = models.TextField('Means of Verification', blank=True)
    method_of_data_collection = models.TextField('Method of Data Collection', max_length=765, blank=True)
    responsible_person = models.ForeignKey('activity.Contact', verbose_name='Responsible Person(s) and Team',
                                           null=True, on_delete=models.SET_NULL)
    method_of_analysis = models.CharField('Method of Analysis', max_length=255, blank=True)
    information_use = models.TextField('Information Use', blank=True, max_length=765)
    quality_assurance = models.TextField('Quality Assurance Measures', blank=True, max_length=765)
    data_issues = models.TextField('Data Issues', blank=True, max_length=765)
    notes = models.TextField('Changes to Indicator', max_length=765, blank=True)
    comments = models.TextField('Comments', max_length=765, blank=True)
    workflow_level1 = models.ForeignKey(WorkflowLevel1, null=True, verbose_name='Workflow Level1',
                                        on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(Approval, null=True, verbose_name='Approved By', on_delete=models.SET_NULL)
    tags = models.ManyToManyField(IndicatorTag, verbose_name='Indicator Tags', related_name='indicator_tags')
    additional_fields = models.ManyToManyField(AdditionalField, verbose_name='Additional Fields',
                                               related_name='indiactor_additional_fields')
    additional_field_values = JSONField(null=True, verbose_name='Additional Values Object')
    add_to_library = models.BooleanField('Add Indicator to Library?', default=0)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='indicator_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='indicator_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name', 'level', 'create_date',)

    def __str__(self):
        return self.name or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(AdditionalField, self).save(*args, **kwargs)


class IndicatorLibrary(models.Model):
    """
    Indicator Library Model
    """
    indicator_lib_uuid = models.UUIDField('Indicator UUID', editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField('Indicator Name', max_length=255)
    type = models.ForeignKey(IndicatorType, verbose_name='Indicator Type', null=True, on_delete=models.SET_NULL)
    objective = models.ForeignKey(Objective, verbose_name='WorkflowLevel1 Objective', null=True, on_delete=models.SET_NULL)
    level = models.ForeignKey(IndicatorLevel, verbose_name='Indicator IndicatorLevel', null=True, on_delete=models.SET_NULL)
    sector = models.ForeignKey(Sector, verbose_name='Indicator Sector', null=True, on_delete=models.SET_NULL)
    definition = models.TextField('Indicator Definition', blank=True)
    key_performance_indicator = models.BooleanField('Key Performance Indicator?', default=0)
    justification = models.TextField(max_length=500, null=True, blank=True,
                                     verbose_name='Rationale or Justification for Indicator')
    unit_of_measure = models.TextField('Unit of Measure', max_length=500, blank=True, )
    disaggregation = models.ManyToManyField(DisaggregationValue)
    direction_of_change = models.CharField('Direction of Change', max_length=100, blank=True, choices=DIRECTION_CHOICES,
                                           default='increasing')
    baseline = models.DecimalField('Baseline', null=True, decimal_places=4, default=Decimal('0.0000'), max_digits=25)
    overall_target = models.DecimalField('Overall Target', null=True, default=Decimal('0.0000'), decimal_places=4,
                                         max_digits=25)
    rationale_for_target = models.TextField('Rationale for Target', max_length=500, blank=True)
    number_of_target_periods = models.IntegerField('Number of Periodic Target', default=0)
    periodic_targets = models.ManyToManyField(ReportingPeriod, verbose_name='Periodic Target')
    periodic_targets = models.ManyToManyField(ReportingPeriod, verbose_name='Periodic Target')
    source = models.CharField('Source', max_length=255, blank=True)
    means_of_verification = models.TextField('Means of Verification', blank=True)
    method_of_data_collection = models.TextField('Method of Data Collection', max_length=765, blank=True)
    responsible_person = models.ForeignKey('activity.Contact', verbose_name='Responsible Person(s) and Team',
                                           null=True, on_delete=models.SET_NULL)
    method_of_analysis = models.CharField('Method of Analysis', max_length=255, blank=True)
    information_use = models.TextField('Information Use', blank=True, max_length=765)
    quality_assurance = models.TextField('Quality Assurance Measures', blank=True, max_length=765)
    data_issues = models.TextField('Data Issues', blank=True, max_length=765)
    notes = models.TextField('Changes to Indicator', max_length=765, blank=True)
    comments = models.TextField('Comments', max_length=765, blank=True)
    workflow_level1 = models.ForeignKey(WorkflowLevel1, null=True, verbose_name='Workflow Level1',
                                        on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(Approval, null=True, verbose_name='Approved By', on_delete=models.SET_NULL)
    tags = models.ManyToManyField(IndicatorTag, verbose_name='Indicator Tags', related_name='indicator_lib_tags')
    additional_fields = models.ManyToManyField(AdditionalField, verbose_name='Additional Fields',
                                               related_name='lib_additional_fields')
    additional_field_values = JSONField(null=True, verbose_name='Additional Values Object')
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='indicator_lib_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='indicator_lib_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IndicatorLibrary, self).save(*args, **kwargs)


class IndicatorResult(models.Model):
    """
    Indicator Result Model
    """
    result_uuid = models.UUIDField('Indicator Result UUID', editable=False, default=uuid.uuid4, unique=True)
    indicator = models.ForeignKey(Indicator, verbose_name='Indicator', on_delete=models.CASCADE)
    disaggregation_value = models.ManyToManyField(DisaggregationValue, verbose_name='Disaggregation Values',
                                                  related_name='disaggregation_values', blank=True)
    description = models.TextField('Indicator Results Description', max_length=765, blank=True)
    comment = models.TextField('Comment/Explanation', max_length=765, blank=True)
    result = models.DecimalField('Result', max_digits=20, decimal_places=4, default=Decimal('0.0000'))
    workflow_level1 = models.ForeignKey(WorkflowLevel1, verbose_name='Related WorkflowLevel1', null=True,
                                        on_delete=models.SET_NULL)
    workflow_level2 = models.ForeignKey(WorkflowLevel2, verbose_name='Related WorkflowLevel1', null=True,
                                        on_delete=models.SET_NULL)
    reporting_period = models.ForeignKey(ReportingPeriod, verbose_name='Reporting Period', null=True,
                                         on_delete=models.SET_NULL)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='result_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='result_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('indicator',)

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IndicatorResult, self).save(*args, **kwargs)

    @property
    def disaggregation_set(self):
        return ', '.join(
            ['{} : {}'.format(y.disaggregation_label.label, y.value)
             for y in self.disaggregation_value.all()]
        )

