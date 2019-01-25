/****
module: EditExtractMappingModule
prefix: eemm

****/

var createEditExtractMappingModule = function(extract_study_id_callback) {

    var _extract_study_id;

    var _extract_study_id_callback = extract_study_id_callback;

    var get_extract_study_id_update = function(extract_study_id) {
        console.log("edit_table_mappings:" + extract_study_id);
        _extract_study_id = extract_study_id;
        _do_function_choices();
    } 
 
    function _build_concept_choices(json_list) {
        var select_fragment  = document.getElementById("eemm_concept_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].concept_id;
            option_fragment.text=json_list[i].concept_code + " \"" + json_list[i].concept_name + "\"" ;
            select_fragment.appendChild(option_fragment);
        }
    }

    function _do_search_button() {
        var vocabulary_choice = document.getElementById("eemm_vocabulary_choice").value;
        var search_term_input = document.getElementById("eemm_concept_string").value;
        console.log("do_search_button()" + search_term_input + ", " + vocabulary_choice);
        var vocabularies_url = "/ui/get_concepts_like/" + vocabulary_choice + "/" + search_term_input + "/";
        load_url(vocabularies_url, _build_concept_choices);
    }

    function _build_vocabulary_choices(json_list) {
        var select_fragment  = document.getElementById("eemm_vocabulary_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
        //select_div.addEventListener('click', _do_column_choices, false); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i];
            option_fragment.text=json_list[i];
            select_fragment.appendChild(option_fragment);
        }


        var search_term_button = document.getElementById("eemm_concept_button");
        search_term_button.addEventListener('click', _do_search_button, false); 
        var concept_string_widget = document.getElementById("eemm_concept_string");
        /* concept_string_widget.addEventListener('input', _do_search_button, false); # fires after each character */
        concept_string_widget.addEventListener('change', _do_search_button, false); 
    }

    function _do_vocabulary_choices() {
        var vocabularies_url = "/ui/get_common_vocabularies/";
        console.log("_do_vocabulary_choices()" + vocabularies_url);
        load_url(vocabularies_url, _build_vocabulary_choices);
    }

    function _build_function_choices(json_list) {
        var select_fragment  = document.getElementById("eemm_cat_function_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
        //select_div.addEventListener('click', _do_column_choices, false); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].name;
            option_fragment.text=json_list[i].name;
            select_fragment.appendChild(option_fragment);
        }
    }

    function _do_function_choices() {
        console.log("edit_table_mapping._do_function_choices()")
        var functions_url = "/ui/get_categorization_functions/" ;
        console.log("_do_function_choices()" + functions_url);
        load_url(functions_url, _build_function_choices);
    }

    function init() {
        console.log("edit_table_mapping.init()")
        _do_vocabulary_choices();
        _do_function_choices();
    }

    return {
        get_extract_study_id_update,
        init
    };
};
