import json
import psycopg2
from psycopg2.extras import RealDictCursor
import itertools
import subprocess
import os
import logging

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.forms.models import model_to_dict
from django.urls import reverse
from django.db.models import Q

from rest_framework import serializers
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from ui.models import Concept, Study, TableColumn, StudyToOhdsiMapping, ExtractStudy, CategorizationFunctionMetadata, StudyToOhdsiMappingFunction, CategorizationFunctions, MappingFunctions, CategorizationFunctionParameters, Person
from ui.forms import StudyToOhdsiMappingFunctionForm

from HeartData import migrate
from HeartData import calculate
from HeartData import extract
import HeartData.load_studies
from HeartData.person import  BasePerson
from HeartData.migrate import select_values
from HeartData.observation import  fetch

# Naming Conventions:
# get_thing returns a single thing
# get_thing_list returns a list
# get_thing_like returns a list on a like/wildcard query
# get_thing_for_attribute returns a list
# get_thing_for_attribute_attribute returns a list filtered by two attributes
# get_thing_by_attribute returns a map/dictionary/hash

logger = logging.getLogger(__name__)

# ========== !!! =======================
def get_cursor() :
    db_name = os.environ.get("PGDATABASE")
    user_name = os.environ.get("PGUSER")
    con = psycopg2.connect(database=db_name, user=user_name) 
    con.autocommit=True
    value_cursor = con.cursor(cursor_factory=RealDictCursor)
    return((value_cursor, con))
# ========== !!! =======================

# -- FOR REST ----
class ConceptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Concept
        fields = ('concept_id', 'concept_name', 'vocabulary_id' , 'concept_code')

class StudySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Study
        fields = ('study_id', 'study_name', 'person_id_range_start', 'person_id_range_end', 'observation_range_start', 'observation_range_end', 'loaded', 'migrated', 'calculated')

class ExtractStudySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExtractStudy
        fields = ('extract_study_id', 'study_id', 'name', 'comment')

class TableColumnSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TableColumn
        fields = ('study_id', 'table_name', 'column_name')

class StudyToOhdsiMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyToOhdsiMapping
        fields =  ('study_id', 'from_table', 'from_column', 'function_name', 'vocabulary_id', 'concept_code', 'to_table', 'to_column',
                'addl_value_1', 'addl_column_1', 'from_where_clause', 'comment', 'from_where_column', 'units', 'has_date')

class StudyToOhdsiMappingFunctionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StudyToOhdsiMappingFunction
        fields = ('study_id', 'from_table', 'from_column', 'function_name', 'vocabulary_id', 'concept_code', 'from_int', 'from_value', 'to_concept', 'conversion_factor')

#class OhdsiMappingFunctionSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = OhdsiMappingFunction
#        fields = ('function_name', 'study_id', 'module_name', 'comment')

        

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_mapping_for_study(request, study_id) :
    mapping_list = StudyToOhdsiMapping.objects.filter(study=study_id).order_by('vocabulary_id')

    json_list=list()
    for m in mapping_list:
        serializer = StudyToOhdsiMappingSerializer(m)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_mapping_for_study_table(request, study_id, table_name) :
    mapping_list = StudyToOhdsiMapping.objects.filter(study=study_id, from_table=table_name).order_by('vocabulary_id')

    json_list=list()
    for m in mapping_list:
        serializer = StudyToOhdsiMappingSerializer(m)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_mapping_for_study_table_column(request, study_id, table_name, column_name) :
    mapping_list = StudyToOhdsiMapping.objects.filter(study=study_id, from_table=table_name, from_column=column_name)

    json_list=list()
    for m in mapping_list:
        serializer = StudyToOhdsiMappingSerializer(m)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

