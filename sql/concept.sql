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

insert into concept values (2000000001, 'Heart failure duration', 'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-1', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000002, 'Pump Failure',           'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-2', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000003, 'Cardiovascular Death',   'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-3', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000004, 'Non CV Death',           'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-4', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000005, 'End of Study',           'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-5', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000006, 'Randomization',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-6', '2018-04-13', '2099-12-31', null  );
insert into concept values (2000000007, 'Aggregated Cardia Arrest',    'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-7', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000008, 'Fatal Myocardial Infarction', 'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-8', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000009, 'Other CV Death',              'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-9', '2018-04-13', '2099-12-31', null); 
insert into concept values (2000000010, 'Uknown cause of death',       'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-10','2018-04-13', '2099-12-31', null); 
insert into concept values (2000000011, 'Ethnicity Unknown',            'Race',     'SNOMED',    'Social Context', null, '10241000175103', '2017-09-14', '2099-12-13', null); 

insert into concept values (2000000012, 'paradigm.ctd_flg1',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-12','2018-04-13', '2099-12-31', null); 

insert into concept values (2000000901, 'A',          'UCD.Kao TEST', 'UCD.Kao', 'UCD.Kao CC', null, 'test-1','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000902, 'B',          'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'test-2','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000903, 'C',          'UCD.Kao TEST', 'UCD.Kao', 'UCD.Kao CC', null, 'test-3','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000904, 'D',          'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'test-4','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000905, 'E',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'test-5','2018-07-06', '2099-12-31', null); 
insert into concept values (2000000906, 'sex',        'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'test-6','2018-07-06', '2099-12-31', null); 

-- use SNOMED 69031000119105
-- insert into concept values (2000000013, 'paradigm.crt_flg1',          'UCD.Kao D', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-13','2018-04-13', '2099-12-31', null); 

insert into concept values (2000000014, 'paradigm.icd_flg1',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-14', '2018-04-13', '2099-12-31', null); 
insert into concept values (2000000015, 'paradigm.ang_flg1',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-15', '2018-04-13', '2099-12-31', null); 
insert into concept values (2000000016, 'paradigm.angioten',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-16', '2018-04-13', '2099-12-31', null); 
insert into concept values (2000000017, 'Alternate Patient ID',       'UCD.Kao D',   'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-17', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000018, 'Death Days',                 'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-18', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000019, 'Tmt is placebo/std of care', 'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-19', '2018-04-13', '2099-12-31', null); 
insert into concept values (2000000020, 'End Of Study Days',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-20', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000021, 'End Of Study Date',          'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-21', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000022, 'Topcat End Of Study years',  'UCD.Kao D',   'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-22', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000023, 'Topcat Site death years',    'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-23', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000024, 'Topcat CEC death years',     'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-24', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000025, 'Topcat Site vs CEC',         'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-25', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000026, 'Death Days',                 'UCD.Kao D',   'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-26', '2018-04-13', '2099-12-31', null);
insert into concept values (2000000027, 'Death Status',               'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-27', '2018-10-25', '2099-12-31', null); 
insert into concept values (2000000028,'CV Death Status',             'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-28', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000029, 'CV Death days',              'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-29', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000030, 'All-cause Hospital status',  'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-30', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000031, 'All-cause Hospital days',    'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-31', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000032, 'CV Hospital status',         'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-32', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000033, 'CV Hospital days',           'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-33', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000034, 'HF Hospital status',         'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-34', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000035, 'ACCORD CaCB',                'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-35', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000036, 'CV Death or non-fatal MI or non-fatal stroke','Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-36', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000037, 'CORONA 4-value Tobacco Use', 'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-37', '2018-10-28', '2099-12-31', null);
insert into concept values (2000000038, 'original_subject_id',        'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-38', '2018-12-05', '2099-12-31', null);
insert into concept values (2000000039, 'Relative Wall Thickness',    'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-39', '2018-12-05', '2099-12-31', null);
insert into concept values (2000000040, '2nd DBP',                    'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-40', '2018-12-05', '2099-12-31', null);
insert into concept values (2000000041, '2nd SBP',                    'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-41', '2018-12-05', '2099-12-31', null);
insert into concept values (2000000042, 'dSBP',                       'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-42', '2019-04-04', '2099-12-31', null); --
insert into concept values (2000000043, 'dDBP',                       'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-43', '2019-04-04', '2099-12-31', null); --
insert into concept values (2000000051, 'EPV EMS Ratio DRV',          'UCD.Kao D',   'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-51', '2019-01-17', '2099-12-31', null);
insert into concept values (2000000053, 'BSA DRV',                    'UCD.Kao D',   'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-53', '2019-01-17', '2099-12-31', null); 
insert into concept values (2000000054, 'RWT Cat',                    'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-54', '2019-02-06', '2099-12-31', null); --
insert into concept values (2000000055, 'LVM Cat',                    'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-55', '2019-02-06', '2099-12-31', null); --
insert into concept values (2000000056, 'LVM Cat male',               'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-56', '2019-02-06', '2099-12-31', null); --
insert into concept values (2000000057, 'LVM Cat female',             'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-57', '2019-02-06', '2099-12-31', null); --
insert into concept values (2000000058, 'HF Hospital days',           'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-58', '2018-10-25', '2099-12-31', null);
insert into concept values (2000000059, 'Gender Cat',                 'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-59', '2019-02-06', '2099-12-31', null);
insert into concept values (2000000060, 'LVH Cat',                    'Measurement', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-60', '2019-02-19', '2099-12-31', null); --
insert into concept values (2000000061, 'BARI-2D non sublingal nitrate',       'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-61', '2019-04-05', '2099-12-31', null);
insert into concept values (2000000062, 'ACCORD Other BP med',        'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-62', '2019-04-05', '2099-12-31', null);
insert into concept values (2000000063, 'MI Stroke',                  'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-63', '2019-04-16', '2099-12-31');
insert into concept values (2000000064, 'Race 2 class',               'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-64', '2019-04-19', '2099-12-31');
insert into concept values (2000000065, 'Race Non-African American',  'UCD.Kao D',   'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-65', '2019-04-24', '2099-12-31');
insert into concept values (2000000066, 'Study Name',                 'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-66', '2019-05-08', '2099-12-31');
insert into concept values (2000000067, 'Member of ALLHAT LLT tmt?',  'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-67', '2019-05-15', '2099-12-31');
insert into concept values (2000000068, 'Member of ALLHAT DOX tmt?',  'Observation', 'UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-68', '2019-05-15', '2099-12-31');
insert into concept values (2000000069, 'AIM-HIGH 4-value Tobacco Use','Observation','UCD.Kao', 'UCD.Kao CC', null, 'UCD-Kao-69', '2019-05-15', '2099-12-31');


ALTER TABLE concept ADD CONSTRAINT fpk_concept_domain FOREIGN KEY (domain_id)  REFERENCES domain (domain_id);
ALTER TABLE concept ADD CONSTRAINT fpk_concept_class FOREIGN KEY (concept_class_id)  REFERENCES concept_class (concept_class_id);
ALTER TABLE concept ADD CONSTRAINT fpk_concept_vocabulary FOREIGN KEY (vocabulary_id)  REFERENCES vocabulary (vocabulary_id);
ALTER TABLE concept_class ADD CONSTRAINT fpk_concept_class_concept FOREIGN KEY (concept_class_concept_id)  REFERENCES concept (concept_id);
ALTER TABLE domain ADD CONSTRAINT fpk_domain_concept FOREIGN KEY (domain_concept_id)  REFERENCES concept (concept_id);
ALTER TABLE vocabulary ADD CONSTRAINT fpk_vocabulary_concept FOREIGN KEY (vocabulary_concept_id)  REFERENCES concept (concept_id);




