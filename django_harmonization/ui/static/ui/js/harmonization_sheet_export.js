/****
module: harmonization_sheet_export
prefix: hsm

****/
"use strict";

var createHarmonizationSheetModuleExport = function() {

    var showExtractMappingsModule;
    var editExtractMappingModule;
    var extractStudyChoiceModule;
    var editExtractMappingFunctionModule;

    function init() {

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
