#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Count
from django.db import IntegrityError

from indicators.models import IndicatorResult, Indicator

from workflow.models import (WorkflowLevel2, WorkflowLevel1, ActivityUser,
                             ActivitySites, ActivityBookmarks, FormGuidance
)
from activity.models import (Location, Country, Sector, Organization)
from activity.tables import IndicatorDataTable
from activity.util import get_organizations, get_nav_links
from activity.forms import (
    RegistrationForm, BookmarkForm, OrganizationEditForm)
from django.core import serializers
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string


@login_required(login_url='/accounts/login/')
def index(request, selected_organizations=None, id=0, sector=0):
    """
    Home page
    get count of agreements approved and total for dashboard
    """

    # add program
    if request.method == 'POST' and request.is_ajax:
        return add_program(request)

    program_id = id
    user_countries = get_organizations(request.user)

    if not selected_organizations:
        selected_organizations = user_countries
        selected_countries_list = None
        selected_countries_label_list = None
    else:
        # transform to list if a submitted country
        selected_organizations = [selected_organizations]
        selected_countries_list = Organization.objects.all().filter(
            id__in=selected_organizations)
        selected_countries_label_list = Organization.objects.all().filter(
            id__in=selected_organizations).values('country')

    get_agency_site = ActivitySites.objects.all().filter(id=1)
    get_sectors = Sector.objects.all().select_related()
    get_all_sectors = Sector.objects.all()

    # limit the programs by the selected sector
    if int(sector) == 0:
        get_programs = WorkflowLevel1.objects.all()\
            .prefetch_related('agreement', 'agreement__office').filter(
            funding_status__status="Funded", organization__in=selected_organizations)
        # .exclude(agreement__isnull=True)
        sectors = Sector.objects.all()
    else:
        get_programs = WorkflowLevel1.objects.all()\
            .filter(funding_status="Funded",
                    country__in=selected_organizations, sector=sector)
        sectors = Sector.objects.all().filter(id=sector)

    filter_for_quantitative_data_sums = {
        'indicator__key_performance_indicator': True,
        'periodic_target__isnull': False,
        'result__isnull': False,
    }

    # get data for just one program or all programs
    if int(program_id) == 0:
        get_filtered_name = None
        filter_for_quantitative_data_sums[
            'indicator__program__country__in'] = selected_organizations

        # filter by all programs then filter by sector if found
        if int(sector) > 0:
            filter_for_quantitative_data_sums[
                'agreement__sector__in'] = sectors
            get_site_profile = Location.objects.all().prefetch_related(
                'country', 'district', 'province').filter(
                Q(Q(projectagreement__sector__in=sectors)),
                country__in=selected_organizations).filter(status=1)
            get_site_profile_indicator = Location.objects.all()\
                .prefetch_related('country', 'district', 'province').filter(
                Q(collecteddata__program__country__in=selected_organizations))\
                .filter(status=1)
            agreement_total_count = WorkflowLevel2.objects.all().filter(
                sector__in=sectors,
                program__country__in=selected_organizations).count()
            complete_total_count = WorkflowLevel2.objects.all().filter(
                project_agreement__sector__in=sectors,
                program__country__in=selected_organizations).count()
            agreement_approved_count = WorkflowLevel2.objects.all().filter(
                approval='approved', sector__in=sectors,
                program__country__in=selected_organizations).count()
            complete_approved_count = WorkflowLevel2.objects.all().filter(
                approval='approved', project_agreement__sector__in=sectors,
                program__country__in=selected_organizations).count()

            agreement_awaiting_count = WorkflowLevel2.objects.all().filter(
                approval='awaiting approval', sector__in=sectors,
                program__country__in=selected_organizations).count()

            complete_awaiting_count = WorkflowLevel2.objects.all().filter(
                approval='awaiting approval',
                project_agreement__sector__in=sectors,
                program__country__in=selected_organizations).count()

            agreement_open_count = WorkflowLevel2.objects.all().filter(
                Q(Q(approval='open') | Q(approval="") | Q(
                    approval=None)), sector__id__in=sectors,
                program__country__in=selected_organizations).count()
            complete_open_count = WorkflowLevel2.objects.all().filter(
                Q(Q(approval='open') | Q(approval="") | Q(approval=None)),
                project_agreement__sector__in=sectors,
                program__country__in=selected_organizations).count()
            agreement_wait_count = WorkflowLevel2.objects.all().filter(
                Q(approval='in progress') & Q(
                    Q(approval='in progress') | Q(approval=None) | Q(
                        approval="")),
                sector__in=sectors,
                program__country__in=selected_organizations).count()
            complete_wait_count = WorkflowLevel2.objects.all().filter(
                Q(approval='in progress') & Q(
                    Q(approval='in progress') | Q(approval=None) | Q(
                        approval="")),
                project_agreement__sector__in=sectors,
                program__country__in=selected_organizations).count()

        else:
            get_site_profile = Location.objects.all()
            get_site_profile_indicator = Location.objects.all()
            agreement_total_count = WorkflowLevel2.objects.all().filter(
                workflow_level1__organization__in=selected_organizations).count()
            complete_total_count = WorkflowLevel2.objects.all().filter(
                workflow_level1__organization__in=selected_organizations).count()
            agreement_approved_count = WorkflowLevel2.objects.all().filter(
                 workflow_level1__organization__in=selected_organizations).count()
            complete_approved_count = WorkflowLevel2.objects.all().filter(
                 workflow_level1__organization__in=selected_organizations).count()

            agreement_awaiting_count = WorkflowLevel2.objects.all().filter(
                 workflow_level1__organization__in=selected_organizations).count()
            complete_awaiting_count = WorkflowLevel2.objects.all().filter(
                 workflow_level1__organization__in=selected_organizations).count()
            agreement_open_count = WorkflowLevel2.objects.all().filter(
                workflow_level1__organization__in=selected_organizations).count()
            complete_open_count = WorkflowLevel2.objects.all().filter(
                workflow_level1__organization__in=selected_organizations).count()
            agreement_wait_count = WorkflowLevel2.objects.all().filter(
                workflow_level1__organization__in=selected_organizations).count()
            complete_wait_count = WorkflowLevel2.objects.all().filter(
                workflow_level1__organization__in=selected_organizations).count()

    else:
        filter_for_quantitative_data_sums[
            'indicator__program__id'] = program_id

        get_filtered_name = WorkflowLevel1.objects.get(id=program_id)
        agreement_total_count = WorkflowLevel2.objects.all().filter(
            workflow_level1__id=program_id).count()
        complete_total_count = WorkflowLevel2.objects.all().filter(workflow_level1__id=program_id).count()
        agreement_approved_count = WorkflowLevel2.objects.all().filter(
            workflow_level1__id=program_id).count()
        complete_approved_count = WorkflowLevel2.objects.all().filter(
            workflow_level1__id=program_id).count()
        agreement_open_count = WorkflowLevel2.objects.all().filter(
            workflow_level1__id=program_id).count()
        complete_open_count = WorkflowLevel2.objects.all().filter(workflow_level1__id=program_id).count()
        agreement_wait_count = WorkflowLevel2.objects.all().count()
        complete_wait_count = WorkflowLevel2.objects.all().filter(workflow_level1__id=program_id).count()
        get_site_profile = Location.objects.all()
        get_site_profile_indicator = Location.objects.all()

        agreement_awaiting_count = WorkflowLevel2.objects.all().filter(
            workflow_level1__id=program_id).count()
        complete_awaiting_count = WorkflowLevel2.objects.all().filter(
            workflow_level1__id=program_id).count()

    get_quantitative_data_sums = IndicatorResult.objects.all()
        # .filter(**filter_for_quantitative_data_sums) \
    #         # .exclude(result=None, periodic_target=None,
    #         #          workflow_level1__funding_status__status="Archived") \
    #         # .order_by('indicator__workflow_level1',) \
    #         # .values('indicator__overall_target', 'indicator__workflow_level1__id',
    #         #         'indicator__workflow_level1__name', 'indicator__name', 'indicator__id') \
    #         # .annotate(targets=Sum('periodic_target'), actuals=Sum('result'))

    # Evidence and Objectives are for the global leader dashboard
    # items and are the same every time
    count_evidence = IndicatorResult.objects.all().filter(
        indicator__isnull=False) \
        .values("indicator__workflow_level1__organization__full_name").annotate(
        indicator_count=Count('pk', distinct=True))
    get_objectives = IndicatorResult.objects.filter(
        indicator__objective__isnull=False,
        indicator__workflow_level1__organization__in=selected_organizations) \
        .exclude(reporting_period=None) \
        .order_by('indicator__objective__name') \
        .values('indicator__objective__name') \
        .annotate(
        indicators=Count('indicator__pk', distinct=True))
    table = IndicatorDataTable(get_quantitative_data_sums)
    table.paginate(page=request.GET.get('page', 1), per_page=20)

    count_program = WorkflowLevel1.objects.all().filter(
        organization__in=selected_organizations, funding_status__status='Funded').count()

    # approved_by = ActivityUser.objects.get(user_id=request.user)
    user_pending_approvals = WorkflowLevel2.objects.all()

    count_program_agreement = WorkflowLevel2.objects.all().filter(
        workflow_level1__organization__in=selected_organizations,
        workflow_level1__funding_status__status='Funded').values('workflow_level1').distinct().count()
    count_indicator = Indicator.objects.all().filter(
        workflow_level1__organization__in=selected_organizations,
        workflow_level1__funding_status__status='Funded').values('workflow_level1').distinct().count()
    count_evidence_adoption = IndicatorResult.objects.all().filter(
        indicator__isnull=False,
        indicator__workflow_level1__organization__in=selected_organizations) \
        .values("indicator__workflow_level1__organization__full_name") \
        .annotate(indicator_count=Count('pk', distinct=True));
    count_program = int(count_program)
    count_program_agreement = int(count_program_agreement)

    green = "#5CB85C"
    yellow = "#E89424"
    red = "#B30838"

    # 66% or higher = Green above 25% below %66 is Orange and below %25 is Red

    if count_program_agreement >= float(count_program / 1.5):
        workflow_adoption = green
    elif count_program / 1.5 > count_program_agreement > count_program / 4:
        workflow_adoption = yellow
    elif count_program_agreement <= count_program / 4:
        workflow_adoption = red

    if count_indicator >= float(count_program / 1.5):
        indicator_adoption = green
    elif count_program / 1.5 > count_indicator > count_program / 4:
        indicator_adoption = yellow
    elif count_indicator <= count_program / 4:
        indicator_adoption = red

    total_evidence_adoption_count = 0
    total_indicator_data_count = 0
    for country in count_evidence_adoption:
        total_evidence_adoption_count = total_evidence_adoption_count + \
            country['evidence_count']
        total_indicator_data_count = total_indicator_data_count + \
            country['indicator_count']

    if total_evidence_adoption_count >= float(
            total_indicator_data_count / 1.5):
        evidence_adoption = green
    elif total_indicator_data_count / 1.5 > total_evidence_adoption_count > \
            total_indicator_data_count / 4:
        evidence_adoption = yellow
    elif total_evidence_adoption_count <= total_indicator_data_count / 4:
        evidence_adoption = red

    return render(request, "index.html", {
        'agreement_total_count': agreement_total_count,
        'agreement_approved_count': agreement_approved_count,
        'agreement_open_count': agreement_open_count,
        'agreement_wait_count': agreement_wait_count,
        'agreement_awaiting_count': agreement_awaiting_count,
        'complete_open_count': complete_open_count,
        'complete_approved_count': complete_approved_count,
        'complete_total_count': complete_total_count,
        'complete_wait_count': complete_wait_count,
        'complete_awaiting_count': complete_awaiting_count,
        'programs': get_programs,
        'get_site_profile': get_site_profile,
        'countries': user_countries,
        'selected_countries': selected_organizations,
        'get_filtered_name': get_filtered_name,
        'get_sectors': get_sectors,
        'get_all_sectors': get_all_sectors,
        'sector': sector, 'table': table,
        'get_quantitative_data_sums': get_quantitative_data_sums,
        'count_evidence': count_evidence,
        'get_objectives': get_objectives,
        'selected_countries_list': selected_countries_list,
        'get_site_profile_indicator': get_site_profile_indicator,
        'get_agency_site': get_agency_site,
        'workflow_adoption': workflow_adoption,
        'count_program': count_program,
        'count_program_agreement': count_program_agreement,
        'indicator_adoption': indicator_adoption,
        'count_indicator': count_indicator,
        'evidence_adoption': evidence_adoption,
        'count_evidence_adoption': total_evidence_adoption_count,
        'count_indicator_data': total_indicator_data_count,
        'selected_countries_label_list': selected_countries_label_list,
        'user_pending_approvals': user_pending_approvals,
    })


