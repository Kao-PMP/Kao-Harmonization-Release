from django.db import models


# for api-token-auth
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


# Most tables are NOT managed, TableColumn is

#class AttributeDefinition(models.Model):
#    attribute_definition_id = models.IntegerField(primary_key=True)
#    attribute_name = models.CharField(max_length=255)
#    attribute_description = models.TextField(blank=True, null=True)
#    attribute_type_concept_id = models.IntegerField()
#    attribute_syntax = models.TextField(blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'attribute_definition'
#

#class CareSite(models.Model):
#    care_site_id = models.IntegerField(primary_key=True)
#    care_site_name = models.CharField(max_length=255, blank=True, null=True)
#    place_of_service_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    location = models.ForeignKey('Location', models.DO_NOTHING, blank=True, null=True)
#    care_site_source_value = models.CharField(max_length=50, blank=True, null=True)
#    place_of_service_source_value = models.CharField(max_length=50, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'care_site'


class CategorizationFunctions(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'categorization_functions'
        unique_together = (('name'),)

class MappingFunctions(models.Model):
    name = models.CharField(max_length=100)
    study_id = models.IntegerField(blank=True, null=True)
        
    class Meta:
        managed = False
        db_table = 'mapping_function'
        unique_together = (('name'),)

class CategorizationFunctionMetadata(models.Model):
    extract_study = models.ForeignKey('ExtractStudy', models.DO_NOTHING, primary_key=True)
    function_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=100)
    rule_id = models.CharField(max_length=20)
    from_vocabulary_id = models.CharField(max_length=100)
    from_concept_code = models.CharField(max_length=100)
    comment = models.CharField(max_length=256, blank=True, null=True)
    from_table = models.CharField(max_length=20, blank=True, null=True)
    short_name = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorization_function_metadata'
        unique_together = (('extract_study', 'function_name', 'long_name', 'rule_id'), ('extract_study', 'function_name', 'long_name', 'rule_id'),)


class CategorizationFunctionParameters(models.Model):
    extract_study = models.ForeignKey('ExtractStudy', models.DO_NOTHING, primary_key=True)
    function_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=100)
    rule_id = models.CharField(max_length=20)
    value_limit = models.FloatField(blank=True, null=True)
    rank = models.IntegerField()
    from_string = models.CharField(max_length=20, blank=True, null=True)
    from_concept_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorization_function_parameters'
        unique_together = (('extract_study', 'function_name', 'long_name', 'rule_id', 'rank'),)


class CategorizationFunctionQualifiers(models.Model):
    extract_study = models.ForeignKey('ExtractStudy', models.DO_NOTHING, primary_key=True)
    function_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=100)
    rule_id = models.CharField(max_length=20)
    vocabulary_id = models.CharField(max_length=100)
    concept_code = models.CharField(max_length=100)
    value_vocabulary_id = models.CharField(max_length=100, blank=True, null=True)
    value_as_string = models.CharField(max_length=100, blank=True, null=True)
    value_as_number = models.IntegerField(blank=True, null=True)
    value_as_concept_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorization_function_qualifiers'
        unique_together = (('extract_study', 'function_name', 'long_name', 'rule_id', 'vocabulary_id', 'concept_code'),)


class CategorizationFunctionTable(models.Model):
    extract_study = models.ForeignKey('ExtractStudy', models.DO_NOTHING, primary_key=True)
    function_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=100)
    from_table = models.ForeignKey('TableColumn', models.DO_NOTHING, db_column='from_table', blank=True, null=True)
    from_column = models.CharField(max_length=100, blank=True, null=True)
    from_vocabulary = models.ForeignKey('VocabularyConcept', models.DO_NOTHING, blank=True, null=True)
    from_concept_code = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorization_function_table'
        unique_together = (('extract_study', 'function_name', 'long_name'),)