# TODO: viewsets? ...there's something in Django for simple get_all queries like this...
@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_concepts_like(request, vocab_id, string, mapped, extract):

    ## LIMIT TO 100 ####################################
    concept_list = Concept.objects.filter(vocabulary_id=vocab_id, concept_name__icontains=string)[:100]
    ## ##################################################

    json_list=list()
    for c in concept_list:
        serializer = ConceptSerializer(c)
        json_list.append(serializer.data)
    # note about old attack vector regarding serializing lists and that safe=False flag:
    # https://docs.djangoproject.com/en/1.9/ref/request-response/#jsonresponse-objects
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_concept_by_id(request, concept_id):
    concept_list = Concept.objects.filter(concept_id=concept_id)
    json_list=list()
    for c in concept_list:
        serializer = ConceptSerializer(c)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_concept_by_vocab_and_concept_code(request, vocabulary_id, concept_code):
    concept_list = Concept.objects.filter(vocabulary_id=vocabulary_id).filter(concept_code=concept_code)
    json_list=list()
    for c in concept_list:
        serializer = ConceptSerializer(c)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json


@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_all_studies(request): #study_list = Study.objects.exclude(study_id != 0).order_by(study_id)
# DFQ?! TODO FIX
    study_list = Study.objects.all().order_by('study_id')
    json_list=list()
    for s in study_list:
        serializer = StudySerializer(s)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_extract_study_list(request):
    study_list = ExtractStudy.objects.all().order_by('extract_study_id')
    json_list=list()
    for s in study_list:
        serializer = ExtractStudySerializer(s)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_table_columns_for_study(request, study_id):
    column_list = TableColumn.objects.filter(study_id=study_id).order_by('column_name')
    json_list=list()
    for c in column_list:
        serializer = TableColumnSerializer(c)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_columns_for_study_table(request, study_id, table_name):
    column_list = TableColumn.objects.filter(study_id=study_id, table_name=table_name).exclude(column_name='no_column').order_by('column_name')  
    json_list=list()
    for c in column_list:
        serializer = TableColumnSerializer(c)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_tables_for_study(request, study_id): # NEEDS UNIQUE!! TODO
    column_list = TableColumn.objects.filter(study_id=study_id).order_by('table_name')
    json_list=list()
    table=''
    for c in column_list:
        if (table != c.table_name) :  # are there legit unique filters in python? TODO
            serializer = TableColumnSerializer(c)
            json_list.append(serializer.data)
            table = c.table_name
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

def _clean_per_id(values_dict_list):
    #  The incoming dict has multiple values per patient_id (id), make it so we just pick the first.
    # are the still sorted here?
    out_list=[]
    id_set=set()
    # {'id': 6520016, 'from_column': 'amcod', 'from_table': 'best.ame', 'value': 'RD10'}
    for row in values_dict_list:
        if row['id'] not in id_set and row['value'] is not None:
            id_set.add(row['id'])
            out_list.append(row)

    return out_list

