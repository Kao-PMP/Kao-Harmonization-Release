from django.forms import ModelForm
from ui.models import StudyToOhdsiMappingFunction
class StudyToOhdsiMappingFunctionForm(ModelForm):
    class Meta:
        model = StudyToOhdsiMappingFunction
        fields = ('study_id', 'from_table', 'from_column', 'function_name', 'vocabulary_id', 'concept_code', 'from_int', 'from_value', 'to_concept', 'conversion_factor')