#class CdmSource(models.Model):
#    cdm_source_name = models.CharField(max_length=255)
#    cdm_source_abbreviation = models.CharField(max_length=25, blank=True, null=True)
#    cdm_holder = models.CharField(max_length=255, blank=True, null=True)
#    source_description = models.TextField(blank=True, null=True)
#    source_documentation_reference = models.CharField(max_length=255, blank=True, null=True)
#    cdm_etl_reference = models.CharField(max_length=255, blank=True, null=True)
#    source_release_date = models.DateField(blank=True, null=True)
#    cdm_release_date = models.DateField(blank=True, null=True)
#    cdm_version = models.CharField(max_length=10, blank=True, null=True)
#    vocabulary_version = models.CharField(max_length=20, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'cdm_source'


#class Cohort(models.Model):
#    cohort_definition = models.ForeignKey('CohortDefinition', models.DO_NOTHING, primary_key=True)
#    subject_id = models.IntegerField()
#    cohort_start_date = models.DateField()
#    cohort_end_date = models.DateField()
#
#    class Meta:
#        managed = False
#        db_table = 'cohort'
#        unique_together = (('cohort_definition', 'subject_id', 'cohort_start_date', 'cohort_end_date'),)


#class CohortAttribute(models.Model):
#    cohort_definition = models.ForeignKey('CohortDefinition', models.DO_NOTHING, primary_key=True)
#    cohort_start_date = models.DateField()
#    cohort_end_date = models.DateField()
#    subject_id = models.IntegerField()
#    attribute_definition = models.ForeignKey(AttributeDefinition, models.DO_NOTHING)
#    value_as_number = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    value_as_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'cohort_attribute'
#        unique_together = (('cohort_definition', 'subject_id', 'cohort_start_date', 'cohort_end_date', 'attribute_definition'),)


#class CohortDefinition(models.Model):
#    cohort_definition_id = models.IntegerField(primary_key=True)
#    cohort_definition_name = models.CharField(max_length=255)
#    cohort_definition_description = models.TextField(blank=True, null=True)
#    definition_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    cohort_definition_syntax = models.TextField(blank=True, null=True)
#    subject_concept_id = models.IntegerField()
#    cohort_initiation_date = models.DateField(blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'cohort_definition'


class Concept(models.Model):
    concept_id = models.IntegerField(primary_key=True)
    concept_name = models.CharField(max_length=255)
    domain = models.ForeignKey('Domain', models.DO_NOTHING)
    vocabulary = models.ForeignKey('Vocabulary', models.DO_NOTHING)
    concept_class = models.ForeignKey('ConceptClass', models.DO_NOTHING)
    standard_concept = models.CharField(max_length=1, blank=True, null=True)
    concept_code = models.CharField(max_length=50)
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'concept'


class ConceptAncestor(models.Model):
    ancestor_concept_id = models.IntegerField(primary_key=True)
    descendant_concept_id = models.IntegerField()
    min_levels_of_separation = models.IntegerField()
    max_levels_of_separation = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'concept_ancestor'
        unique_together = (('ancestor_concept_id', 'descendant_concept_id'),)