def _summarize_study_values(values_dict_list, column_name):
# values_dict_list is a list of row dictionaries
# TODO do on JS side like the ohdsi data?

    single_per_id_values_dict_list = _clean_per_id(values_dict_list)
    value_iterator = map((lambda x: x['value']), single_per_id_values_dict_list)
    value_list = list(value_iterator)
    value_set = set(value_list)
    clean_list = list(filter(lambda x: x!=None, value_list))
    clean_set = set(value_list)
    if len(clean_set) >= 10 and len(clean_list) >= 10 :
        # like BEST's randate and eos_dt, the values are non-numerical and can't be summarized
        # and there are too many (>10) to show the counts for each value. 
        # TODO log this?!!!
        if type(value_list[0]) != type(1) and type(value_list[0]) != type(1.0):  
            n=len(value_list)
            print("WARNING views._summarize_study_values() Too many values and wrong type to summarize for ", column_name)
            # TODO come up with a less Easter Egg like way of communicating this:
            return({'a_too':0, 'b_many':0, 'c_non_numerical':0, 'd_values':n})
        else:
            # CONTINOUS: min/avg/max
            n=0
            for v in value_set:
                v_sum = sum(map(lambda x: 1, filter(lambda x: x==v, value_list)))
                #print("views._summarize_study_values()    ", column_name, v, v_sum)
                n+=v_sum
            print("views._summarize_study_values()  sum  ", column_name, n)
            value_list.sort()
            median=value_list[int(len(value_list)/2)]
            average=0
            try:
                average=format(sum(clean_list)/n, '.2f') 
                return({'n':n,  'min':min(clean_list), 'med': median, 'avg': average, 'max': max(clean_list)})
            except Exception as ex:
                print("views._summarize_study_values() ERROR:", column_name, n)
                print('    (exc)', ex)
                print("    (cont) ", len(value_set))
                # print("    (cont) ", clean_list)
            return({'n':0,  'something':3, 'isnt':3, 'right':9, 'max':3}) # TODO stupid easter egg trick
    else:
        # DISCRETE/CATEGORIZED
        distribution_dict={}
        n=0
        for v in value_set:
            n+=sum(map(lambda x: 1, filter(lambda x: x==v, value_list)))
        for v in value_set:
            filtered = filter(lambda x: x==v, value_list)
            sum_value=sum(map(lambda x: 1, filter(lambda x: x==v, value_list)))
            #distribution_dict[v]=(sum_value/n)*100 # percentage
            distribution_dict[v]=sum_value # raw value
        return(distribution_dict)
    
@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
# TODO extend for "where clause" columns like the labs values 
def get_study_value_by_table_column(request, study_id, table_name, column_name): 
    (cursor, con) = get_cursor()
    personObj = BasePerson.factory(int(study_id))  
    person_ids = personObj.get_study_person_ids(con)
    mapping_row = { 'from_table':table_name, 'from_column':column_name }
    values =  select_values(mapping_row, personObj, person_ids, cursor)
    json_list=list()
    summary = _summarize_study_values(values, column_name)
    json_list.append(summary)
    cursor.close()
    con.close()
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json


@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_ohdsi_value_by_vocabulary_concept(request, study_id, vocabulary_id, concept_code, table_name): 

    # TODO marked for when we go beyon just picking the first value for each person
    (cursor, con) = get_cursor()
    personObj = BasePerson.factory(int(study_id))  
    # date_column_name = personObj.get_date_column_for_table(mapping['from_table'])
    id_column_name = personObj.get_id_field_name()
    person_ids = personObj.get_study_person_ids(con)
    json_list=list()
    for person_id in person_ids:
        value_row={}
        study_person_id = personObj.convert_person_id_to_study(person_id)
        value_row[id_column_name] = study_person_id
        tuples = fetch(con, table_name, person_id, vocabulary_id, concept_code)
        if (len(tuples) > 0) :
            (value_as_number, value_as_string, value_as_concept_id, date) = tuples[0]
            value_row['value_as_number']=value_as_number
            value_row['value_as_string']=value_as_string
            value_row['value_as_concept_id']=value_as_concept_id
            value_row['date']=date
            json_list.append(value_row)
        
        #else :
        #    print("no value for ", study_id, vocabulary_id, concept_code, table_name, person_id)
    cursor.close()
    con.close()
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
def get_ohdsi_person_count(request, study_id):
    persons = Person.objects.filter(study_id=study_id)
    return len(persons)
    

@api_view(['DELETE'])
def delete_ohdsi_mapping(request, study_id, from_table, from_column, from_where_clause, from_where_column):
    if (from_where_clause == '' or from_where_column == ''):
        mapping = StudyToOhdsiMapping.objects.get(
            study_id=study_id, 
            from_table=from_table,
            from_column=from_column,
            from_where_clause__isnull=True,
            from_where_column__isnull=True)
    else:
        mapping = StudyToOhdsiMapping.objects.get(
            study_id=study_id, 
            from_table=from_table,
            from_column=from_column,
            from_where_clause=from_where_clause,
            from_where_column=from_where_column)
    if (mapping):
        mapping.delete()
        json_response = JsonResponse("deleted.", safe=False, status=200) # TODO
        return(json_response) # JsonResponse application/json
    else:
        json_response = JsonResponse("no such object.", safe=False, status=404) # TODO
        return(json_response) # JsonResponse application/json

