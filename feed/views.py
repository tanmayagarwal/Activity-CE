#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import django_filters

from .serializers import *
from activity.util import get_organizations

from workflow.mixins import APIDefaultsMixin

from activity.models import (Location, Country, Sector, LocationType, Office, Organization)
from workflow.models import (
    WorkflowLevel1, ProjectType, Checklist,
    WorkflowLevel2, Capacity, Evaluate, Contact, Documentation,
    Province, District, AdminLevelThree, Village, StakeholderType
)
from indicators.models import (
    Indicator, ReportingPeriod, ActivityUser, IndicatorType, DisaggregationType,
    IndicatorLevel, ExternalService, ExternalServiceRecord, Objective, IndicatorResult,
    ActivityTable, DisaggregationValue, DisaggregationLabel
)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class PeriodicTargetReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PeriodicTargetSerializer

    def get_queryset(self):
        queryset = ReportingPeriod.objects.all()
        indicator_id = self.request.query_params.get('indicator', None)
        if indicator_id:
            queryset = queryset.filter(indicator=indicator_id)
        return queryset


class PogramIndicatorReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgramIndicatorSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = WorkflowLevel1.objects.prefetch_related(
            'indicator_set',
            'indicator_set__indicator_type',
            'indicator_set__sector', 'indicator_set__level',
            'indicator_set__collecteddata_set').all()
        return queryset

# API Classes


class UserViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing or retrieving users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    search by country name and program name
    limit to users logged in country permissions
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = WorkflowLevel1.objects.all().filter(country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('country__country', 'name')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = WorkflowLevel1.objects.all()
    serializer_class = ProgramSerializer


class SectorViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer


class ProjectTypeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer


class OfficeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer


class SiteProfileViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Search by country name and program name
    limit to users logged in country permissions
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = Location.objects.all().filter(country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('country__country',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = Location .objects.all()
    serializer_class = SiteProfileSerializer


class CountryViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class AgreementViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Search by country name and program name
    limit to users logged in country permissions
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = WorkflowLevel2.objects.all().filter(
            program__country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    """
    def post(self,request):

        for each agreement
            insert int and string fields direct
            if FK field

        return blank
    """

    filter_fields = ('program__country__country', 'program__name')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = WorkflowLevel2.objects.all()
    serializer_class = AgreementSerializer
    pagination_class = SmallResultsSetPagination


class CompleteViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Search by country name and program name
    limit to users logged in country permissions
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = WorkflowLevel2.objects.all().filter(
            program__country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('program__country__country', 'program__name')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = WorkflowLevel2.objects.all()
    serializer_class = CompleteSerializer
    pagination_class = SmallResultsSetPagination


class IndicatorViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Search by country name and program name
    limit to users logged in country permissions
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = Indicator.objects.all().filter(
            program__country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('program__country__country', 'program__name')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer


class ReportingFrequencyViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = ReportingPeriod.objects.all()
    serializer_class = ReportingFrequencySerializer


class ActivityUserViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for listing or retrieving ActivityUsers.

    """

    def list(self, request):
        queryset = ActivityUser.objects.all()
        serializer = ActivityUserSerializer(instance=queryset, context={
                                        'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = ActivityUser.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = ActivityUserSerializer(
            instance=user, context={'request': request})
        return Response(serializer.data)

    queryset = ActivityUser.objects.all()
    serializer_class = ActivityUserSerializer


class IndicatorTypeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = IndicatorType.objects.all()
    serializer_class = IndicatorTypeSerializer


class ObjectiveViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Objective.objects.all()
    serializer_class = ObjectiveSerializer


class DisaggregationTypeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = DisaggregationType.objects.all()
    serializer_class = DisaggregationTypeSerializer


class LevelViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = IndicatorLevel.objects.all()
    serializer_class = LevelSerializer


class StakeholderViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Search by Country
    Limited to logged in users accessible countires
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = Organization.objects.all().filter(country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('country__country',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = Organization.objects.all()
    serializer_class = StakeholderSerializer


class ExternalServiceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = ExternalService.objects.all()
    serializer_class = ExternalServiceSerializer


class ExternalServiceRecordViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = ExternalServiceRecord.objects.all()
    serializer_class = ExternalServiceRecordSerializer


class StrategicObjectiveViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Objective.objects.all()
    serializer_class = StrategicObjectiveSerializer


class StakeholderTypeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = StakeholderType.objects.all()
    serializer_class = StakeholderTypeSerializer


class CapacityViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Capacity.objects.all()
    serializer_class = CapacitySerializer


class EvaluateViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Evaluate.objects.all()
    serializer_class = EvaluateSerializer


class ProfileTypeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = LocationType.objects.all()
    serializer_class = ProfileTypeSerializer


class ProvinceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class AdminLevelThreeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = AdminLevelThree.objects.all()
    serializer_class = AdminLevelThreeSerializer


class VillageViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Village.objects.all()
    serializer_class = VillageSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class DocumentationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Documentation.objects.all()
    serializer_class = DocumentationSerializer


class CollectedDataViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = IndicatorResult.objects.all().filter(
            program__country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('indicator__program__country__country',
                     'indicator__program__name')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = IndicatorResult.objects.all()
    serializer_class = CollectedDataSerializer
    pagination_class = SmallResultsSetPagination


class ActivitytableViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user_countries = get_organizations(self.request.user)
        queryset = ActivityTable.objects.filter(country__in=user_countries)
        table_id = self.request.query_params.get('table_id', None)
        if table_id is not None:
            queryset = queryset.filter(table_id=table_id)
        return queryset

    filter_fields = ('table_id', 'country__country',
                     'collecteddata__indicator__program__name')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    serializer_class = ActivitytableSerializer
    pagination_class = StandardResultsSetPagination


class DisaggregationValueViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    def list(self, request):
        user_countries = get_organizations(request.user)
        queryset = DisaggregationValue.objects.all().filter(
            country__in=user_countries)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('country__country', 'indicator__program__name')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = DisaggregationValue.objects.all()
    serializer_class = DisaggregationValueSerializer
    pagination_class = StandardResultsSetPagination

# Returns a list of all project agreement and feed to Hikaya


class ProjectAgreementViewSet(APIDefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for getting WorkflowLevel2."""

    queryset = WorkflowLevel2.objects.order_by('create_date')
    serializer_class = AgreementSerializer


class LoggedUserViewSet(APIDefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for getting Logged Users."""

    queryset = LoggedUser.objects.all()
    serializer_class = LoggedUserSerializer


class ChecklistViewSet(APIDefaultsMixin, viewsets.ModelViewSet):
    queryset = Checklist.objects.all()
    serializer_class = ChecklistSerializer


class OrganizationViewSet(APIDefaultsMixin, viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
