from django.db import models

from django.utils import timezone

import uuid

from activity.middlewares.get_current_user import get_request
from workflow.models import (ActivityUser)


class IatiAidType(models.Model):
    """
    IATI Aid Type Model
    """
    iati_aid_type_uuid = models.UUIDField('IATI Aid Type UUID', editable=False, default=uuid.uuid4, unique=True)
    aid_type = models.CharField('IATI Aid Type', max_length=100)
    code = models.CharField('IATI Aid Type Code', max_length=25)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='aid_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='aid_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('aid_type',)
        verbose_name_plural = 'IATI Aid Types'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiAidType, self).save(*args, **kwargs)

    def __str__(self):
        return self.aid_type or ''


class IatiFinanceType(models.Model):
    """
    IATI Finance Type Model
    """
    iati_finance_type_uuid = models.UUIDField('IATI Finance Type UUID', editable=False, default=uuid.uuid4, unique=True)
    finance_type = models.CharField('IATI Finance Type', max_length=100)
    code = models.CharField('IATI Finance Type Code', max_length=25)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='finance_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='finance_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('finance_type',)
        verbose_name_plural = 'IATI Finance Types'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiFinanceType, self).save(*args, **kwargs)

    def __str__(self):
        return self.finance_type or ''


class IatiCollaborationType(models.Model):
    """
    IATI Collaboration Type Model
    """
    iati_collaboration_type_uuid = models.UUIDField('IATI Collaboration Type UUID', editable=False, default=uuid.uuid4, unique=True)
    collaboration_type = models.CharField('IATI Collaboration Type', max_length=100)
    code = models.CharField('IATI Collaboration Type Code', max_length=25)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='collaboration_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='collaboration_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('collaboration_type',)
        verbose_name_plural = 'IATI Collaboration Types'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiCollaborationType, self).save(*args, **kwargs)

    def __str__(self):
        return self.finance_type or ''


class IatiCondition(models.Model):
    """
    IATI Condition Type Model
    """
    iati_finance_type_uuid = models.UUIDField('IATI Condition UUID', editable=False, default=uuid.uuid4, unique=True)
    condition = models.CharField('IATI Condition', max_length=100, blank=True,
                                 help_text='Specify terms and conditions attached to the activity that, if not met,'
                                           'may influence the delivery of commitments made by participating'
                                           ' organizations.')
    condition_type = models.CharField('IATI Condition Type', max_length=100)
    code = models.CharField('IATI Condition Type Code', max_length=25)
    condition_attached = models.BooleanField('IATI Condition Attached?', default=0)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='condition_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='condition_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('condition',)
        verbose_name_plural = 'IATI Condition Types'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiCondition, self).save(*args, **kwargs)

    def __str__(self):
        return self.condition_type or ''


class IatiFlowType(models.Model):
    """
    IATI Flow Type Model
    """
    iati_flow_type_uuid = models.UUIDField('IATI Flow Type UUID', editable=False, default=uuid.uuid4, unique=True)
    flow_type = models.CharField('IATI Flow Type', max_length=100)
    code = models.CharField('IATI Flow Type Code', max_length=25)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='flow_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='flow_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('flow_type',)
        verbose_name_plural = 'IATI Flow Types'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiFlowType, self).save(*args, **kwargs)

    def __str__(self):
        return self.flow_type or ''


class IatiHumanitarianScope(models.Model):
    """
    IATI Humanitarian Scope Model
    """
    iati_humanitarian_scope_uuid = models.UUIDField('IATI Humanitarian Scope UUID', editable=False, default=uuid.uuid4,
                                                    unique=True)
    humanitarian_scope = models.CharField('IATI Humanitarian Scope', max_length=100)
    code = models.CharField('IATI Humanitarian Scope Code', max_length=25)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='humanitarian_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='humanitarian_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('humanitarian_scope',)
        verbose_name_plural = 'IATI Humanitarian Scope'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiHumanitarianScope, self).save(*args, **kwargs)

    def __str__(self):
        return self.humanitarian_scope


class IatiProjectStatus(models.Model):
    """
    IATI Project Status Model
    """
    iati_project_status_uuid = models.UUIDField('IATI Project Status UUID', editable=False, default=uuid.uuid4,
                                                    unique=True)
    project_status = models.CharField('IATI Project Status', max_length=100)
    code = models.CharField('IATI Project Status Code', max_length=25)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='project_status_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='project_status_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('project_status',)
        verbose_name_plural = 'IATI Project Status'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiProjectStatus, self).save(*args, **kwargs)

    def __str__(self):
        return self.project_status


class IatiTiedStatus(models.Model):
    """
    IATI Tied Status Model
    """
    iati_tied_status_uuid = models.UUIDField('IATI Tied Status UUID', editable=False, default=uuid.uuid4,
                                                    unique=True)
    tied_status = models.CharField('IATI Tied Status', max_length=100)
    code = models.CharField('IATI Tied Status Code', max_length=25)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='tied_status_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='tied_status_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('tied_status',)
        verbose_name_plural = 'IATI Tied Status'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(IatiTiedStatus, self).save(*args, **kwargs)

    def __str__(self):
        return self.tied_status


class Iati(models.Model):
    """
    IAT information Model
    """
    iati_uuid = models.UUIDField('IATI UUID', editable=False, default=uuid.uuid4, unique=True)
    activity_identifier = models.CharField('IATI Activity Identifier', max_length=100)
    aid_type = models.ForeignKey(IatiAidType, verbose_name='IATI Aid Type', null=True, on_delete=models.SET_NULL)
    collaboration_type = models.ForeignKey(IatiCollaborationType, verbose_name='IATI Collaboration Type', null=True,
                                           on_delete=models.SET_NULL)
    condition = models.ForeignKey(IatiCondition, verbose_name='IATI Condition', null=True, on_delete=models.SET_NULL)

    finance_type = models.ForeignKey(IatiFinanceType, verbose_name='IATI Finance Type', null=True,
                                     on_delete=models.SET_NULL)
    flow_type = models.ForeignKey(IatiFlowType, verbose_name='IATI Flow Type', null=True, on_delete=models.SET_NULL)

    humanitarian_scope = models.ForeignKey(IatiHumanitarianScope, verbose_name='IATI Humanitarian Scope', null=True,
                                           on_delete=models.SET_NULL)
    project_status = models.ForeignKey(IatiProjectStatus, verbose_name='IATI Project Status', null=True,
                                       on_delete=models.SET_NULL)
    tied_status = models.ForeignKey(IatiTiedStatus, verbose_name='IATI Tied Status', null=True,
                                    on_delete=models.SET_NULL)
    ready_for_reporting = models.BooleanField('Ready for IATI reporting?', default=0)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='iati_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='iati_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('activity_identifier',)
        verbose_name_plural = 'IATI'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Iati, self).save(*args, **kwargs)

    def __str__(self):
        return self.activity_identifier