class ConceptClass(models.Model):
    concept_class_id = models.CharField(primary_key=True, max_length=20)
    concept_class_name = models.CharField(max_length=255)
    concept_class_concept = models.ForeignKey(Concept, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'concept_class'


class ConceptRelationship(models.Model):
    concept_id_1 = models.IntegerField(primary_key=True)
    concept_id_2 = models.IntegerField()
    relationship = models.ForeignKey('Relationship', models.DO_NOTHING)
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'concept_relationship'
        unique_together = (('concept_id_1', 'concept_id_2', 'relationship'),)


class ConceptSynonym(models.Model):
    concept = models.ForeignKey(Concept, models.DO_NOTHING)
    concept_synonym_name = models.CharField(max_length=1000)
    language_concept_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'concept_synonym'

#
#class ConditionEra(models.Model):
#    condition_era_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    condition_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    condition_era_start_date = models.DateField()
#    condition_era_end_date = models.DateField()
#    condition_occurrence_count = models.IntegerField(blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'condition_era'


#class ConditionOccurrence(models.Model):
#    condition_occurrence_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    condition_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    condition_start_date = models.DateField()
#    condition_start_datetime = models.DateTimeField()
#    condition_end_date = models.DateField(blank=True, null=True)
#    condition_end_datetime = models.DateTimeField(blank=True, null=True)
#    condition_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    stop_reason = models.CharField(max_length=20, blank=True, null=True)
#    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
#    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
#    condition_source_value = models.CharField(max_length=50, blank=True, null=True)
#    condition_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    condition_status_source_value = models.CharField(max_length=50, blank=True, null=True)
#    condition_status_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'condition_occurrence'
#

#class Cost(models.Model):
#    cost_id = models.IntegerField(primary_key=True)
#    cost_event_id = models.IntegerField()
#    cost_domain_id = models.CharField(max_length=20)
#    cost_type_concept_id = models.IntegerField()
#    currency_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    total_charge = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    total_cost = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    total_paid = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_by_payer = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_by_patient = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_patient_copay = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_patient_coinsurance = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_patient_deductible = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_by_primary = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_ingredient_cost = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    paid_dispensing_fee = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    payer_plan_period = models.ForeignKey('PayerPlanPeriod', models.DO_NOTHING, blank=True, null=True)
#    amount_allowed = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    revenue_code_concept_id = models.IntegerField(blank=True, null=True)
#    reveue_code_source_value = models.CharField(max_length=50, blank=True, null=True)
#    drg_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    drg_source_value = models.CharField(max_length=3, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'cost'


class Death(models.Model):
    person = models.ForeignKey('Person', models.DO_NOTHING, primary_key=True)
    death_date = models.DateField()
    death_datetime = models.DateTimeField(blank=True, null=True)
    death_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'death_type_concept')
    cause_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'cause_concept')
    cause_source_value = models.CharField(max_length=50, blank=True, null=True)
    cause_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'cause_source_concept')

    class Meta:
        managed = False
        db_table = 'death'


#class DeviceExposure(models.Model):
#    device_exposure_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    device_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    device_exposure_start_date = models.DateField()
#    device_exposure_start_datetime = models.DateTimeField()
#    device_exposure_end_date = models.DateField(blank=True, null=True)
#    device_exposure_end_datetime = models.DateTimeField(blank=True, null=True)
#    device_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    unique_device_id = models.CharField(max_length=50, blank=True, null=True)
#    quantity = models.IntegerField(blank=True, null=True)
#    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
#    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
#    device_source_value = models.CharField(max_length=100, blank=True, null=True)
#    device_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'device_exposure'


class Domain(models.Model):
    domain_id = models.CharField(primary_key=True, max_length=20)
    domain_name = models.CharField(max_length=255)
    domain_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'domain_concept')

    class Meta:
        managed = False
        db_table = 'domain'


#class DoseEra(models.Model):
#    dose_era_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    drug_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    unit_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    dose_value = models.DecimalField(max_digits=65535, decimal_places=65535)
#    dose_era_start_date = models.DateField()
#    dose_era_end_date = models.DateField()
#
#    class Meta:
#        managed = False
#        db_table = 'dose_era'
#
#
#class DrugEra(models.Model):
#    drug_era_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    drug_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    drug_era_start_date = models.DateField()
#    drug_era_end_date = models.DateField()
#    drug_exposure_count = models.IntegerField(blank=True, null=True)
#    gap_days = models.IntegerField(blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'drug_era'
#
#
#class DrugExposure(models.Model):
#    drug_exposure_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    drug_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    drug_exposure_start_date = models.DateField()
#    drug_exposure_start_datetime = models.DateTimeField()
#    drug_exposure_end_date = models.DateField()
#    drug_exposure_end_datetime = models.DateTimeField(blank=True, null=True)
#    verbatim_end_date = models.DateField(blank=True, null=True)
#    drug_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    stop_reason = models.CharField(max_length=20, blank=True, null=True)
#    refills = models.IntegerField(blank=True, null=True)
#    quantity = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    days_supply = models.IntegerField(blank=True, null=True)
#    sig = models.TextField(blank=True, null=True)
#    route_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    lot_number = models.CharField(max_length=50, blank=True, null=True)
#    provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
#    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
#    drug_source_value = models.CharField(max_length=50, blank=True, null=True)
#    drug_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    route_source_value = models.CharField(max_length=50, blank=True, null=True)
#    dose_unit_source_value = models.CharField(max_length=50, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'drug_exposure'
#
#
#class DrugStrength(models.Model):
#    drug_concept = models.ForeignKey(Concept, models.DO_NOTHING, primary_key=True)
#    ingredient_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    amount_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    amount_unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    numerator_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    numerator_unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    denominator_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    denominator_unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    box_size = models.IntegerField(blank=True, null=True)
#    valid_start_date = models.DateField()
#    valid_end_date = models.DateField()
#    invalid_reason = models.CharField(max_length=1, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'drug_strength'
#        unique_together = (('drug_concept', 'ingredient_concept'),)
#