def switch_organization(request, org_id):
    organization = Organization.objects.filter(id=int(org_id)).first()
    activity_user = ActivityUser.objects.filter(user=request.user).first()
    activity_user.organization = organization
    activity_user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user)
        return HttpResponseRedirect('/')
    else:
        return HttpResponse('Activation link is invalid!')


class EmailError(Exception):
    """Existing Email Error"""
    pass


def register(request):
    """
    Register a new User profile using built in Django Users Model
    """
    # privacy = ActivitySites.objects.get(id=1)
    if request.method == 'POST':
        data = request.POST
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email_address')
        password = data.get('password')

        try:
            if User.objects.filter(email=email):
                raise EmailError

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                is_active=False,
            )
        except EmailError:
            return render(request, 'registration/register.html',
                          {"message_email": "email already exists !"})
        except IntegrityError:
            return render(request, 'registration/register.html',
                          {"message_username": "username already exists !"})

        current_site = get_current_site(request)
        mail_subject = 'Activate your Activity account.'
        message = render_to_string('registration/activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        email = EmailMessage(
            mail_subject, message, to=[email]
        )
        email.send()
        if user:
            activity_user = ActivityUser.objects.create(user=user)
            if activity_user:
                return HttpResponse('Please confirm your email address to '
                                    'complete the registration')

            else:
                return render(request, 'registration/register.html')

    else:
        return render(request, 'registration/register.html')


