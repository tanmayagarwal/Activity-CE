import uuid
import datetime

from django.db import models
from django.utils import timezone

from decimal import Decimal
from workflow.models import (Documentation, ActivityUser)

from activity.middlewares.get_current_user import get_request


class Workspace(models.Model):
    """
    Workspace is the top level model in the hierarchy for Activity
    """
    uuid = models.UUIDField(editable=False, verbose_name='Workspace UUID', default=uuid.uuid4, unique=True)
    name = models.CharField('Workspace Name', max_length=36)
    url = models.CharField('Workspace Url', max_length=100, blank=True)
    description = models.TextField('Workspace Description', max_length=765, blank=True)
    workflow_level_1 = models.CharField(max_length=36, default='Project')
    workflow_level_2 = models.CharField(max_length=36, default='Activity')
    workflow_level_3 = models.CharField(max_length=36, default='Sub-Activity')
    workflow_level_4 = models.CharField(max_length=36, default='Task')
    organization_label = models.CharField(max_length=36, default='Organization')
    indicator_label = models.CharField(max_length=36, default='Indicator')
    form_label = models.CharField(max_length=36, default='Forms')
    site_label = models.CharField(max_length=36, default='Sites')
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='workspace_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='workspace_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Workspaces'

    # displayed in admin templates
    def __str__(self):
        return self.name or ''

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user

        self.edit_date = timezone.now()
        self.modified_by = logged_user
        return super(Workspace, self).save(*args, **kwargs)


class OrganizationType(models.Model):
    """
    Organization Type Model
    """
    type_uuid = models.UUIDField('Organization Type UUID', editable=False, default=uuid.uuid4, unique=True)
    type = models.CharField('Organization Type', max_length=100, unique=True)
    create_date = models.DateTimeField('Create Date', blank=True, null=True)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='org_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='org_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Workflow Level1 Types'

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
        return super(OrganizationType, self).save(*args, **kwargs)


class OrganizationSubType(models.Model):
    """
    Organization Sub-Type Model
    """
    sub_type_uuid = models.UUIDField('Organization Sub-Type UUID', editable=False, default=uuid.uuid4, unique=True)
    sub_type = models.CharField('Organization Sub-Type', max_length=100, unique=True)
    type = models.ForeignKey(OrganizationType, verbose_name='Organization Type', null=True,
                             on_delete=models.SET_NULL)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='org_sub_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='org_sub_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Workflow Level1 Sub Types'

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
        return super(OrganizationSubType, self).save(*args, **kwargs)


class Organization(models.Model):
    """
    Organization Model
    """
    # define status choices
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )

    full_name = models.CharField('Full Organization Name',  max_length=135, blank=True, default='First Organization')
    short_name = models.CharField('Organization Short Name', max_length=100)
    url = models.CharField('Organization Website url', max_length=165, blank=True)
    description = models.TextField('Description/Notes', max_length=765, null=True, blank=True)
    organization_type = models.ForeignKey(OrganizationType, null=True,  on_delete=models.SET_NULL)
    parent_organization = models.ForeignKey('self', null=True, related_name='children', on_delete=models.SET_NULL)
    documentation = models.ForeignKey(Documentation, null=True, on_delete=models.SET_NULL)
    link_to_description_relationship = models.CharField('Link to Description of Relationship', blank=True,
                                                        max_length=165)
    link_to_due_diligence = models.CharField('Link to Due Diligence', blank=True, max_length=165)
    singular_label = models.CharField('Organization Singular Label',  max_length=135, blank=True,
                                      default='Organization')
    plural_label = models.CharField('Organization Plural Label', max_length=135, blank=True, default='Organizations')
    organization_identifier = models.CharField('Organization Identifier', max_length=100, blank=True)
    organization_status = models.CharField('Organization Status', max_length=100, choices=STATUS_CHOICES)
    create_date = models.DateTimeField('Create Date', null=True, blank=True)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', related_name='org_created_by',
                                   editable=False, null=True, on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', related_name='org_modified_by',
                                    editable=False, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('full_name',)
        verbose_name_plural = "Organizations"
        app_label = 'activity'

    # displayed in admin templates
    def __str__(self):
        return self.name or ''

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Organization, self).save(*args, **kwargs)


class Office(models.Model):
    """
    Office Model
    """
    name = models.CharField('Office Name', max_length=255, blank=True)
    code = models.CharField('Office Code', max_length=255, blank=True)
    create_date = models.DateTimeField('Create Date', null=True, blank=True)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', related_name='office_created_by',
                                   editable=False, null=True, on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', related_name='office_modified_by',
                                    editable=False, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if self.create_date is None:
            self.create_date = datetime.now()
            self.created_by = logged_user
        self.edit_date = datetime.now()
        self.modified_by = logged_user
        super(Office, self).save(*args, **kwargs)

    # displayed in admin templates
    def __str__(self):
        new_name = self.name + " - " + self.code
        return new_name


class Sector1(models.Model):
    """
    Sector Model
    """
    sector = models.CharField('Sector Name', max_length=255)
    parent_sector = models.ForeignKey('self', blank=True, null=True, related_name='sub_sectors',
                                      on_delete=models.SET_NULL)
    create_date = models.DateTimeField('Create Date', null=True, blank=True)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='sector_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='sector_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('sector',)
        verbose_name_plural = 'Location'
        app_label = 'workflow'

    # displayed in admin templates
    def __str__(self):
        return self.sector or ''

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Sector1, self).save(*args, **kwargs)