class EventsMapping(models.Model):
    study = models.ForeignKey('Study', models.DO_NOTHING, primary_key=True)
    from_table = models.ForeignKey('TableColumn', models.DO_NOTHING, db_column='from_table', related_name = 'from_table')
    from_column = models.CharField(max_length=50)
    to_table = models.ForeignKey('TableColumn', models.DO_NOTHING, db_column='to_table', related_name = 'to_table')
    to_column = models.CharField(max_length=50)
    value_vocabulary_id = models.CharField(max_length=50, blank=True, null=True)
    value_concept_code = models.CharField(max_length=50, blank=True, null=True)
    addl_column = models.CharField(max_length=50, blank=True, null=True)
    addl_value = models.CharField(max_length=50, blank=True, null=True)
    from_date_column = models.CharField(max_length=50, blank=True, null=True)
    where_clause = models.CharField(max_length=256)
    comment = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'events_mapping'
        unique_together = (('study', 'from_table', 'from_column', 'to_table', 'to_column', 'where_clause'),)


class ExtractStudy(models.Model):
    extract_study_id = models.IntegerField(primary_key=True)
    study_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'extract_study'


#class FactRelationship(models.Model):
#    domain_concept_id_1 = models.ForeignKey(Concept, models.DO_NOTHING, db_column='domain_concept_id_1')
#    fact_id_1 = models.IntegerField()
#    domain_concept_id_2 = models.ForeignKey(Concept, models.DO_NOTHING, db_column='domain_concept_id_2')
#    fact_id_2 = models.IntegerField()
#    relationship_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#
#    class Meta:
#        managed = False
#        db_table = 'fact_relationship'


class Location(models.Model):
    location_id = models.IntegerField(primary_key=True)
    address_1 = models.CharField(max_length=50, blank=True, null=True)
    address_2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=9, blank=True, null=True)
    county = models.CharField(max_length=20, blank=True, null=True)
    location_source_value = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location'


class Measurement(models.Model):
    measurement_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    measurement_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'measurement_concept')
    measurement_date = models.DateField()
    measurement_datetime = models.DateTimeField(blank=True, null=True)
    measurement_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'measurement_type_concept')
    operator_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'operator_concept')
    value_as_number = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    value_as_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'measurement_value_as_concept')
    unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'measurement_unit_concept')
    range_low = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    range_high = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    #provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    provider = models.IntegerField(blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
    measurement_source_value = models.CharField(max_length=50, blank=True, null=True)
    measurement_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'measurement_source_concept')
    unit_source_value = models.CharField(max_length=50, blank=True, null=True)
    value_source_value = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'measurement'


class Note(models.Model):
    note_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    note_date = models.DateField()
    note_datetime = models.DateTimeField(blank=True, null=True)
    note_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'note_type_concept')
    note_class_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'note_class_concept')
    note_title = models.CharField(max_length=250, blank=True, null=True)
    note_text = models.TextField()
    encoding_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'encoding_concept')
    language_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'language_concept')
    #provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    provider = models.IntegerField(blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
    note_source_value = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'note'


#class NoteNlp(models.Model):
#    note_nlp_id = models.BigIntegerField(primary_key=True)
#    note = models.ForeignKey(Note, models.DO_NOTHING)
#    section_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    snippet = models.CharField(max_length=250, blank=True, null=True)
#    offset = models.CharField(max_length=250, blank=True, null=True)
#    lexical_variant = models.CharField(max_length=250)
#    note_nlp_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    note_nlp_source_concept_id = models.IntegerField(blank=True, null=True)
#    nlp_system = models.CharField(max_length=250, blank=True, null=True)
#    nlp_date = models.DateField()
#    nlp_datetime = models.DateTimeField(blank=True, null=True)
#    term_exists = models.CharField(max_length=1, blank=True, null=True)
#    term_temporal = models.CharField(max_length=50, blank=True, null=True)
#    term_modifiers = models.CharField(max_length=2000, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'note_nlp'


