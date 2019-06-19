#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import *


# use these form classes to enforce unique emails, if required
class UniqueEmailForm:
    def clean_email(self):
        qs = User.objects.filter(email=self.cleaned_data['email'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count():
            raise forms.ValidationError(
                'That email address is already in use')
        else:
            return self.cleaned_data['email']


class MyUserChangeForm(UniqueEmailForm, UserChangeForm):
    email = forms.EmailField(required=True)


class MyUserCreationForm(UniqueEmailForm, UserCreationForm):
    email = forms.EmailField(required=True)


class MyUserAdmin(UserAdmin):
    # add the email field in to the initial add_user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
    )

    actions = ['make_active', 'make_inactive']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined',
                   'last_login']

    form = MyUserChangeForm
    add_form = MyUserCreationForm


# Re-register UserAdmin with custom options
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


# NEW MODELS
@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'create_date', 'updated_by',)
    list_filter = ('created_by',)
    display = 'Workspaces'


@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'created_by', 'create_date',)
    list_filter = ('created_by',)
    display = 'Organization Types'


@admin.register(OrganizationSubType)
class OrganizationSubTypeAdmin(admin.ModelAdmin):
    list_display = ('sub_type', 'created_by', 'create_date',)
    list_filter = ('created_by',)
    display = 'Organization Sub-Types'


@admin.register(Organization)
class Organization1Admin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name', 'parent_organization', 'create_date',)
    list_filter = ('created_by',)
    display = 'Organizations'


@admin.register(Sector)
class Sector1Admin(admin.ModelAdmin):
    list_display = ('sector', 'created_by', 'create_date')
    list_filter = ('parent_sector', 'created_by')
    display = 'Sectors'


@admin.register(Contact)
class Contact1Admin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'created_by', 'create_date')
    list_filter = ('organization__name', 'created_by__name')
    display = 'Contacts'


@admin.register(LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'created_by', 'create_date')
    list_filter = ('type',)
    display = ' Location Types'


@admin.register(AdministrativeLevel)
class AdministrativeLevelAdmin(admin.ModelAdmin):
    list_display = ('level_1', 'level_2', 'level_3', 'level_4')
    display = 'Administrative Levels'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_location', 'contact', 'created_by', 'create_date')
    list_filter = ('parent_location__name', 'contact__first_name')
    display = 'Locations'


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'workspace', 'created_by', 'create_date')
    list_filter = ('workspace__name',)
    display = 'Portfolio'
