from __future__ import unicode_literals

import json
from urllib.request import urlopen
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from decimal import Decimal
from datetime import datetime
import uuid

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords
from django.contrib.sessions.models import Session

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone
from django.db.models import Q
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from activity.middlewares.get_current_user import get_request


# New user created generate a token
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class ActivitySites(models.Model):
    name = models.CharField(blank=True, null=True, max_length=255)
    agency_name = models.CharField(blank=True, null=True, max_length=255)
    agency_url = models.CharField(blank=True, null=True, max_length=255)
    activity_report_url = models.CharField(blank=True, null=True,
                                           max_length=255)
    activity_tables_url = models.CharField(blank=True, null=True,
                                           max_length=255)
    activity_tables_user = models.CharField(blank=True, null=True,
                                            max_length=255)
    activity_tables_token = models.CharField(blank=True, null=True,
                                             max_length=255)
    # TODO : Verify if on_delete parameter with Cascade deletion is compatible
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    privacy_disclaimer = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now=False, blank=True, null=True)
    updated = models.DateTimeField(auto_now=False, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Activity Sites"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ On save, update timestamps as appropriate """
        if kwargs.pop('new_entry', True):
            self.created = datetime.now()
        else:
            self.updated = datetime.now()
        return super(ActivitySites, self).save(*args, **kwargs)


class ActivitySitesAdmin(admin.ModelAdmin):
    list_display = ('name', 'agency_name')
    display = 'Activity Site'
    list_filter = ('name',)
    search_fields = ('name', 'agency_name')


class Currency(models.Model):
    name = models.CharField("Currency Name", max_length=255)
    symbol = models.CharField("Currency Symbol", max_length=10, blank=True)
    code = models.CharField("Currency Code", max_length=20, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Currencies"

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Currency, self).save()

    def __unicode__(self):
        return self.name


IMAGE_SPEC = {
    "width": 2000,
    "height": 500,
    "limit_kb": 100
}


def validate_image(image, width=IMAGE_SPEC['width'],
                   height=IMAGE_SPEC['height'],
                   limit_kb=IMAGE_SPEC['limit_kb']):
    file_size = image.file.size
    if file_size > limit_kb * 1024:
        raise ValidationError("Max size of file is %s KB" % limit_kb)
    w, h = get_image_dimensions(image)
    if w < width:
        raise ValidationError("Min width is %s" % width)
    if h < height:
        raise ValidationError("Min height is %s" % height)


class Organization(models.Model):
    name = models.CharField("Organization Name",
                            max_length=255, blank=True, default="Hikaya")
    description = models.TextField(
        "Description/Notes", max_length=765, null=True, blank=True)
    logo = models.FileField("Your Organization Logo",
                            blank=True, null=True, upload_to="media/img/")
    organization_url = models.CharField(blank=True, null=True, max_length=255)
    level_1_label = models.CharField(
        "Project/WorkflowLevel1 Organization Level 1 label", default="WorkflowLevel1",
        max_length=255, blank=True)
    level_2_label = models.CharField(
        "Project/WorkflowLevel1 Organization Level 2 label", default="Project",
        max_length=255, blank=True)
    level_3_label = models.CharField(
        "Project/WorkflowLevel1 Organization Level 3 label", default="Component",
        max_length=255, blank=True)
    level_4_label = models.CharField(
        "Project/WorkflowLevel1 Organization Level 4 label", default="Activity",
        max_length=255, blank=True)
    site_label = models.CharField('Site Organization label', default='Site',
                                  max_length=255)
    stakeholder_label = models.CharField('Stakeholder Organization label',
                                         default='Stakeholder',
                                         max_length=255)
    form_label = models.CharField('Form Organization label', default='Form',
                                  max_length=255)
    indicator_label = models.CharField('Indicator Organization label',
                                       default='Indicator',
                                       max_length=255)
    site_label = models.CharField('Site Organization label', default='Site',
                                  max_length=255)
    theme_color = models.CharField('Organization theme color',
                                   default='#25ced1', max_length=50)
    default_currency = models.ForeignKey(Currency,
                                         help_text='Organization currency',
                                         blank=True, null=True,
                                         on_delete=models.SET_NULL)
    default_language = models.CharField('Organization language',
                                        default='English-US', max_length=50)
    date_format = models.CharField('Organization Date Format',
                                   default='DD.MM.YYYY', max_length=100)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    theme_color = models.CharField(
        "Organization Costum Color", default="25ced1", validators=[
            RegexValidator(regex='^.{6}$', message='Length has to be 6',
                           code='nomatch')],
        max_length=6)
    logo = models.ImageField(
        "Your Organization logo",
        upload_to='images/', blank=True,
        validators=[validate_image],
        help_text="Image of minimum {} width and {} height, "
                  "maximum of {} ko".format(*tuple(IMAGE_SPEC.values())))

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Organizations"
        app_label = 'workflow'

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Organization, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name or ''


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Organization'


TITLE_CHOICES = (
    ('mr', 'Mr.'),
    ('mrs', 'Mrs.'),
    ('ms', 'Ms.'),
)


class ActivityUser(models.Model):
    title = models.CharField(blank=True, null=True,
                             max_length=3, choices=TITLE_CHOICES)
    name = models.CharField("Given Name", blank=True,
                            null=True, max_length=100)
    employee_number = models.IntegerField(
        "Employee Number", blank=True, null=True)
    user = models.OneToOneField(
        User, unique=True, related_name='activity_user',
        on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, default=1, blank=True, null=True,
        on_delete=models.SET_NULL)
    country = models.ForeignKey(
        'activity.Country', blank=True, null=True, on_delete=models.SET_NULL)
    organizations = models.ManyToManyField(Organization, verbose_name='Accessible Organizations',
                                           related_name='organization', blank=True)
    tables_api_token = models.CharField(blank=True, null=True, max_length=255)
    activity_api_token = models.CharField(
        blank=True, null=True, max_length=255)
    privacy_disclaimer_accepted = models.BooleanField(default=False)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name or ''

    @property
    def organizations_list(self):
        return ', '.join([x.name for x in self.organizations.all()])

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(ActivityUser, self).save()


class ActivityBookmarks(models.Model):
    user = models.ForeignKey(
        ActivityUser, related_name='activitybookmark',
        on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=255)
    bookmark_url = models.CharField(blank=True, null=True, max_length=255)
    program = models.ForeignKey(
        "WorkflowLevel1", blank=True, null=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(ActivityBookmarks, self).save()


class ActivityBookmarksAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')
    display = 'Activity User Bookmarks'
    list_filter = ('user__name',)
    search_fields = ('name', 'user')


class ActivityUserProxy(ActivityUser):
    class Meta:
        verbose_name, verbose_name_plural = u"Report Activity User", \
                                            u"Report Activity Users"
        proxy = True


class ActivityUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    display = 'Activity User'
    list_filter = ('country', 'user__is_staff',)
    search_fields = ('name', 'country__country', 'title')


# Form Guidance
class FormGuidance(models.Model):
    form = models.CharField(max_length=135, null=True, blank=True)
    guidance_link = models.URLField(max_length=200, null=True, blank=True)
    guidance = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('create_date',)

    def save(self):
        if self.create_date is None:
            self.create_date = datetime.now()
        super(FormGuidance, self).save()

    def __str__(self):
        return self.form


class FormGuidanceAdmin(admin.ModelAdmin):
    list_display = ('form', 'guidance', 'guidance_link', 'create_date',)
    display = 'Form Guidance'


class Sector(models.Model):
    sector = models.CharField("Sector Name", max_length=255, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('sector',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Sector, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.sector or ''


class SectorAdmin(admin.ModelAdmin):
    list_display = ('sector', 'create_date', 'edit_date')
    display = 'Sector'


class Contact(models.Model):
    name = models.CharField("Name", max_length=255, blank=True, null=True)
    title = models.CharField("Title", max_length=255, blank=True, null=True)
    city = models.CharField("City/Town", max_length=255, blank=True, null=True)
    address = models.TextField(
        "Address", max_length=255, blank=True, null=True)
    email = models.CharField("Email", max_length=255, blank=True, null=True)
    phone = models.CharField("Phone", max_length=255, blank=True, null=True)
    country = models.ForeignKey(
        Country, blank=True, null=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name', 'country', 'title')
        verbose_name_plural = "Contact"

    # onsave add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Contact, self).save()

    # displayed in admin templates
    def __str__(self):
        return u'%s, %s' % (self.name, self.title)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'create_date', 'edit_date')
    display = 'Contact'
    list_filter = ('create_date', 'country')
    search_fields = ('name', 'country', 'title', 'city')


# For programs that have custom dashboards. The default dashboard for all
# other programs is 'WorkflowLevel1 Dashboard'
class FundCode(models.Model):
    name = models.CharField("Fund Code", max_length=255, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(FundCode, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name


class FundCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'program__name', 'create_date', 'edit_date')
    display = 'Fund Code'


class ApprovalAuthority(models.Model):
    approval_user = models.ForeignKey(ActivityUser,
                                      help_text='User with Approval Authority',
                                      blank=True, null=True,
                                      related_name="auth_approving",
                                      on_delete=models.SET_NULL)
    budget_limit = models.IntegerField(null=True, blank=True)
    fund = models.CharField("Fund", max_length=255, null=True, blank=True)
    country = models.ForeignKey(
        "Country", null=True, blank=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('approval_user',)
        verbose_name_plural = "Activity Approval Authority"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(ApprovalAuthority, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.approval_user.user.first_name + " " + \
               self.approval_user.user.last_name


class Province(models.Model):
    name = models.CharField("Admin Level 1", max_length=255, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = "Admin Level 1"
        verbose_name_plural = "Admin Level 1"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Province, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name


class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'create_date')
    search_fields = ('name', 'country__country')
    list_filter = ('create_date', 'country')
    display = 'Admin Level 1'


class District(models.Model):
    name = models.CharField("Admin Level 2", max_length=255, blank=True)
    province = models.ForeignKey(
        Province, verbose_name="Admin Level 1", on_delete=models.CASCADE)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = "Admin Level 2"
        verbose_name_plural = "Admin Level 2"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(District, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'create_date')
    search_fields = ('create_date', 'province')
    list_filter = ('province__country__country', 'province')
    display = 'Admin Level 2'


class AdminLevelThree(models.Model):
    name = models.CharField("Admin Level 3", max_length=255, blank=True)
    district = models.ForeignKey(
        District, verbose_name="Admin Level 2", blank=True, null=True,
        on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = "Admin Level 3"
        verbose_name_plural = "Admin Level 3"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(AdminLevelThree, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name


class AdminLevelThreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'create_date')
    search_fields = ('name', 'district__name')
    list_filter = ('district__province__country__country', 'district')
    display = 'Admin Level 3'


class Village(models.Model):
    name = models.CharField("Admin Level 4", max_length=255, blank=True)
    district = models.ForeignKey(
        District, null=True, blank=True, on_delete=models.SET_NULL)
    admin_3 = models.ForeignKey(AdminLevelThree, verbose_name="Admin Level 3",
                                null=True, blank=True,
                                on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = "Admin Level 4"
        verbose_name_plural = "Admin Level 4"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Village, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name


class VillageAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'create_date', 'edit_date')
    list_filter = ('district__province__country__country', 'district')
    display = 'Admin Level 4'


class Office(models.Model):
    name = models.CharField("Office Name", max_length=255, blank=True)
    code = models.CharField("Office Code", max_length=255, blank=True)
    province = models.ForeignKey(
        Province, verbose_name="Admin Level 1", on_delete=models.CASCADE)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Office, self).save()

    # displayed in admin templates
    def __str__(self):
        new_name = self.name + " - " + self.code
        return new_name


class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'province', 'create_date', 'edit_date')
    search_fields = ('name', 'province__name', 'code')
    list_filter = ('create_date', 'province__country__country')
    display = 'Office'


class ProfileType(models.Model):
    profile = models.CharField("Profile Type", max_length=255, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('profile',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(ProfileType, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.profile


class ProfileTypeAdmin(admin.ModelAdmin):
    list_display = ('profile', 'create_date', 'edit_date')
    display = 'ProfileType'


# Add land classification - 'Rural', 'Urban', 'Peri-Urban', activity-help
# issue #162
class LandType(models.Model):
    classify_land = models.CharField(
        "Land Classification", help_text="Rural, Urban, Peri-Urban",
        max_length=100, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('classify_land',)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(LandType, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.classify_land


class LandTypeAdmin(admin.ModelAdmin):
    list_display = ('classify_land', 'create_date', 'edit_date')
    display = 'Land Type'


class SiteProfileManager(models.Manager):
    def get_queryset(self):
        return super(SiteProfileManager,
                     self).get_queryset().prefetch_related() \
            .select_related('country', 'province', 'district',
                            'admin_level_three', 'type')


class SiteProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'office', 'country', 'district',
                    'province', 'village', 'cluster', 'longitude', 'latitude',
                    'create_date', 'edit_date')
    list_filter = 'country__country'
    search_fields = ('code', 'office__code', 'country__country')
    display = 'Location'


class Capacity(models.Model):
    capacity = models.CharField(
        "Capacity", max_length=255, blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('capacity',)
        verbose_name_plural = "Capacity"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Capacity, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.capacity


class CapacityAdmin(admin.ModelAdmin):
    list_display = ('capacity', 'create_date', 'edit_date')
    display = 'Capacity'


class StakeholderType(models.Model):
    name = models.CharField(
        "Stakeholder Type", max_length=255, blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Stakeholder Types"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(StakeholderType, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name


class StakeholderTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Stakeholder Types'
    list_filter = 'create_date'
    search_fields = 'name'


class Evaluate(models.Model):
    evaluate = models.CharField(
        "How will you evaluate the outcome or impact of the project?",
        max_length=255, blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('evaluate',)
        verbose_name_plural = "Evaluate"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Evaluate, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.evaluate


class EvaluateAdmin(admin.ModelAdmin):
    list_display = ('evaluate', 'create_date', 'edit_date')
    display = 'Evaluate'


class ProjectType(models.Model):
    name = models.CharField("Type of Activity", max_length=135)
    description = models.CharField(max_length=765)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(ProjectType, self).save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Template(models.Model):
    name = models.CharField("Name of Document", max_length=135)
    documentation_type = models.CharField("Type (File or URL)", max_length=135)
    description = models.CharField(max_length=765)
    file_field = models.FileField(upload_to="uploads", blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Template, self).save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'documentation_type',
                    'file_field', 'create_date', 'edit_date')
    display = 'Template'


class StakeholderManager(models.Manager):
    def get_queryset(self):
        return super(StakeholderManager, self).get_queryset().prefetch_related(
            'contact', 'sectors').select_related('country', 'type',
                                                 'formal_relationship_document',
                                                 'vetting_document')


class Stakeholder(models.Model):
    name = models.CharField("Stakeholder/Organization Name",
                            max_length=255, blank=True, null=True)
    type = models.ForeignKey(StakeholderType, blank=True,
                             null=True, on_delete=models.SET_NULL)
    contact = models.ManyToManyField(Contact, max_length=255, blank=True)
    country = models.ForeignKey(
        'activity.Country', blank=True, null=True, on_delete=models.SET_NULL)
    # sector = models.ForeignKey(Sector, blank=True, null=True,
    # related_name='sects')
    sectors = models.ManyToManyField(Sector, blank=True)
    stakeholder_register = models.BooleanField(
        "Has this partner been added to stakeholder register?")
    formal_relationship_document = models.ForeignKey(
        'Documentation',
        verbose_name="Formal Written Description of Relationship",
        null=True, blank=True,
        related_name="relationship_document",
        on_delete=models.SET_NULL)
    vetting_document = models.ForeignKey(
        'Documentation',
        verbose_name="Vetting/ due diligence statement",
        null=True, blank=True, related_name="vetting_document",
        on_delete=models.SET_NULL)
    approval = models.CharField(
        "Approval", default="in progress", max_length=255, blank=True,
        null=True)
    approved_by = models.ForeignKey(ActivityUser, help_text='', blank=True,
                                    null=True,
                                    related_name="stake_approving",
                                    on_delete=models.SET_NULL)
    filled_by = models.ForeignKey(ActivityUser, help_text='', blank=True,
                                  null=True,
                                  related_name="stake_filled",
                                  on_delete=models.SET_NULL)
    notes = models.TextField(max_length=765, blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    # optimize query
    objects = StakeholderManager()

    class Meta:
        ordering = ('country', 'name', 'type')
        verbose_name_plural = "Stakeholders"

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Stakeholder, self).save()

    # displayed in admin templates
    def __str__(self):
        return self.name


class StakeholderAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'country', 'create_date')
    display = 'Stakeholders'
    list_filter = ('country', 'type', 'sector')


class LoggedUser(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    country = models.CharField(max_length=100, blank=False)
    email = models.CharField(max_length=100, blank=False,
                             default='user@mercycorps.com')

    def __str__(self):
        return self.username

    def login_user(sender, request, user, **kwargs):
        country = get_user_country(request)
        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())

        user_id_list = []
        logged_user_id = request.user.id

        try:
            for session in active_sessions:
                data = session.get_decoded()

                user_id_list.append(data.get('_auth_user_id', None))

                if logged_user_id in user_id_list:
                    LoggedUser(username=user.username,
                               country=country, email=user.email).save()

                if data.get('google-oauth2_state'):
                    LoggedUser(username=user.username,
                               country=country, email=user.email).save()

        except Exception as e:
            pass

    def logout_user(sender, request, user, **kwargs):

        try:
            user = LoggedUser.objects.get(pk=user.username)
            user.delete()

        except LoggedUser.DoesNotExist:
            pass

    user_logged_in.connect(login_user)
    user_logged_out.connect(logout_user)


def get_user_country(request):
    # Automatically geolocate the connecting IP
    ip = request.META.get('REMOTE_ADDR')
    try:
        response = urlopen('http://ipinfo.io/' + ip + '/json').read()
        response = json.loads(response)
        return response['country'].lower()

    except Exception as e:
        response = "undefined"
        return response


# NEW MODELS
class WorkflowLevel1Type(models.Model):
    """
    Workflow Level 1 Type Model
    These are Workflow Level 1 categories
    """
    type_uuid = models.UUIDField('Workflow Level 1 Type UUID', editable=False, default=uuid.uuid4, unique=True)
    type = models.CharField('Workflow Level 1 Type', max_length=100, unique=True)
    create_date = models.DateTimeField('Create Date', blank=True, null=True)
    modified_date = models.DateTimeField('Modified Date', blank=True, null=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Workflow Level1 Types'

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
        return super(WorkflowLevel1Type, self).save(*args, **kwargs)


class FundingStatus(models.Model):
    """
    Funding Status Model
    Tracking Workflow Level 1 funding status
    """
    funding_status_uuid = models.UUIDField('Funding Status UUID', editable=False, default=uuid.uuid4(), unique=True)
    status = models.CharField('Funding Status', max_length=165)
    create_date = models.DateTimeField('Create Date', blank=True, null=True)
    modified_date = models.DateTimeField('Modified Date', blank=True, null=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='fund_status_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='fund_status_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Funding Statuses'

    def __str__(self):
        return self.status or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(FundingStatus, self).save(*args, **kwargs)


class Approval(models.Model):
    """
    Approval Model
    """
    approval_uuid = models.UUIDField('Approval UUID', editable=False, default=uuid.uuid4(), unique=True)
    name = models.CharField('Approval Name', max_length=165)
    description = models.TextField('Approval Description', blank=True, max_length=765)
    create_date = models.DateTimeField('Create Date', null=True, blank=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='approval_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='approval_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Approvals'

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
        return super(Approval, self).save(*args, **kwargs)


class WorkflowStatus(models.Model):
    """
    Workflow Status Model
    TODO - create migrations to add the default values
    (Open, Awaiting approval, Tracking, Closed, Rejected)
    """
    status_uuid = models.UUIDField('Workflow Status UUID', editable=False, default=uuid.uuid4, unique=True)
    status = models.CharField('Workflow Status', max_length=100)
    create_date = models.DateTimeField('Create Date', null=True, blank=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='wfl_status_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='wfl_status_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Workflow Statuses'

    def __str__(self):
        return self.status or ''

    def save(self, *args, **kwargs):
        # get logged user
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(WorkflowStatus, self).save(*args, **kwargs)


class WorkflowLevel1(models.Model):
    """
    Workflow Level 1 model (top level workflow model)
    """
    workflow_level1_uuid = models.UUIDField('Workflow Level 1 UUID', editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField('Workflow Level 1 Name', max_length=255, blank=False)
    workflow_level1_code = models.CharField('Workflow Level 1 Code', max_length=100, blank=True)
    description = models.TextField('Workflow Level 1 Description', max_length=765, blank=True)
    start_date = models.DateTimeField('Start Date', null=True, blank=True)
    end_date = models.DateTimeField('End Date', null=True, blank=True)
    workflow_level1_type = models.ForeignKey(WorkflowLevel1Type, verbose_name='Workflow Level 1 Type', null=True,
                                             on_delete=models.SET_NULL)
    workflow_status = models.ForeignKey(WorkflowStatus, max_length=100, verbose_name='Workflow Status', null=True,
                                        on_delete=models.SET_NULL)
    sector = models.ManyToManyField(Sector, blank=True, help_text='Workflow Level 1 sectors')
    workspace = models.ForeignKey('activity.Workspace', on_delete=models.CASCADE)
    organization = models.ForeignKey('activity.Organization', on_delete=models.CASCADE)
    portfolio = models.ForeignKey('activity.Portfolio', on_delete=models.CASCADE)
    funding_status = models.ForeignKey(FundingStatus, verbose_name='Funding Status', null=True,
                                       on_delete=models.SET_NULL)
    iati = models.ForeignKey('externalconfigs.Iati', verbose_name='IATI', null=True, on_delete=models.SET_NULL)
    history = HistoricalRecords()
    create_date = models.DateTimeField('Create Date', null=True, blank=True, editable=False)
    edit_date = models.DateTimeField('Edit Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='wfl1_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='wfl1_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Workflow Level 1s'

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
        return super(WorkflowLevel1, self).save(*args, **kwargs)


class WorkflowLevel2Type(models.Model):
    """
    Workflow Level 2 Type Model
    These are Workflow Level 2 categories
    """
    type_uuid = models.UUIDField('Workflow Level 2 Type UUID', editable=False, default=uuid.uuid4, unique=True)
    type = models.CharField('Workflow Level 2 Type', max_length=100, unique=True)
    create_date = models.DateTimeField('Create Date', blank=True, null=True)
    modified_date = models.DateTimeField('Modified Date', blank=True, null=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='level2_type_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='level2_type_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Workflow Level2 Types'

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
        return super(WorkflowLevel2Type, self).save(*args, **kwargs)


class WorkflowLevel2Manager(models.Manager):
    def get_approved(self):
        return self.filter(approval="approved")

    def get_open(self):
        return self.filter(approval="")

    def get_inprogress(self):
        return self.filter(approval="in progress")

    def get_awaiting_approval(self):
        return self.filter(approval="awaiting approval")

    def get_rejected(self):
        return self.filter(approval="rejected")

    def get_new(self):
        return self.filter(Q(approval=None) | Q(approval=""))

    def get_queryset(self):
        return super(WorkflowLevel2Manager,
                     self).get_queryset().select_related(
            'office',
            'approved_by',
            'approval_submitted_by')


class WorkflowLevel2(models.Model):
    """
    workflow Level2 or 3 or 4 model
    Workflow Level3s have self relationship with WFL2s
    """
    workflow_level2_uuid = models.UUIDField('Workflow Level 2/3 UUID', editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField('Workflow Level 2/3 Name', max_length=255)
    description = models.TextField('Workflow Level 2/3 Description', max_length=765, blank=True)
    workflow_level2_code = models.CharField('Workflow Level2 Code', blank=True, max_length=100)
    start_date = models.DateTimeField('Start Date', null=True, blank=True)
    end_date = models.DateTimeField('End Date', null=True, blank=True)
    workflow_status = models.ForeignKey(WorkflowStatus, max_length=100, verbose_name='Workflow Status', null=True,
                                        on_delete=models.SET_NULL)
    workflow_level1 = models.ForeignKey(WorkflowLevel1, null=False, on_delete=models.CASCADE)
    workflow_level2_type = models.ForeignKey(WorkflowLevel2Type, verbose_name='Workflow Level 2 Type', null=True,
                                             on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', null=True, related_name='workflow_level3s', on_delete=models.SET_NULL)
    office_location = models.ForeignKey(Office, null=True, verbose_name='Office Location Tag',
                                        on_delete=models.SET_NULL)
    implementation_location = models.ForeignKey('activity.Location', verbose_name='Implementation Location Tag',
                                                null=True, on_delete=models.SET_NULL)
    staff_responsible = models.ForeignKey('activity.Contact', verbose_name='Staff Responsible', null=True,
                                          on_delete=models.SET_NULL)
    workflow_sector = models.ManyToManyField(Sector, verbose_name='Workflow Sector Tag',
                                             related_name='workflow_sectors')
    history = HistoricalRecords()
    create_date = models.DateTimeField('Create Date', null=True, blank=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='wfl2_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='wfl2_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Workflow Level 2/3s'

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
        return super(WorkflowLevel2, self).save(*args, **kwargs)


class WorkflowLevel2Plan(models.Model):
    """
    Workflow Level2 Plan Model
    A Junction Table for workflow Level1 and Level2
    """
    workflow_level2_plan_uuid = models.UUIDField('Workflow Level2 Plan UUID', editable=False, default=uuid.uuid4,
                                                 unique=True)
    name = models.CharField('Workflow Level2 Plan  Name', max_length=150)
    description = models.TextField('Workflow Level2 Plan Description', max_length=765, blank=True)
    workflow_level1 = models.ForeignKey(WorkflowLevel1, verbose_name='Workflow Level 1',
                                        on_delete=models.CASCADE)
    workflow_level2 = models.ForeignKey(WorkflowLevel2, verbose_name='Workflow Level 2', null=True,
                                        on_delete=models.SET_NULL)
    history = HistoricalRecords()
    create_date = models.DateTimeField('Create Date', null=True, blank=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='wfl2_plan_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='wfl2_plan_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Workflow Level2 Plans'

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
        return super(WorkflowLevel2Plan, self).save(*args, **kwargs)


class Documentation(models.Model):
    """
    Documentation Model
    """
    name = models.CharField(
        'Name of Document', max_length=135, blank=True, null=True)
    url = models.CharField(
        'URL (Link to document or document repository)', blank=True, null=True,
        max_length=135)
    description = models.CharField(max_length=255, blank=True, null=True)
    template = models.ForeignKey(
        Template, blank=True, null=True, on_delete=models.SET_NULL)
    file_field = models.FileField(upload_to='uploads', blank=True, null=True)
    project = models.ForeignKey(
        WorkflowLevel2, blank=True, null=True, on_delete=models.SET_NULL)
    program = models.ForeignKey(
        WorkflowLevel1, blank=True, null=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    # on save add create date or update edit date
    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = datetime.now()
        self.edit_date = datetime.now()
        super(Documentation, self).save()

    def __str__(self):
        return self.name

    @property
    def name_n_url(self):
        return "%s %s" % (self.name, self.url)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Documentation"


class Budget(models.Model):
    """
    Budget Model
    """
    name = models.CharField(max_length=135, blank=True)
    contributor = models.ForeignKey('activity.Organization', verbose_name='Contributing Organization', null=True,
                                    on_delete=models.SET_NULL)
    description_of_contribution = models.TextField(max_length=765, blank=True)
    workflow_level2 = models.ForeignKey(WorkflowLevel2, null=True, verbose_name="Workflow Level 2",
                                        on_delete=models.SET_NULL)
    estimated_budget = models.DecimalField('Estimated Budget', decimal_places=4, max_digits=16,
                                           default=Decimal('0.0000'))
    actual_budget_donor_currency = models.DecimalField('Actual Budget Donor Currency', decimal_places=4, max_digits=16,
                                                       default=Decimal('0.0000'))
    actual_expenditure_donor_currency = models.DecimalField('Actual Expenditure Donor Currency', decimal_places=4,
                                                            max_digits=16, default=Decimal('0.0000'))
    actual_budget_usd = models.DecimalField('Actual Budget USD', decimal_places=4, max_digits=16,
                                            default=Decimal('0.0000'))
    actual_expenditure_usd = models.DecimalField('Actual Expenditure USD', decimal_places=4, max_digits=16,
                                                 default=Decimal('0.0000'))
    actual_budget_local = models.DecimalField('Actual Budget Local', decimal_places=4, max_digits=16,
                                              default=Decimal('0.0000'))
    actual_expenditure_local = models.DecimalField('Actual Expenditure Local', decimal_places=4, max_digits=16,
                                                   default=Decimal('0.0000'))
    donor_currency = models.ForeignKey('activity.Currency', verbose_name='Donor Currency', null=True,
                                       on_delete=models.SET_NULL)
    history = HistoricalRecords()
    create_date = models.DateTimeField('Create Date', null=True, blank=True, editable=False)
    modified_date = models.DateTimeField('Modified Date', null=True, blank=True)
    created_by = models.ForeignKey(ActivityUser, verbose_name='Created By', editable=False, null=True,
                                   related_name='budget_created_by', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(ActivityUser, verbose_name='Modified By', editable=False, null=True,
                                    related_name='budget_modified_by', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('create_date',)
        verbose_name_plural = 'Budgets'

    def __str__(self):
        return self.contributor or ''

    def save(self, *args, **kwargs):
        logged_user = ActivityUser.objects.get(user=get_request().user)
        if not self.id:
            self.create_date = timezone.now()
            self.created_by = logged_user
        self.modified_date = timezone.now()
        self.modified_by = logged_user
        return super(Budget, self).save(*args, **kwargs)

    @property
    def percent_of_budget_spent(self):
        return Decimal(self.actual_expenditure_donor_currency) / Decimal(self.actual_budget_donor_currency)

    @property
    def remaining_expenditure(self):
        return Decimal(self.actual_budget_donor_currency) - Decimal(self.actual_expenditure_donor_currency)