class Observation(models.Model):
    observation_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey('Person', models.DO_NOTHING)
    observation_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'observation_concept')
    observation_date = models.DateField()
    observation_datetime = models.DateTimeField(blank=True, null=True)
    observation_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'observation_type_concept')
    value_as_number = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    value_as_string = models.CharField(max_length=60, blank=True, null=True)
    value_as_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'observation_value_as_concept')
    qualifier_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
    unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'observation_unit_concept')
    #provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    provider = models.IntegerField(blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
    observation_source_value = models.CharField(max_length=50, blank=True, null=True)
    observation_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'observation_source_concept')
    unit_source_value = models.CharField(max_length=50, blank=True, null=True)
    qualifier_source_value = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'observation'


#class ObservationPeriod(models.Model):
#    observation_period_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    observation_period_start_date = models.DateField()
#    observation_period_start_datetime = models.DateTimeField()
#    observation_period_end_date = models.DateField()
#    observation_period_end_datetime = models.DateTimeField()
#    period_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#
#    class Meta:
#        managed = False
#        db_table = 'observation_period'


class OhdsiCalculationArgument(models.Model):
    vocabulary = models.ForeignKey('VocabularyConcept', models.DO_NOTHING, related_name = 'vocabulary_concept')
    concept_code = models.CharField(max_length=100)
    study = models.ForeignKey('Study', models.DO_NOTHING, primary_key=True)
    function_name = models.CharField(max_length=100)
    argument_order = models.IntegerField(blank=True, null=True)
    argument_name = models.CharField(max_length=30, blank=True, null=True)
    value_field = models.CharField(max_length=20, blank=True, null=True)
    to_concept_code = models.CharField(max_length=100)
    to_vocabulary = models.ForeignKey('VocabularyConcept', models.DO_NOTHING, related_name = 'to_vocabulary_concept')
    from_table = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ohdsi_calculation_argument'
        unique_together = (('study', 'function_name', 'to_concept_code', 'to_vocabulary', 'vocabulary', 'concept_code'),)


class OhdsiCalculationFunction(models.Model):
    study = models.ForeignKey('Study', models.DO_NOTHING, primary_key=True)
    function_name = models.CharField(max_length=100)
    to_vocabulary = models.ForeignKey('VocabularyConcept', models.DO_NOTHING)
    to_concept_code = models.CharField(max_length=100)
    to_table = models.CharField(max_length=100, blank=True, null=True)
    to_column = models.CharField(max_length=100, blank=True, null=True)
    function_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ohdsi_calculation_function'
        unique_together = (('study', 'function_name', 'to_concept_code', 'to_vocabulary'),)


#class PayerPlanPeriod(models.Model):
#    payer_plan_period_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey('Person', models.DO_NOTHING)
#    payer_plan_period_start_date = models.DateField()
#    payer_plan_period_end_date = models.DateField()
#    payer_source_value = models.CharField(max_length=50, blank=True, null=True)
#    plan_source_value = models.CharField(max_length=50, blank=True, null=True)
#    family_source_value = models.CharField(max_length=50, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'payer_plan_period'


class Person(models.Model):
    person_id = models.IntegerField(primary_key=True)
    gender_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'gender_concept')
    year_of_birth = models.IntegerField()
    month_of_birth = models.IntegerField(blank=True, null=True)
    day_of_birth = models.IntegerField(blank=True, null=True)
    birth_datetime = models.DateTimeField(blank=True, null=True)
    race_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'race_concept')
    ethnicity_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'ethnicity_concept')
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    #provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    provider = models.IntegerField(blank=True, null=True)
    #care_site = models.ForeignKey(CareSite, models.DO_NOTHING, blank=True, null=True)
    care_site = models.IntegerField(blank=True, null=True)
    person_source_value = models.CharField(max_length=50, blank=True, null=True)
    gender_source_value = models.CharField(max_length=50, blank=True, null=True)
    gender_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'gender_source_concept')
    race_source_value = models.CharField(max_length=50, blank=True, null=True)
    race_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'race_source_concept')
    ethnicity_source_value = models.CharField(max_length=50, blank=True, null=True)
    ethnicity_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'ethnicity_source_concept')

    class Meta:
        managed = False
        db_table = 'person'