@api_view(['PUT'])
def edit_ohdsi_mapping(request, study_id, from_table, from_column, from_where_clause, from_where_column, function_name, concept_id, to_table, to_column):
    if (from_where_clause == '' or from_where_column == ''):
        mapping = StudyToOhdsiMapping.objects.get(
            study_id=study_id, 
            from_table=from_table,
            from_column=from_column,
            from_where_clause__isnull=True,
            from_where_column__isnull=True)
    else:
        mapping = StudyToOhdsiMapping.objects.get(
            study_id=study_id, 
            from_table=from_table,
            from_column=from_column,
            from_where_clause=from_where_clause,
            from_where_column=from_where_column)

    if (mapping):
        mapping.function_name=function_name
        concept_list = Concept.objects.filter(concept_id=concept_id)
        mapping.vocabulary_id=concept_list[0].vocabulary.vocabulary_id
        mapping.concept_code=concept_list[0].concept_code
        mapping.to_table=to_table
        mapping.to_column=to_column

        mapping.save()

        json_response = JsonResponse("updated.", safe=False, status=200) # TODO
        return(json_response) # JsonResponse application/json
    else:
        json_response = JsonResponse("no such object.", safe=False, status=404) # TODO
        return(json_response) # JsonResponse application/json

@api_view(['PUT'])
def put_ohdsi_mapping(request, study_id, from_table, from_column, function_name, concept_id, to_table, to_column):

    # convert from concept_id to concept_code and vocabulary_id
    concept_list = Concept.objects.filter(concept_id=concept_id)

    study_obj = Study.objects.filter(study_id=study_id)[0]
    #to_table_obj=TableColumn.objects.filter(table_name=to_table, column_name=to_column)[0]
 
    mapping = StudyToOhdsiMapping.objects.create(
        study=study_obj,
        from_table=from_table,
        from_column=from_column,
        #to_table=to_table_obj,
        function_name=function_name,
        to_table=to_table,
        to_column=to_column, 
        vocabulary_id=concept_list[0].vocabulary.vocabulary_id,
        concept_code=concept_list[0].concept_code, 
        comment=  "added by the code"
        #addl_column=
        #/addl_value= 
        #from_date_column= 
        #where_clause=
    )

    mapping.save()

    json_response = JsonResponse("inserted.", safe=False, status=200) # TODO
    return(json_response) # JsonResponse application/json

#def get_mapping_functions_for_study(request, study_id):
#    function_list = OhdsiMappingFunction.objects.filter(study_id=study_id)
#    json_list=list()
#    for f in function_list:
#        serializer = OhdsiMappingFunctionSerializer(f)
#        json_list.append(serializer.data)
#    function_list = OhdsiMappingFunction.objects.filter(study_id=0)
#    for f in function_list:
#        serializer = OhdsiMappingFunctionSerializer(f)
#        json_list.append(serializer.data)
#    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_study_to_ohdsi_mapping_functions(request, study_id):
    function_list = StudyToOhdsiMappingFunction.objects.filter(study_id=study_id)
    json_list=list()
    for f  in function_list:
        serializer = StudyToOhdsiMappingFunctionSerializer(f)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_categorization_functions(request):
    function_list = CategorizationFunctions.objects.all()
    json_list=list()
    for f  in function_list:
        serializer = CategorizationFunctionsSerializer(f)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_mapping_functions(request, study_id):
    #function_list = MappingFunctions.objects.filter(study_id=study_id).filter(study_id=0) # AND
    function_list = MappingFunctions.objects.filter(Q(study_id=study_id) | Q(study_id=0)) # OR
    json_list=list()
    for f  in function_list:
        serializer = MappingFunctionsSerializer(f)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_mapping_function_by_name(request, name):
    function_list = MappingFunctions.objects.filter(name=name)
    json_list=list()
    for f  in function_list:
        serializer = MappingFunctionsSerializer(f)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def study_to_ohdsi_mapping_function(request): 
