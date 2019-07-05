#!/usr/bin/python3
# -*- coding: utf-8 -*-

import django_filters
from .models import WorkflowLevel2


class ProjectAgreementFilter(django_filters.FilterSet):

    class Meta:
        model = WorkflowLevel2
        fields = ['name', 'workflow_level1']

    def __init__(self, *args, **kwargs):
        super(ProjectAgreementFilter, self).__init__(*args, **kwargs)