def user_login(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            activity_user = ActivityUser.objects.filter(user=user).first()
            if activity_user.organization:
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/accounts/register/organization')

        else:
            render(request, 'registration/login.html')
    return render(request, 'registration/login.html')


def register_organization(request):
    """
    register organization
    : param request:
    : return org profile page
    """
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        description = data.get('description')

        org = Organization.objects.create(name=name, description=description)
        if org:
            user = ActivityUser.objects.filter(user=request.user).first()
            user.organization = org
            user.save()
            return redirect('admin_profile_settings')
        else:
            return redirect('register_organization')
    else:
        return render(request, 'registration/organization_register.html')


def profile(request):
    """
    Update a User profile using built in Django Users Model if the user
    is logged in otherwise redirect them to registration version
    """
    if request.user.is_authenticated:
        obj = get_object_or_404(ActivityUser, user=request.user)
        form = RegistrationForm(request.POST or None, instance=obj,
                                initial={'username': request.user})

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.error(
                    request, 'Your profile has been updated.',
                    fail_silently=False)

        return render(request, 'registration/profile.html', {
            'form': form, 'helper': RegistrationForm.helper
        })
    else:
        return HttpResponseRedirect('/accounts/register')


def admin_dashboard(request):
    """
    Admin dashboard view
    """
    nav_links = get_nav_links('Home')
    return render(
        request,
        'admin/landing_page.html',
        {'nav_links': nav_links}
    )


def admin_configurations(request):
    logged_activity_user = ActivityUser.objects.get(user=request.user)

    if request.method == 'POST' and request.is_ajax:
        data = request.POST

        model_updates = {
            'level_1_label': data.get('level_1_label'),
            'level_2_label': data.get('level_2_label'),
            'level_3_label': data.get('level_3_label'),
            'level_4_label': data.get('level_4_label'),
            'stakeholder_label': data.get('stakeholder_label'),
            'date_format': data.get('date_format'),
            # 'default_currency': data.get('default_currency')
        }
        organization = Organization.objects.filter(
            id=logged_activity_user.organization.id)
        updates = organization.update(**model_updates)
        if updates:
            organization_changes = Organization.objects.filter(
                id=logged_activity_user.organization.id)
            data = serializers.serialize('json', organization_changes)
            return HttpResponse(data, content_type="application/json")

    nav_links = get_nav_links('Configurations')
    return render(
        request,
        'admin/default_settings.html',
        {'nav_links': nav_links,
         'organization': logged_activity_user.organization}
    )


def admin_profile_settings(request):
    user = get_object_or_404(ActivityUser, user=request.user)
    organization = user.organization
    if request.method == 'POST':
        form = OrganizationEditForm(request.FILES,
                                    instance=organization)
        if form.is_valid():

            organization.logo = request.FILES.get('logo')
            organization.save()
            user.organization = organization
            user.save()
            messages.error(
                request, 'Your organization logo has been updated.',
                fail_silently=False)
    else:
        form = OrganizationEditForm(instance=organization)

    nav_links = get_nav_links('Profile Settings')
    return render(
        request,
        'admin/profile_settings.html',
        {'nav_links': nav_links,
         'form': form}
    )


def admin_user_management(request):
    nav_links = get_nav_links('User Management')
    return render(
        request,
        'admin/user_management.html',
        {'nav_links': nav_links}
    )


def add_program(request):
    """ 
    Add program
    """
    data = request.POST
    activity_user = ActivityUser.objects.filter(user=request.user).first()
    program = WorkflowLevel1(name=data.get(
        'program_name'), start_date=data.get('start_date'),
        end_date=data.get('end_date'), organization=activity_user.organization)

    try:
        program.save()

        sectors = Sector.objects.filter(id__in=data.getlist('sectors[]'))
        program.sector.set(sectors)

        # Return a "created" (201) response code.
        return HttpResponse(program)
    except Exception as ex:
        raise Exception(ex)


class BookmarkList(ListView):
    """
    Bookmark Report filtered by project
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_list.html'

    def get(self, request, *args, **kwargs):
        get_user = ActivityUser.objects.all().filter(user=request.user)
        get_bookmarks = ActivityBookmarks.objects.all().filter(user=get_user)
        return render(request, self.template_name,
                      {'get_bookmarks': get_bookmarks})


class BookmarkCreate(CreateView):
    """
    Using Bookmark Form for new bookmark per user
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_form.html'
    guidance = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Bookmarks")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BookmarkCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BookmarkCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = {
            'user': self.request.user,
        }
        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Created!')
        latest = ActivityBookmarks.objects.latest('id')
        redirect_url = '/bookmark_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = BookmarkForm


class BookmarkUpdate(UpdateView):
    """
    Bookmark Form Update an existing site profile
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_form.html'
    guidance = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Bookmarks")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BookmarkUpdate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = {
            'user': self.request.user,
        }
        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Updated!')
        latest = ActivityBookmarks.objects.latest('id')
        redirect_url = '/bookmark_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = BookmarkForm


class BookmarkDelete(DeleteView):
    """
    Bookmark Form Delete an existing bookmark
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_confirm_delete.html'
    success_url = "/bookmark_list"

    def dispatch(self, request, *args, **kwargs):
        return super(BookmarkDelete, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BookmarkForm


def logout_view(request):
    """
    Logout a user
    """
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/")