#, study_id, from_table, from_column, vocabulary_id, concept_code, function_name, from_int, from_value, to_concept, conversion_factor):
# use (study_id, from_table, from_column, vocabulary_id, concept_code) in the URL to live up to REST dogma
    if request.method == 'POST':
        form = StudyToOhdsiMappingFunctionForm(request.POST)
        #if form.isValid():
        form.save()
        #return HttpResponseRedirect(reverse('app_name:url_name'))
        return HttpResponse('done')
    else:
        form = StudyToOhdsiMappingFunctionForm()

    return render(request, 'study_to_ohdsi_mapping_function.html', { 'form' : StudyToOhdsiMappingFunctionForm(), })

# ------ non-ORM access into Study tables ----


class CategorizationFunctionsSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)

class MappingFunctionsSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)

class StudyValueSerializer(serializers.Serializer):
        id = serializers.CharField(max_length=100)
        value = serializers.CharField(max_length=100)
        from_table = serializers.CharField(max_length=100)
        from_column = serializers.CharField(max_length=100)
        loaded = serializers.CharField(max_length=100)
        migrated = serializers.CharField(max_length=100)
        calculated = serializers.CharField(max_length=100)
        

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_study_values(request, study_id, table_name, column_name) :
    # FETCH the hard way from a dynamically created query

    (value_cursor, con) = get_cursor()

    personObj = BasePerson.factory(int(study_id))  
    print("DEBUG", study_id)
    print("DEBUG", personObj)
    person_ids = personObj.get_study_person_ids(con)[:10]
    #def select_values(mapping, personObj,  value_cursor) :
    #""" Selects values from study tables.
    #    Mapping has keys from_table, from_column, optionally from_where_clause, from_where_column, has_date
    #    Returns value_rows with fields id_column_name, from_column, optionally date_value, 
    #mapping = { 'from_table' : table_name, 'from_column' : column_name , 'from_where_clause':None, 'has_date':None, 'from_where_column':None}
    mapping = { 'from_table' : table_name, 'from_column' : column_name }
    rows = select_values(mapping, personObj, person_ids, value_cursor)
    value_cursor.close()
    con.close()
    
    # SERIALIZE
    json_list=list()
    for row in rows:
        print("DEBUG: get_study_values() ROW", row)
        serializer = StudyValueSerializer(row)
        serialized = serializer.data
        json_list.append(serialized)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json


@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_mapped_columns_for_study(request, study_id):
    """ returns concepts that have been used in mappings for any vocabulary for the named study
    """
    json_list=list()
    if (study_id != None) :
        #mapping_list = StudyToOhdsiMapping.objects.filter(study_id=study_id).order_by('from_table', 'from_column')
        mapping_list = StudyToOhdsiMapping.objects.filter(study_id=study_id).order_by('vocabulary_id')
        for m in mapping_list:
            serializer = StudyToOhdsiMappingSerializer(m)
            json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_mapped_columns_for_study_and_table(request, study_id, table):
    """ returns concepts that have been used in mappings for any vocabulary for the named study
    """
    json_list=list()
    if (study_id != None) :
        mapping_list = StudyToOhdsiMapping.objects\
            .filter(study_id=study_id)\
            .filter(from_table=table)\
            .order_by('vocabulary_id')
            #.order_by('from_table', 'from_column')

        for m in mapping_list:
            serializer = StudyToOhdsiMappingSerializer(m)
            json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json


