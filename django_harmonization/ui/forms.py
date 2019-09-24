from django.forms import ModelForm
from ui.models import StudyMappingArguments
class StudyMappingArgumentsForm(ModelForm):
    class Meta:
        model = StudyMappingArguments
        fields = (
            'study_id', 'from_table', 'from_column', 
            'function_name',
            'from_where_clause', 'from_where_column',
            'mapped_string', 'mapped_number', 'mapped_concept_vocabulary_id', 'mapped_concept_code',
            'transform_factor', 'transform_shift',
            'to_concept_vocabulary_id', 'to_concept_code')

            #'from_int', 'from_value', 'to_concept', 'conversion_factor',
            #'vocabulary_id', 'concept_code', 'from_int', 'from_value', 'to_concept', 'conversion_factor')
###id

