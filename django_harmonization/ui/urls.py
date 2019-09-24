from django.conf import settings
from django.conf.urls import url
#from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from ui import views
from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [

    # AUTH 
    url(r'^login/$', 
        auth_views.LoginView.as_view(),  name='login'),
    url(r'^logout/$', 
        auth_views.LogoutView.as_view(),  name='logout'),
    url(r'^admin/', 
        admin.site.urls),

    # CONCEPT
    url(r'^get_concepts_like/(?P<vocab_id>[\w.]+)/(?P<string>[\w%\s]+)/(?P<mapped>true|false)/(?P<extract>true|false)/$', 
        views.get_concepts_like, name='get_concepts_like'),
    url(r'^get_concept_by_id/(?P<concept_id>\d+)/$', 
        views.get_concept_by_id, name='get_concept_by_id'),
    url(r'^get_concept_by_vocab_and_concept_code/(?P<vocabulary_id>[.\w]+)/(?P<concept_code>[-\w]+)/$', 
        views.get_concept_by_vocab_and_concept_code, name='get_concept_by_vocab_and_concept_code'),

    # OTHER
    url(r'^get_common_vocabularies/$', 
        views.get_common_vocabularies, name='get_common_vocabularies'),
    url(r'^get_used_concepts_for_vocabulary/(?P<vocabulary_id>[\w.]+)/$', 
        views.get_used_concepts_for_vocabulary, name='get_used_concepts_for_vocabulary'),

    # MAPPINGS
    # edit_table_mapping_function.js, function_choice.js, show_study_metrics.js, show_table_mappings.js, source_table_column.js
    url(r'^get_study_to_ohdsi_mapping_functions/(?P<study_id>\w+)/$', #  354
        views.get_study_to_ohdsi_mapping_functions, name='get_study_to_ohdsi_mapping_functions'),
    url(r'^get_mapping_for_study/(?P<study_id>\d+)/$',  # 92
        views.get_mapping_for_study, name='get_mapping_for_study'),
    url(r'^get_mapped_columns_for_study/(?P<study_id>\w+)/$',   # 466
        views.get_mapped_columns_for_study, name='get_mapped__columns_for_study'),
    url(r'^get_study_mapping_arguments/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)/(?P<function_name>\w+)/(?P<from_where_clause>\w*)/(?P<from_where_column>\w*)/$', 
        views.get_study_mapping_arguments, name='get_study_mapping_arguments'),
    url(r'^get_study_mapping_arguments/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)/(?P<function_name>\w+)/$', 
        views.get_study_mapping_arguments, name='get_study_mapping_arguments'),

    # MAPPINGS CRUD a single row:
    url(r'^put_ohdsi_mapping/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)/(?P<function_name>\w+)/(?P<concept_id>\d+)/(?P<to_table>\w+)/(?P<to_column>[\w_]+)/$', 
        #(?P<from_where_clause>\w*)/(?P<from_where_column>\w*)/
        views.put_ohdsi_mapping, name='put_ohdsi_mapping'),
    url(r'^delete_ohdsi_mapping/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)/(?P<from_where_clause>\w*)/(?P<from_where_column>\w*)/$', 
        views.delete_ohdsi_mapping, name='delete_ohdsi_mapping'),
    # yeah I know:REST says put is either insert or update...
    url(r'^edit_ohdsi_mapping/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)/(?P<from_where_clause>\w*)/(?P<from_where_column>\w*)/(?P<function_name>\w+)/(?P<concept_id>\d+)/(?P<to_table>\w+)/(?P<to_column>[\w_]+)/$', 
        views.edit_ohdsi_mapping, name='edit_ohdsi_mapping'),
    url(r'^edit_ohdsi_mapping/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)/(?P<function_name>\w+)/(?P<concept_id>\d+)/(?P<to_table>\w+)/(?P<to_column>[\w_]+)/$', 
        views.edit_ohdsi_mapping, name='edit_ohdsi_mapping'),

    # same ?
    # show_study_metrics.js, show_table_mappings.js, source_table_column.js
    url(r'^get_mapping_for_study_table/(?P<study_id>\d+)/(?P<table_name>[\w._]+)/$',  # 104
        views.get_mapping_for_study_table, name='get_mapping_for_study_table'),
    url(r'^get_mapped_columns_for_study_and_table/(?P<study_id>\w+)/(?P<table>[\w.]+)/$',  # 478
        views.get_mapped_columns_for_study_and_table, name='get_mapped__columns_for_study_and_table'),

    url(r'^get_mapping_for_study_table_column/(?P<study_id>\d+)/(?P<table_name>[\w._]+)/(?P<column_name>[\w._]+)/$', 
        views.get_mapping_for_study_table_column, name='get_mapping_for_study_table_column'),



    # STUDY
    url(r'^get_all_studies/$', 
        views.get_all_studies, name='get_all_studies'),
    url(r'^get_study/(?P<study_name>\w+)/$', 
        views.get_study, name='get_study'),
    url(r'^get_study_by_id/(?P<study_id>\w+)/$', 
        views.get_study_by_id, name='get_study_by_id'),

    # EXTRACT_STUDY
    url(r'^get_extract_study_list/$',  
        views.get_extract_study_list, name='get_extract_study_list'),

    # CATEGORIZATION_FUNCTION_METADATA
    url(r'^get_extract_mapping_list/(?P<extract_study_id>\d+)/$',  
        views.get_extract_mapping_list, name='get_extract_mapping_list'),
    url(r'^get_extract_mapping_function/(?P<extract_study_id>\d+)/(?P<function_name>\w+)/(?P<long_name>[\w\s]+)/(?P<rule_id>\d+)/$',  
        views.get_extract_mapping_function, name='get_extract_mapping_function'),

    # TABLE_COLUMN
    url(r'^get_table_columns_for_study/(?P<study_id>\w+)/$', 
        views.get_table_columns_for_study, name='get_table_columns_for_study'),
    url(r'^get_tables_for_study/(?P<study_id>\d+)/$', 
        views.get_tables_for_study, name='get_tables_for_study'),
    url(r'^get_columns_for_study_table/(?P<study_id>\d+)/(?P<table_name>[\w._]+)/$', 
        views.get_columns_for_study_table, name='get_columns_for_study_table'),
    
    # CATEGORIZATION_FUNCTIONS
    url(r'^get_categorization_functions/$', 
        views.get_categorization_functions, name='get_categorization_functions'),
    url(r'^get_categorization_function_parameters/(?P<extract_study_id>\d+)/(?P<function_name>[\w\s]+)/(?P<long_name>[\w\s]+)/$', 
        views.get_categorization_function_parameters, name='get_categorization_function_parameters'),

    # MAPPING_FUNCTIONS
    url(r'^get_mapping_functions/(?P<study_id>\w+)/$', 
        views.get_mapping_functions, name='get_mapping_functions'),
    url(r'^get_mapping_function_by_name/(?P<name>\w+)/$',
        views.get_mapping_function_by_name, name='get_mapping_function_by_name'),


    # STUDY TABLES' values
    url(r'^get_study_value_by_table_column/(?P<study_id>\d+)/(?P<table_name>[\w._]+)/(?P<column_name>[\w._-]+)/$', 
        views.get_study_value_by_table_column, name='get_study_value_by_table_column'),
    url(r'^get_study_values/(?P<study_id>\d+)/(?P<table_name>[\w._]+)/(?P<column_name>[\w._]+)/$', 
        views.get_study_values, name='get_study_values'),

    # OHDSI VALUE
    url(r'^get_ohdsi_value_by_vocabulary_concept/(?P<study_id>\d+)/(?P<vocabulary_id>[\w._-]+)/(?P<concept_code>[\w.-]+)/(?P<table_name>[\w.]+)/$', 
        views.get_ohdsi_value_by_vocabulary_concept, name='get_ohdsi_value_by_vocabulary_concept'),

    # DEBUG
    url(r'^echo_string/(?P<input>[\w._]+)/$', 
        views.echo_string, name='echo_string'),

    # PIPELINE
    url(r'^create_db/(?P<dbname>[\w._]+)/$', 
        views.create_db, name='create_db'),
    url(r'^load_ohdsi/$', 
        views.load_ohdsi, name='load_ohdsi'),
    url(r'^load_studies/$',     
        views.load_studies, name='load_studies'),
    url(r'^load_mappings/$', 
        views.load_mappings, name='load_mappings'),
    url(r'^run_migrate/(?P<study_name>\w+)/$', 
        views.run_migrate, name='run_migrate'),
    url(r'^run_calculate/(?P<study_name>\w+)/$',        
        views.run_calculate, name='run_calculate'),
    url(r'^run_extract/(?P<study_name>\w+)/(?P<extract_cfg_id>\d+)/$', 
        views.run_extract, name='run_extract'),

    # REPORTS
    url(r'^report_end_to_end/$', 
        views.report_end_to_end, name='report_end_to_end'),
    url(r'^test_paradigm_csv/$', 
        views.test_paradigm_csv, name='test_paradigm_csv'),

    # Deprecated, see spreadsheet_params
    url(r'^spreadsheet_csv/$', 
        views.spreadsheet_csv, name='spreadsheet_csv'),
    # Deprecated, see spreadsheet_params
    url(r'^spreadsheet_txt/$', 
        views.spreadsheet_txt, name='spreadsheet_txt'),
    # Deprecated, see spreadsheet_params
    url(r'^coverage_grid/$', 
        views.coverage_grid, name='coverage_grid'),

    url(r'^spreadsheet_params/(?P<report_type>\w+)/(?P<extract_study_id>\d+)/(?P<detail>\w+)/(?P<unused>\w+)/$', 
        views.spreadsheet_params, name='spreadsheet_params'),
    url(r'^spreadsheet_params_html/(?P<report_type>\w+)/(?P<extract_study_id>\d+)/(?P<detail>\w+)/(?P<unused>\w+)/$', 
        views.spreadsheet_params_html, name='spreadsheet_params_html'),

    # STATIC
    url(r'^study_harmonization/$', 
        TemplateView.as_view(template_name='study_harmonization.html'), name='study_harmonization'),
        #views.study_harmonization, name='study_harmonization'),
    url(r'^harmonization_sheet_import/$', 
        TemplateView.as_view(template_name='harmonization_sheet_import.html'), name='harmonization_sheet_import'),
    url(r'^harmonization_sheet_export/$', 
        TemplateView.as_view(template_name='harmonization_sheet_export.html'), name='harmonization_sheet_export'),
    url(r'^index.html$', 
        TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^mapping.html$', 
        TemplateView.as_view(template_name='mapping.html'), name='mapping'),
    url(r'^new_database.html$', 
        TemplateView.as_view(template_name='new_database.html'), name='new_database'),
    url(r'^pipeline.html$', 
        TemplateView.as_view(template_name='pipeline.html'), name='pipeline'),
    url(r'^peax.html$', 
        TemplateView.as_view(template_name='peax.html'), name='peax'),
    url(r'^rstudio.html$', 
        TemplateView.as_view(template_name='rstudio.html'), name='rstudio'),
    url(r'^reports.html$', 
        TemplateView.as_view(template_name='reports.html'), name='reports'),

    url(r'^data_extraction.html$', 
        TemplateView.as_view(template_name='data_extraction.html'), name='data_extraction'),
    url(r'^create_factor_function.html$', 
        TemplateView.as_view(template_name='create_factor_function.html'), name='create_factor_function'),
    url(r'^create_mapping_function.html$', 
        TemplateView.as_view(template_name='create_mapping_function.html'), name='create_mapping_function'),

    url(r'^function_choice.html$', 
        TemplateView.as_view(template_name='function_choice.html'), name='function_choice'),

    url(r'^study_choice.html$', 
        TemplateView.as_view(template_name='study_choice.html'), name='study_choice'),
    url(r'^show_table_mappings.html$', 
        TemplateView.as_view(template_name='show_table_mappings.html'), name='show_table_mappings'),
    url(r'^edit_table_mapping.html$', 
        TemplateView.as_view(template_name='edit_table_mapping.html'), name='edit_table_mapping'),
    url(r'^edit_table_mapping_function_arg.html$', 
        TemplateView.as_view(template_name='edit_table_mapping_function_arg.html'), name='edit_table_mapping_function_arg'),

    url(r'^extract_study_choice.html$', 
        TemplateView.as_view(template_name='extract_study_choice.html'), name='extract_study_choice'),
    url(r'^show_extract_mappings.html$', 
        TemplateView.as_view(template_name='show_extract_mappings.html'), name='show_extract_mappings'),
    url(r'^edit_extract_mapping.html$', 
        TemplateView.as_view(template_name='edit_extract_mappings.html'), name='edit_extract_mapping'),

    url(r'^submit_mapping.html$', 
        TemplateView.as_view(template_name='submit_mapping.html'), name='submit_mapping'),

    url(r'^destination_concept.html$', 
        TemplateView.as_view(template_name='destination_concept.html'), name='destination_concept'),

]
