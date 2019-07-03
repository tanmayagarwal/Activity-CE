#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
import json data from API
IMPORTANT!! you must turn off pagination for this to work from a URL
and get all country records
Install module django-extensions
Runs twice via function calls at bottom once
"""
from workflow.models import Country, WorkflowLevel1
from datetime import date
import urllib.request
import sys
import json
from django.db import connection, transaction

cursor = connection.cursor()


def run():
    print("Uploading JSON data")


type = "WorkflowLevel1"
program_country = 1


def get_all_data(url, type, program_country):

    # set url for json feed here
    json_file = urllib.request.urlopen(url)

    # load data
    data = json.load(json_file)
    json_file.close()

    #print(data

    # query to mysql database after parsing json data
    def save_countries(keys_to_sql, vars_to_sql):
        # save the original keys list for update in case we need to run that
        save_keys = keys_to_sql
        keys_to_sql = ", ".join(map(str, keys_to_sql))

        query = "INSERT INTO activitydb_country (country,code) " \
                "VALUES ('%s','%s')" % (
            vars_to_sql[0], vars_to_sql[1])
        print(query)

        try:
            cursor.execute(query)
            transaction.commit()
        except Exception as err:
            sys.stderr.write('ERROR: %s\n' % str(err))
            column = save_keys[1]
            value = 1
            country = vars_to_sql[0]
            if type == "country":
                query_update = "UPDATE activitydb_country set country = %s " \
                               "where lower(%(type)s) = '%s'" % (
                    column, value, country.lower())
            try:
                cursor.execute(query_update)
                transaction.commit()
            except Exception as err:
                sys.stderr.write('ERROR: %s\n' % str(err))
            return 1
    pass

    # query to mysql database after parsing json data
    def save_programs(keys_to_sql, vars_to_sql, program_country):
        # save the original keys list for update in case we need to run that
        save_keys = keys_to_sql
        keys_to_sql = ", ".join(map(str, keys_to_sql))

        var_to_tuple = tuple(vars_to_sql)
        print(var_to_tuple)

        query = "INSERT INTO activitydb_program (%s) VALUES %s" % (
            keys_to_sql, var_to_tuple)
        print(query)

        try:
            cursor.execute(query)
            transaction.commit()
        except Exception as err:
            sys.stderr.write('ERROR: %s\n' % str(err))
        pass

        latest = WorkflowLevel1.objects.latest('id')

        query2 = "INSERT INTO activitydb_program_country " \
                 "(country_id,program_id) VALUES (%s,%s)" % (
            program_country, latest.id)

        print(query2)
        try:
            cursor.execute(query2)
            transaction.commit()
        except Exception as err:
            sys.stderr.write('ERROR: %s\n' % str(err))
        pass

    for row in data:
        print(row)
        vars_to_sql = []
        keys_to_sql = []
        for new_key, new_value in row.iteritems():
            try:
                new_key = new_key.encode('ascii', 'ignore')
                new_value = new_value.encode('ascii', 'ignore')
            except Exception as err:
                sys.stderr.write('ERROR: %s\n' % str(err))
            # print(new_key)
            # print(new_valu)e
            if type == "Country":
                if new_value:
                    # country or region related columns only
                    if new_key in ('country', 'region', 'iso_code'):
                        # change iso_code to code for DB table
                        if new_key == 'iso_code':
                            new_key = 'code'
                        keys_to_sql.append(new_key)
                        vars_to_sql.append(new_value)
            elif type == "WorkflowLevel1":
                if new_value:
                    # country or region related columns only
                    if new_key in ('gaitid', 'funding_status', 'granttitle',
                                   'cost_center'):
                        # change iso_code to code for DB table
                        if new_key == 'granttitle':
                            new_key = 'name'
                        keys_to_sql.append(new_key)
                        vars_to_sql.append(new_value)

        # add create_date to comma seperated list of columns
        keys_to_sql.append("create_date")
        # append todays date to var
        today = date.today()
        today.strftime('%Y-%m-%d')
        today = str(today)
        vars_to_sql.append(today)

        # add description to comma separated list of columns
        keys_to_sql.append("description")
        # append todays date to var
        vars_to_sql.append("")

        if type == "Country":
            save_countries(keys_to_sql, vars_to_sql)
        elif type == "WorkflowLevel1":
            save_programs(keys_to_sql, vars_to_sql, program_country)


# TODO : Change urls or delete lines
# get an updated json data file for the hub and update or insert new records
print("WorkflowLevel1")
get_countries = Country.objects.all()
for country in get_countries:
    print(country.country)
    safe_country = urllib.quote_plus(country.country)
    program_url = \
        "http://mcapi.mercycorps.org/gaitprogram/?country=%s&format=json" % (
            safe_country)
    print(program_url)
    get_all_data(program_url, "WorkflowLevel1", int(country.id))

print("Alright, all done.")
