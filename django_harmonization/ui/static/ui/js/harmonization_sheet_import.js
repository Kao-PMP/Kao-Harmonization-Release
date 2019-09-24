/****
module: harmonization_sheet
prefix: hsm

****/
"use strict";

var createHarmonizationSheetModule = function() {

    var studyChoiceModule;
    var showTableMappingsModule;
    var editTableMappingModule;
    var showTableMappingArgsModule 
    var editTableMappingFunctionArgModule;

    //var editTableMappingFunctionModule;

    function init() {
        editTableMappingFunctionArgModule = createEditTableMappingFunctionArgModule(
            function(row_tuple) {
                console.log("arg module CB here" + row_tuple);
                //editTableMappingFunctionArgModule.get_function_name_update(row_tuple.function_name); 
            }
        );

        showTableMappingArgsModule = createShowTableMappingArgsModule(
            function(key) {
                console.log("CB in show table mapping args " + key);
                editTableMappingFunctionArgModule.get_key_update(key);
            }
        );

        editTableMappingModule = createEditTableMappingModule(
            function(table_name) {
                console.log("got a table name:\"" + table_name + "\"");
                showTableMappingsModule.get_table_name_update(table_name);
            }
       );
        editTableMappingModule.init();    

        showTableMappingsModule = createShowTableMappingsModule(
            function(json_string) {
                var json_obj = JSON.parse(json_string)
                console.log("chose a mapping row:\"" + json_string + "\"");

                editTableMappingModule.get_row_key_update(
                    json_obj['from_table'],
                    json_obj['from_column'],
                    json_obj['function_name'],
                    json_obj['from_where_column'],
                    json_obj['from_where_clause'],
                    json_obj['vocabulary_id'],
                    json_obj['concept_code'],
                    json_obj['to_table'],
                    json_obj['to_column']
                );

                console.log("chose a mapping row:\"" + json_string + "\"");
                console.log("chose a mapping row:\"" + json_obj + "\"");
                ///console.log("chose a mapping row:\"" + editTableMappingFunctionModule + "\"");

                    showTableMappingArgsModule.get_row_key_update(
                      json_obj['study_id'],
                      json_obj['from_table'],
                      json_obj['from_column'],
                      json_obj['function_name'],
                      json_obj['from_where_column'],
                      json_obj['from_where_clause'],
                      json_obj['vocabulary_id'],
                      json_obj['concept_code'],
                      json_obj['to_table'],
                      json_obj['to_column']
                  );
            
            }
        );

        studyChoiceModule = createStudyChoiceModule(
            function(study_id) {
                console.log("got a study_id:\"" + study_id + "\"");
                showTableMappingsModule.get_study_id_update(study_id);
                editTableMappingModule.get_study_id_update(study_id);
            }
        );  


    };

    return {
        init
    };
}
