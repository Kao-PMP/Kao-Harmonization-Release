/***
module:function_choice
param: callback(concept_id)
prefix: fcm
***/

var createFunctionChoiceModule = function(callback) {
   
    var _function_name;

    function _do_choice_event() { 
        var function_name = document.getElementById("fcm_function_choice").value;
        _function_name = function_name; 
        callback(_function_name);
    }


    function _build_function_choices(json_list) {
        console.log("function_choice._build_function_choices()" +length(json_list))
        var select_div = document.getElementById("fcm_select_function_div");
        while (select_div.hasChildNodes()) {
            select_div.removeChild(select_div.firstChild);
        }

        var select_fragment = document.createElement("select")
        select_fragment.id = "fcm_function_choice"
        select_div.append(select_fragment)
        for (var i=0; i< json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].function_name;
            option_fragment.text=json_list[i].function_name;
            select_fragment.appendChild(option_fragment);
        } 
        select_div.addEventListener('click', _do_choice_event, false);
    };
    
    function do_function_choices(study_id) {
        var study_id=get_checked_radio_button("fcm_study_choice"); // TODO modulaaritzaiton
        var function_url = "/ui/get_study_to_ohdsi_mapping_functions/" + study_id;
        console.log("function_choice.do_function_choices()" + function_url);
        load_url(function_url, _build_function_choices);
    };


    function get_study_id_update(study_id) {
        _study_id = study_id;
        do_function_choices(_study_id);
    }
    
    return {
        get_study_id_update
    };
}
