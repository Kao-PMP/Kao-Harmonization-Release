-- test that the number of records in Death is correct
-- These are like asserts. they should all come up true.
-- written for display here
select 'Test row counts in Death Table. Test_1.sql' as title;
select 'BEST'     as study, count(*) as actual, 860 as expected, count(*)=860 from Death where person_id < 10000000
union
select 'HFACTION' as study, count(*) as actual, 344 as expected, count(*)=344 from Death where person_id >= 10000000 and person_id < 11000000
union
select 'SCDHEFT'  as study, count(*) as actual, 666 as expected, count(*)=666 from Death where person_id >= 11000000 and person_id < 12000000
union
select 'TOPCAT'   as study, count(*) as actual, 530 as expected, count(*)=530 from Death where person_id >= 12000000 and person_id < 13000000
union
select 'PARADIGM' as study, count(*) as actual, 1112 as expected, count(*)=1112 from Death where person_id >= 13000000 and person_id < 14000000;

-- written to give a pass/fail answer for the whole thing here:
select
(select count(*)=860 from Death where person_id < 10000000)
and
(select count(*)=344 from Death where person_id >= 10000000 and person_id < 11000000)
and
(select count(*)=666 from Death where person_id >= 11000000 and person_id < 12000000)
and
(select count(*)=530 from Death where person_id >= 12000000 and person_id < 13000000)
and
(select count(*)=1112 from Death where person_id >= 13000000 and person_id < 14000000)
as sum_total_answer;

