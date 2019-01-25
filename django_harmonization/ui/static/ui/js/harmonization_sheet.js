/****
module: harmonization_sheet
prefix: hsm

****/
"use strict";

var createHarmonizationSheetModule = function() {

    var showTableMappingsModule;
    var editTableMappingModule;
    var showExtractMappingsModule;
    var editExtractMappingModule;
    var studyChoiceModule;
    var extractStudyChoiceModule;
  
    var editTableMappingFunctionModule;
    var editExtractMappingFunctionModule;

    function init() {

        // IMPORT
        editTableMappingFunctionModule = createEditTableMappingFunctionModule(
            function(row_tuple) {
                console.log("chose a mapping rowd:\"" + row_tuple + "\"");
                editTableMappingFunctionModule.get_function_name_update(row_tuple.function_name); 
            }
        );
        editTableMappingFunctionModule.init();

        showTableMappingsModule = createShowTableMappingsModule();
        editTableMappingModule = createEditTableMappingModule(
            function(table_name) {
                console.log("got a table name:\"" + table_name + "\"");
                showTableMappingsModule.get_table_name_update(table_name);
            }
        );
        editTableMappingModule.init();    

        studyChoiceModule = createStudyChoiceModule(
            function(study_id) {
                console.log("got a study_id:\"" + study_id + "\"");
                showTableMappingsModule.get_study_id_update(study_id);
                editTableMappingModule.get_study_id_update(study_id);
            }
        );  


        // EXTRACT
        editExtractMappingFunctionModule = createEditExtractMappingFunctionModule();
        editExtractMappingFunctionModule.init();
        
        showExtractMappingsModule = createShowExtractMappingsModule(editExtractMappingFunctionModule.get_extract_function_row_choice);

        editExtractMappingModule = createEditExtractMappingModule();
        editExtractMappingModule.init();    
    
        extractStudyChoiceModule =  createExtractStudyChoiceModule(
            function(extract_study_id) {
                showExtractMappingsModule.get_extract_study_id_update(extract_study_id);
                editExtractMappingModule.get_extract_study_id_update(extract_study_id);
            }
        );
    };

    return {
        init
    };
}
