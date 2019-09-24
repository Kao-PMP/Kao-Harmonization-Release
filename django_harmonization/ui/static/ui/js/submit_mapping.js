/***
module: SubmitMappingModule
prefix: smm
***/

var createSubmitMappingModule = function() {


    function get_source_update( study_id, table_name, column_name) {
        try {
            document.getElementById("smm_mapping_row_source").innerHTML = "Source: " + study_id + ":" + table_name + ":" + column_name
        }
        catch (err) {
            document.getElementById("smm_status_p").innerHTML =  "More elements required for source." + err
        }
    }

    function get_destination_update(vocab_id, concept_code) { 
        try {
            document.getElementById("smm_mapping_row_destination").innerHTML = "Destination: " + vocab_id + ":" + concept_code ;
        }
        catch (err) {
            document.getElementById("smm_status_p").innerHTML =  "More elements required for destination."
        }
    }
    
    function get_function_update(function_name) { 
        console.log("SubmitMappingModule.get_function_update() " + function_name)
        try {
            document.getElementById("smm_mapping_row_function").innerHTML = "Function: " + function_name
        }
        catch (err) {
            document.getElementById("smm_status_p").innerHTML =  "Mapping function choice required."
        }
    }

    return {
        get_source_update,
        get_destination_update,
        get_function_update
    };
        
}