## -- ORM, plain json serialized response from a dictionary --

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_concepts_from_study(request, study_id, vocab_id):
    concept_list = Concept.objects.filter(vocabulary_id=vocab_id, concept_name__icontains=string)

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_extract_mapping_list(request, extract_study_id):
    # extraction:  extract_study_id, function_name, long_name, rule_id, from_vocabulary_id, from_concept_code,
    # No Serializer used, just brings over every field in the Model. TODO?
    extraction_mappings=CategorizationFunctionMetadata.objects.filter(extract_study_id=extract_study_id).order_by('from_vocabulary_id', 'from_concept_code')

    json_list=list()
    big_json_string=''
    for mapping_model in extraction_mappings:
        mapping_dict = model_to_dict(mapping_model)
        json_list.append(mapping_dict)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_extract_mapping_function(request, extract_study_id, function_name, long_name, rule_id):
    # key:  extract_study_id, function_name, long_name, rule_id
    # No Serializer used, just brings over every field in the Model. TODO?
    extraction_mappings=CategorizationFunctionMetadata.objects.filter(extract_study_id=extract_study_id).filter(function_name=function_name).filter(long_name=long_name).filter(rule_id=rule_id)

    json_list=list()
    big_json_string=''
    for mapping_model in extraction_mappings:
        mapping_dict = model_to_dict(mapping_model)
        json_list.append(mapping_dict)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_categorization_function_parameters(request, extract_study_id, function_name, long_name) :
    extraction_parameters=CategorizationFunctionParameters.objects.filter(extract_study_id=extract_study_id).filter(function_name=function_name).filter(long_name=long_name)

    json_list=list()
    big_json_string=''
    for parameter_row in extraction_parameters:
        mapping_dict = model_to_dict(parameter_row)
        json_list.append(mapping_dict)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json
    


@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_used_concepts_for_vocabulary(request, vocabulary_id):
    """ Returns concepts that have been used in mappings for any study for the named vocabulary
        Has a hand-rolled serialization so we can add the concept_name (TBD TODO) to what is
        basically a row from the study_to_ohdsi_mapping....also uniquify's the list
    """
    mapping_list = StudyToOhdsiMapping.objects.filter(vocabulary_id=vocabulary_id)
    used_concepts_set=set()
    concepts_list=list()
    json_list=list()
    keys_list=['vocabulary_id', 'concept_code', 'to_table', 'to_column', 'from_where_clause', 'from_where_column']
    for mapping_model in mapping_list:
        mapping_dict = model_to_dict(mapping_model)
        concept_dict=dict()
        key = (mapping_dict['vocabulary_id'], mapping_dict['concept_code'])
        if (key not in used_concepts_set):
            for key2 in keys_list:
                concept_dict[key2]=mapping_dict[key2]
            concept_dict['concept_name']='tbd'
            used_concepts_set.add(key)
            json_list.append(concept_dict)

    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def get_common_vocabularies(request):
    return(JsonResponse(['ATC', 'LOINC', 'SNOMED', 'RxNorm', 'UCD.Kao'], safe=False, status=200))

@api_view(['GET'])
def get_study(request, study_name):
    study_list = Study.objects.filter(study_name=study_name)
    json_list=list()
    for s in study_list:
        serializer = StudySerializer(s)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

@api_view(['GET'])
def get_study_by_id(request, study_id):
    study_list = Study.objects.filter(study_id=study_id)
    json_list=list()
    for s in study_list:
        serializer = StudySerializer(s)
        json_list.append(serializer.data)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

# ---- NON-REST ----------

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def report_end_to_end(request):
    context = {}
    return render(request, 'reports/report_end_to_end.html', context)

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def test_paradigm_csv(request):
    context = {}
    return(_run_script(request, '../bin/test_paradigm_csv.sh'))



