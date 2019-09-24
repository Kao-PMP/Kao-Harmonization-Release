/***
module:extract_study_choice
param: callback(concept_id)
prefix: escm
***/

var createExtractStudyChoiceModule = function(callback) {
   
    var _extract_study_id;
    var _callback = callback;

    function _do_choice_event() { 
        _extract_study_id = function_name = document.getElementById("escm_function_choice").value;
        _callback(_extract_study_id);
    }


    function _build_extract_study_choices(json_list) {
        console.log("extract_study_choice._build_extract_study_choices()" + json_list.length)
        //console.log("extract_study_choice._build_extract_study_choices()" + JSON.stringify(json_list))
        var select_div = document.getElementById("escm_select_extract_study_div");
        while (select_div.hasChildNodes()) {
            select_div.removeChild(select_div.firstChild);
        }

        var select_fragment = document.createElement("select")
        select_fragment.id = "escm_function_choice"
        select_div.append(select_fragment)
        for (var i=0; i< json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].extract_study_id;  // <-------
            if (i == 0) {
                _extract_study_id = json_list[i].extract_study_id;
            }
            option_fragment.text=json_list[i].name;
            select_fragment.appendChild(option_fragment);
        } 
        select_div.addEventListener('change', _do_choice_event, false);

        _callback(_extract_study_id);
    };
    
    function do_choices() {
        var function_url = "/ui/get_extract_study_list/";
        console.log("extract_study_choice.do_choices()" + function_url);
        load_url(function_url, _build_extract_study_choices);
    };

    do_choices();
    
    return {
        
    };
}