class Contact(models.Model):
    """
    Contact Model
    """
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    singular_label = models.CharField('Singular Label', max_length=100, default='Contact')
    plural_label = models.CharField('Plural Label', max_length=100, default='Contacts')
    email = models.CharField('Email Address', max_length=100, blank=True, null=True)
    phone = models.CharField('Phone Number', max_length=25, blank=True, null=True)
    street = models.CharField('City', max_length=100, blank=True)
    city = models.CharField('City', max_length=100, blank=True)
    zip_code = models.CharField('Zip/Postal Code', max_length=25, blank=True)
    state = models.CharField('State/Province', max_length=100, blank=True)
    country = models.CharField('Country', max_length=100, blank=True)
    organization = models.ForeignKey(Organization, verbose_name='Organization Contact',
                                     on_delete=models.CASCADE)
    create_date = models.DateTimeField('Create Date', null=True, blank=True)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='contact_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='contact_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('first_name',)
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def full_address(self):
        # html string
        return '{} <br> {} {} {} <br> {}'.\
            format(self.street, self.city, self.zip_code, self.state, self.country)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Contact, self).save(*args, **kwargs)


class LocationType(models.Model):
    """
    Location Type Model
    """
    location_type_uuid = models.UUIDField('Organization Sub-Type UUID', editable=False, default=uuid.uuid4, unique=True)
    type = models.CharField('Location Type', max_length=100, unique=True)
    create_date = models.DateTimeField('Create Date', blank=True, null=True, editable=False)
    modified_date = models.DateTimeField('Edit Date', blank=True, null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='location_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='location_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Location Types'

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
        return super(LocationType, self).save(*args, **kwargs)


class AdministrativeLevel(models.Model):
    """
    Administrative IndicatorLevel Model
    """
    level_1 = models.CharField('Administrative IndicatorLevel 1', max_length=100, blank=True)
    level_2 = models.CharField('Administrative IndicatorLevel 2', max_length=100, blank=True)
    level_3 = models.CharField('Administrative IndicatorLevel 3', max_length=100, blank=True)
    level_4 = models.CharField('Administrative IndicatorLevel 4', max_length=100, blank=True)
    create_date = models.DateTimeField('Create Date', null=True, blank=True)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created by', editable=False, null=True,
                                   related_name='admin_level_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='admin_level_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('level_1',)
        verbose_name_plural = 'Administrative Levels'

    # displayed in admin templates
    def __str__(self):
        return self.level_1 or ''

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(AdministrativeLevel, self).save(*args, **kwargs)


class Country(models.Model):
    """
    Country Model
    """
    country = models.CharField('Country Name', max_length=255, blank=True)
    workspace = models.ForeignKey(Workspace, blank=True, null=True, on_delete=models.SET_NULL)
    code = models.CharField('2 Letter Country Code', max_length=4, blank=True)
    description = models.TextField('Description/Notes', max_length=765, blank=True)
    latitude = models.CharField('Latitude', max_length=255, null=True, blank=True)
    longitude = models.CharField('Longitude', max_length=255, null=True, blank=True)
    zoom = models.IntegerField('Zoom', default=5)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('country',)
        verbose_name_plural = 'Countries'

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Country, self).save(*args, **kwargs)

    # displayed in admin templates
    def __str__(self):
        return self.country or ''


class Location(models.Model):
    """
    Location (Site) Model
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )
    location_uuid = models.UUIDField('Location UUID', editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField('Site Name', max_length=100, blank=True)
    parent_location = models.ForeignKey('self', null=True, related_name='sub_locations', on_delete=models.SET_NULL)
    contact = models.ForeignKey(Contact, null=True, verbose_name='Location Contact', on_delete=models.SET_NULL)
    status = models.CharField('Location Status', blank=True, max_length=100, choices=STATUS_CHOICES, default='active')
    country = models.ForeignKey(Country, verbose_name='Country of Location', on_delete=models.CASCADE)
    office = models.ForeignKey(Office, null=True, verbose_name='Location Office', on_delete=models.SET_NULL)
    type = models.ForeignKey(LocationType, null=True, verbose_name='Location Type', on_delete=models.SET_NULL)
    admin_levels = models.ForeignKey(AdministrativeLevel, verbose_name='Administrative Levels', null=True,
                                     on_delete=models.SET_NULL)
    latitude = models.DecimalField('Latitude Coordinates', decimal_places=16, max_digits=25, default=Decimal('0.00'))
    longitude = models.DecimalField('Longitude Coordinates', decimal_places=16, max_digits=25, default=Decimal('0.00'))
    create_date = models.DateTimeField('Create Date', null=True, blank=True)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created by', editable=False, null=True,
                                   related_name='location_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='location_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Sites'

    # displayed in admin templates
    def __str__(self):
        return self.name or ''

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Location, self).save(*args, **kwargs)


class Portfolio(models.Model):
    """
    Portfolio Model
    This acts like a folder for user data
    """
    portfolio_uuid = models.UUIDField('Portfolio UUID', editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField('Portfolio Name', max_length=100, unique=True)
    workspace = models.ForeignKey(Workspace, null=False, on_delete=models.CASCADE)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='portfolio_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='portfolio_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Portfolios'

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
        return super(Portfolio, self).save(*args, **kwargs)


class Currency(models.Model):
    """
    Currency Model
    """
    currency_uuid = models.UUIDField('Currency UUID', editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField('Currency Name', max_length=255)
    symbol = models.CharField('Currency Symbol', max_length=10, blank=True)
    code = models.CharField('Currency Code', max_length=20, blank=True)
    create_date = models.DateTimeField('Create Date', null=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, editable=False)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created Vy', editable=False, null=True,
                                   related_name='currency_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='currency_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Currencies'

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Currency, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