@api_view(['GET'])
def create_db(request, dbname):
    print("CREATE DB:" + dbname)
    completed_process = subprocess.run(["createdb " + dbname], shell=True, check=False)
    if (completed_process.returncode == 0): 
        return(JsonResponse(completed_process.stdout, safe=False, status=200)) # JsonResponse application/json
    else:
        return(JsonResponse(completed_process.stderr, safe=False, status=500)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def echo_string(request, input):
    output = subprocess.getoutput("echo " + input)
    my_ds = { 'a':"0", 'b':output, 'c':"1" }
    print(my_ds)
    x = JsonResponse(my_ds, safe=False, status=200)
    print(x)
    return(x)
      
@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def load_ohdsi(request):
    dbname = os.environ.get("PGDATABASE")
    print("views:load_ohdsi(): " + dbname)
    return(_run_script(request, 'ohdsi.sh ' + dbname))

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def load_studies(request):
    returncode = HeartData.load_studies.main()
    if (returncode): 
        message = 'load_studies succeeded:' + str(returncode)
        print(message)
        return(JsonResponse(message, safe=False, status=200)) # JsonResponse application/json
    else:
        message = 'load_studies failed:' + str(returncode)
        print(message)
        return(JsonResponse(message, safe=False, status=500)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def load_mappings(request):
    dbname = os.environ.get("PGDATABASE")
    if not dbname :
        print("Set the PGDATABASE variable name. It's null.")
        # TODO push this message out the UI so you get more than "FAILED"
        exit(1)
    print("views:load_mappings(): " + dbname)
    return(_run_script(request, 'load_mappings.sh ' + dbname))

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def run_migrate(request, study_name):
    dbname = os.environ.get("PGDATABASE")
    username = os.environ.get("PGUSER")
    try:
        migrate.main(dbname, username, study_name)
        return(JsonResponse("migrate succeeded", safe=False, status=200)) # JsonResponse application/json
    except Exception as e:
        print("exception in migrate:" + str(e))
        return(JsonResponse("migrate failed:" + str(e), safe=False, status=500)) # JsonResponse application/json

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def run_calculate(request,  study_name):
    dbname = os.environ.get("PGDATABASE")
    username = os.environ.get("PGUSER")
    try:
        calculate.main(dbname, username, study_name)
        return(JsonResponse("calculate succeeded", safe=False, status=200)) # JsonResponse application/json
    except Exception as e:
        print("exception in calculate:" + str(e))
        response = JsonResponse("calculate failed:" + str(e), safe=False, status=500) # JsonResponse application/json
        return(response)

@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def run_extract(request, study_name, extract_cfg_id):
    dbname = os.environ.get("PGDATABASE")
    username = os.environ.get("PGUSER")
    try:
        extract.main(dbname, username, study_name, extract_cfg_id)
        return(JsonResponse("extract succeeded", safe=False, status=200)) # JsonResponse application/json
    except Exception as e:
        print("exception in extract:" + str(e))
        return(JsonResponse("extract failed: " + str(e), safe=False, status=500)) # JsonResponse application/json

def _run_script(request, script_name): # 
    completed_process = subprocess.run("../bin/" + script_name, shell=True, check=False)
    if (completed_process.returncode == 0): 
        return(JsonResponse(script_name + ' success ' + str(completed_process.stdout), safe=False, status=200)) # JsonResponse application/json
    else:
        return(JsonResponse(script_name + ' failed: ' + str(completed_process.stdout), safe=False, status=500)) # JsonResponse application/json



@api_view(['GET'])
#@authentication_classes((BasicAuthentication, SessionAuthentication, TokenAuthentication))
#@permission_classes((IsAuthenticated,))
def vocabulary_like(request, vocab_id, string):
    concept_list = Concept.objects.filter(vocabulary_id=vocab_id, concept_name__icontains=string)

    # RAW
    #retval=''
    #if (len(concept_list) == 0):
    #    retval="(empty result set)"
    #for c in concept_list:
    #   retval += str(c.concept_id) + ', ' + c.concept_code +  ', "' + c.concept_name + '",<br> '
    #return HttpResponse('Lookup in %s for string "%s" found:<br> %s' % (vocab_id, string, retval))

    # via TEMPLATE
    context =  { 'concept_list': concept_list,
              'vocab_id': vocab_id,
              'string': string,
            }
    return render(request, 'ui/vocabulary_like.html', context)