class ProcedureOccurrence(models.Model):
    procedure_occurrence_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING)
    procedure_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'procedure_concept')
    procedure_date = models.DateField()
    procedure_datetime = models.DateTimeField()
    procedure_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'procedure_type_concept')
    modifier_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'modifier_concept')
    quantity = models.IntegerField(blank=True, null=True)
    #provider = models.ForeignKey('Provider', models.DO_NOTHING, blank=True, null=True)
    provider = models.IntegerField(blank=True, null=True)
    visit_occurrence = models.ForeignKey('VisitOccurrence', models.DO_NOTHING, blank=True, null=True)
    procedure_source_value = models.CharField(max_length=50, blank=True, null=True)
    procedure_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'procedure_source_concept')
    qualifier_source_value = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'procedure_occurrence'


#class Provider(models.Model):
#    provider_id = models.IntegerField(primary_key=True)
#    provider_name = models.CharField(max_length=255, blank=True, null=True)
#    npi = models.CharField(max_length=20, blank=True, null=True)
#    dea = models.CharField(max_length=20, blank=True, null=True)
#    specialty_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    care_site = models.ForeignKey(CareSite, models.DO_NOTHING, blank=True, null=True)
#    year_of_birth = models.IntegerField(blank=True, null=True)
#    gender_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    provider_source_value = models.CharField(max_length=50, blank=True, null=True)
#    specialty_source_value = models.CharField(max_length=50, blank=True, null=True)
#    specialty_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    gender_source_value = models.CharField(max_length=50, blank=True, null=True)
#    gender_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'provider'


