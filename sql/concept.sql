-- Domain: "UCD.Kao Domain"
-- Vocabulary: "UCD.Kao Vocabulary"
-- Concept Class: "UCD.Kao Concept Class"

ALTER TABLE concept DROP CONSTRAINT fpk_concept_domain ;
ALTER TABLE concept DROP CONSTRAINT fpk_concept_class ;
ALTER TABLE concept DROP CONSTRAINT fpk_concept_vocabulary;

ALTER TABLE vocabulary DROP CONSTRAINT fpk_vocabulary_concept ;
ALTER TABLE domain DROP CONSTRAINT fpk_domain_concept ;
ALTER TABLE concept_class DROP CONSTRAINT fpk_concept_class_concept ;

insert into concept values (2000000101, 'UCD.Kao Concept Class Concept', 'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-101', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000102, 'UCD.Kao Vocabulary Concept',    'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-102', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000103, 'UCD.Kao Domain Concept',        'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-103', '2018-04-13', '2099-12-31', null  );

insert into concept_class values('UCD.Kao CC', 'UCD.Kao Concept Class', 2000000101);
insert into vocabulary    values('UCD.Kao', 'UCD.Kao Vocabulary', null, null,     2000000102);
insert into domain        values('UCD.Kao D', 'UCD.Kao Domain',         2000000103);

insert into concept values (2000000001, 'Heart failure duration', 'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-1', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000002, 'Pump Failure',           'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-2', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000003, 'Cardiovascular Death',   'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-3', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000004, 'Non CV Death',           'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-4', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000005, 'End of Study',           'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-5', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000006, 'Randomization',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-6', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000007, 'Aggregated Cardia Arrest',    'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-7', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000008, 'Fatal Myocardial Infarction', 'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-8', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000009, 'Other CV Death',              'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-9', '2018-04-13', '2099-12-31', null); 
insert into concept values (2000000010, 'Uknown cause of death',       'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-10','2018-04-13', '2099-12-31', null); 
insert into concept values (2000000011, 'Ethnicity Unknown',            'Race',     'SNOMED',    'Social Context', null, '10241000175103', '2017-09-14', '2099-12-13', null); 

insert into concept values (2000000012, 'paradigm.ctd_flg1',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-12','2018-04-13', '2099-12-31', null); 

insert into concept values (2000000901, 'A',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'test-1','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000902, 'B',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'test-2','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000903, 'C',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'test-3','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000904, 'D',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'test-4','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000905, 'E',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'test-5','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000906, 'sex',        'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'test-6','2018-07-06', '2099-12-31', null); 

-- use SNOMED 69031000119105
-- insert into concept values (2000000013, 'paradigm.crt_flg1',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-13','2018-04-13', '2099-12-31', null); 

insert into concept values (2000000014, 'paradigm.icd_flg1',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-14','2018-04-13', '2099-12-31', null); 
insert into concept values (2000000015, 'paradigm.ang_flg1',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-15','2018-04-13', '2099-12-31', null); 
insert into concept values (2000000016, 'paradigm.angioten',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-16','2018-04-13', '2099-12-31', null); 
insert into concept values (2000000017, 'Alternate Patient ID',       'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-17','2018-04-13', '2099-12-31', null);
insert into concept values (2000000018, 'Death Days',                 'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-18','2018-04-13', '2099-12-31', null);
insert into concept values (2000000019, 'Tmt is placebo/std of care', 'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-19','2018-04-13', '2099-12-31', null); 
insert into concept values (2000000020, 'End Of Study Days',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-20', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000021, 'End Of Study Date',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-21', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000022, 'Topcat End Of Study years',  'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-22', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000023, 'Topcat Site death years',    'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-23', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000024, 'Topcat CEC death years',     'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-24', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000025, 'Topcat Site vs CEC',         'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-25', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000026, 'Death Days',                 'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-26', '2018-04-13', '2099-12-31', null);


ALTER TABLE concept ADD CONSTRAINT fpk_concept_domain FOREIGN KEY (domain_id)  REFERENCES domain (domain_id);
ALTER TABLE concept ADD CONSTRAINT fpk_concept_class FOREIGN KEY (concept_class_id)  REFERENCES concept_class (concept_class_id);
ALTER TABLE concept ADD CONSTRAINT fpk_concept_vocabulary FOREIGN KEY (vocabulary_id)  REFERENCES vocabulary (vocabulary_id);
ALTER TABLE concept_class ADD CONSTRAINT fpk_concept_class_concept FOREIGN KEY (concept_class_concept_id)  REFERENCES concept (concept_id);
ALTER TABLE domain ADD CONSTRAINT fpk_domain_concept FOREIGN KEY (domain_concept_id)  REFERENCES concept (concept_id);
ALTER TABLE vocabulary ADD CONSTRAINT fpk_vocabulary_concept FOREIGN KEY (vocabulary_concept_id)  REFERENCES concept (concept_id);

