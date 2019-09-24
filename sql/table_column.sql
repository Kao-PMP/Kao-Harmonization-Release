INSERT into table_column (study_id, table_name, column_name)
SELECT s.study_id,  concat(c.table_schema, '.', c.table_name), c.column_name
FROM information_schema.columns c JOIN study s
    ON upper(c.table_schema) = upper(s.study_name)
WHERE c.table_schema in ('accord', 'aimhigh', 'allhat', 'bari2d')
AND  (concat(c.table_schema, ',', c.table_name), c.column_name) NOT IN
    (SELECT table_name, column_name FROM table_column)
;