class Relationship(models.Model):
    relationship_id = models.CharField(primary_key=True, max_length=20)
    relationship_name = models.CharField(max_length=255)
    is_hierarchical = models.CharField(max_length=1)
    defines_ancestry = models.CharField(max_length=1)
    reverse_relationship = models.ForeignKey('self', models.DO_NOTHING)
    relationship_concept = models.ForeignKey(Concept, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'relationship'


class SourceToConceptMap(models.Model):
    source_code = models.CharField(max_length=50)
    source_concept_id = models.IntegerField()
    source_vocabulary = models.ForeignKey('Vocabulary', models.DO_NOTHING, primary_key=True, related_name = 'source_vocabulary')
    source_code_description = models.CharField(max_length=255, blank=True, null=True)
    target_concept = models.ForeignKey(Concept, models.DO_NOTHING)
    target_vocabulary = models.ForeignKey('Vocabulary', models.DO_NOTHING, related_name = 'target_vocabulary')
    valid_start_date = models.DateField()
    valid_end_date = models.DateField()
    invalid_reason = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'source_to_concept_map'
        unique_together = (('source_vocabulary', 'target_concept', 'source_code', 'valid_end_date'),)

#
#class Specimen(models.Model):
#    specimen_id = models.IntegerField(primary_key=True)
#    person = models.ForeignKey(Person, models.DO_NOTHING)
#    specimen_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    specimen_type_concept = models.ForeignKey(Concept, models.DO_NOTHING)
#    specimen_date = models.DateField()
#    specimen_datetime = models.DateTimeField(blank=True, null=True)
#    quantity = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
#    unit_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    anatomic_site_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    disease_status_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True)
#    specimen_source_id = models.CharField(max_length=50, blank=True, null=True)
#    specimen_source_value = models.CharField(max_length=50, blank=True, null=True)
#    unit_source_value = models.CharField(max_length=50, blank=True, null=True)
#    anatomic_site_source_value = models.CharField(max_length=50, blank=True, null=True)
#    disease_status_source_value = models.CharField(max_length=50, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'specimen'
#

class Study(models.Model):
    study_id = models.IntegerField(primary_key=True)
    study_name = models.CharField(max_length=100, blank=True, null=True)
    person_id_range_start = models.IntegerField(blank=True, null=True)
    person_id_range_end = models.IntegerField(blank=True, null=True)
    observation_range_start = models.IntegerField(blank=True, null=True)
    observation_range_end = models.IntegerField(blank=True, null=True)
    loaded = models.BooleanField()
    migrated = models.BooleanField()
    calculated = models.BooleanField()
    id_field_name           = models.CharField(max_length=10, blank=True, null=True)
    person_id_prefix        = models.CharField(max_length=10, blank=True, null=True)
    person_id_select        = models.CharField(max_length=100, blank=True, null=True)
    person_details_select   = models.CharField(max_length=200, blank=True, null=True)
    study_class             = models.CharField(max_length=50, blank=True, null=True)
    sex_table_name        = models.CharField(max_length=100, blank=True, null=True)
    sex_column_name        = models.CharField(max_length=100, blank=True, null=True)
    sex_function_name        = models.CharField(max_length=100, blank=True, null=True)
    race_table_name        = models.CharField(max_length=100, blank=True, null=True)
    race_column_name        = models.CharField(max_length=100, blank=True, null=True)
    race_function_name        = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'study'

class TableColumn(models.Model):
    table_column_id = models.IntegerField(primary_key=True)
    study = models.ForeignKey(Study, models.DO_NOTHING, blank=True, null=True)
    table_name = models.CharField(max_length=50)
    column_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'table_column'
        unique_together = (('table_name', 'column_name'),)

#class StudyConceptType(models.Model):
#    study_id = models.IntegerField(primary_key=True)
#    study_concept_type_id = models.AutoField()
#    name = models.CharField(max_length=50)
#    filename = models.CharField(max_length=50)
#    description = models.CharField(max_length=1000, blank=True, null=True)
#    considered = models.NullBooleanField()
#
#    class Meta:
#        managed = False
#        db_table = 'study_concept_type'
#        unique_together = (('study_id', 'study_concept_type_id'),)
#
#
#class StudyConceptValue(models.Model):
#    study = models.ForeignKey(StudyConceptType, models.DO_NOTHING, primary_key=True)
#    study_concept_type_id = models.IntegerField()
#    study_concept_value_id = models.AutoField()
#    name = models.CharField(max_length=250)
#    description = models.CharField(max_length=1000, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'study_concept_value'
#        unique_together = (('study', 'study_concept_type_id', 'study_concept_value_id'),)


class StudyToOhdsiMapping(models.Model):
    study = models.ForeignKey(Study, models.DO_NOTHING)

    # WTF, TODO
    #from_table = models.ForeignKey('TableColumn', models.DO_NOTHING, db_column='from_table', related_name = 'study_from_table')
    from_table = models.CharField(max_length=100)

    from_column = models.CharField(max_length=100)
    function_name = models.CharField(max_length=100, blank=True, null=True)

    vocabulary_id = models.CharField(max_length=100)
    concept_code = models.CharField(max_length=100, blank=True, null=True)

    # should be a single composite key, but django doesn't support that and the demo's due. TODO
    # https://pypi.python.org/pypi/django-composite-foreignkey
    #vocabulary_id = models.ForeignKey('Concept', models.DO_NOTHING, blank=True, null=True)
    #concept_code = models.ForeignKey('Concept', models.DO_NOTHING,  blank=True, null=True)

    # TODO I think, it's OK. We need the FK in the database, but not here?? Can't traverse it here wihtout this, 
    # but the FK in the database ensures we're not making up concepts.
    #vocabulary = models.ForeignKey('VocabularyConcept', models.DO_NOTHING, blank=True, null=True)
    #concept_code = models.ForeignKey('VocabularyConcept', models.DO_NOTHHING,  blank=True, null=True)

    #to_table = models.ForeignKey('TableColumn', models.DO_NOTHING, db_column='to_table', blank=True, null=True, related_name = 'ohdsi_to_table')
    to_table = models.CharField(max_length=100, blank=True, null=True)
    to_column = models.CharField(max_length=100, blank=True, null=True)
    addl_value_1 = models.CharField(max_length=20, blank=True, null=True)
    addl_column_1 = models.CharField(max_length=20, blank=True, null=True)
    from_where_clause = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=250, blank=True, null=True)
    from_where_column = models.CharField(max_length=100, blank=True, null=True)
    units = models.CharField(max_length=20, blank=True, null=True)
    has_date = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'study_to_ohdsi_mapping'

    def __str__(self):
        return "table:{} coln:{} fun:{} v:{} c:{} table:{} column:{} where:{} where:{} has_date:{}".format(
            self.from_table, self.from_column, self.function_name, self.vocabulary_id, 
            self.concept_code, self.to_table, self.to_column, self.from_where_column, self.from_where_clause, self.has_date)



