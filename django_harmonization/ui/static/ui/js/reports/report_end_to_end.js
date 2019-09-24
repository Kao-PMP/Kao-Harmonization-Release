/****
module: harmonization_sheet
prefix: hsm

****/
"use strict";

var createReportEndToEndModule = function() {

    var studyChoiceModule;
    var showStudyMetricsModule; 

    function init() {
        showStudyMetricsModule = createShowStudyMetricsModule();
        studyChoiceModule = createStudyChoiceModule(
            function(study_id) {
                console.log("got a study_id:\"" + study_id + "\"");
                // who wants to know about study changes?
                showStudyMetricsModule.get_study_id_update(study_id);
            }
        );  
    };

    return {
        init
    };
}