class VisitOccurrence(models.Model):
    visit_occurrence_id = models.IntegerField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING)
    visit_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'visit_concept')
    visit_start_date = models.DateField()
    visit_start_datetime = models.DateTimeField(blank=True, null=True)
    visit_end_date = models.DateField()
    visit_end_datetime = models.DateTimeField(blank=True, null=True)
    visit_type_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'visit_type_concept')
    #provider = models.ForeignKey(Provider, models.DO_NOTHING, blank=True, null=True)
    provider = models.IntegerField(blank=True, null=True)
    #care_site = models.ForeignKey(CareSite, models.DO_NOTHING, blank=True, null=True)
    care_site = models.IntegerField(blank=True, null=True)
    visit_source_value = models.CharField(max_length=50, blank=True, null=True)
    visit_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'visit_source_concept')
    admitting_source_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'admitting_source_concept')
    admitting_source_value = models.CharField(max_length=50, blank=True, null=True)
    discharge_to_concept = models.ForeignKey(Concept, models.DO_NOTHING, blank=True, null=True, related_name = 'discharge_to_source_concept')
    discharge_to_source_value = models.CharField(max_length=50, blank=True, null=True)
    preceding_visit_occurrence_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'visit_occurrence'


class Vocabulary(models.Model):
    vocabulary_id = models.CharField(primary_key=True, max_length=20)
    vocabulary_name = models.CharField(max_length=255)
    vocabulary_reference = models.CharField(max_length=255, blank=True, null=True)
    vocabulary_version = models.CharField(max_length=255, blank=True, null=True)
    vocabulary_concept = models.ForeignKey(Concept, models.DO_NOTHING, related_name = 'vocabulary_concept')

    class Meta:
        managed = False
        db_table = 'vocabulary'


class VocabularyConcept(models.Model):
    vocabulary_id = models.CharField(max_length=20)
    concept_code = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'vocabulary_concept'
        unique_together = (('vocabulary_id', 'concept_code'),)

class StudyMappingArguments(models.Model):
    study_id = models.IntegerField(blank=True, null=True)
    from_table = models.CharField(max_length=100, blank=True, null=True)
    from_column = models.CharField(max_length=100, blank=True, null=True)
    function_name = models.CharField(max_length=100, blank=True, null=True)
    from_where_clause = models.CharField(max_length=100, blank=True, null=True)
    from_where_column = models.CharField(max_length=100, blank=True, null=True)
    mapped_string = models.CharField(max_length=100, blank=True, null=True)
    mapped_number = models.IntegerField(blank=True, null=True)
    mapped_concept_vocabulary_id = models.CharField(max_length=20, blank=True, null=True)
    mapped_concept_code = models.CharField(max_length=50, blank=True, null=True)
    transform_factor = models.FloatField(blank=True, null=True)
    transform_shift = models.FloatField(blank=True, null=True)
    to_concept_vocabulary_id = models.CharField(max_length=20, blank=True, null=True)
    to_concept_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "study_id:{} from_table:{} from_column:{} function_name:{} from_where_clause:{} from_where_column:{} mapped_string:{} mapped_number:{} mapped_concept_vocabulary_id:{} mapped_concept_code:{} transform_factor:{} transform_shift:{}  to_concept_vocabulary_id:{} to_concept_code:{}".format(
            self.study_id,
            self.from_table,
            self.from_column,
            self.function_name,
            self.from_where_clause,
            self.from_where_column,
            self.mapped_string,
            self.mapped_number,
            self.mapped_concept_vocabulary_id,
            self.mapped_concept_code,
            self.transform_factor,
            self.transform_shift,
            self.to_concept_vocabulary_id,
            self.to_concept_code)

    class Meta:
        managed = False
        db_table = 'study_mapping_arguments'

