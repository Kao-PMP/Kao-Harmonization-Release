/****
module: edit_table_mapping
prefix: etmm

****/

var createEditTableMappingModule = function(table_choice_cb) {


    const initial_search_term = 'heart';
    const initial_vocabulary_choice = 'LOINC';
    var _table_choice_cb = table_choice_cb;
    const _from_where_clause = '';
    const _from_where_column = '';
    var _study_id;
    var _table_name;
    var _column_name;
    var _vocabulary_choice;
    var _concept_choice_id; // an OHDSI concept_id, not the vocabulary's id called concept_code in OHDSI
    var _function_name ; 
    var select_div = document.getElementById("etmm_select_columns_div");

    function _do_concept_select() {
        var select_fragment  = document.getElementById("etmm_concept_choice");
        //console.log("do concept select " + select_fragment.selectedIndex + " t:" 
        //    + select_fragment.options[select_fragment.selectedIndex].text + " v:"       
        //    + select_fragment.options[select_fragment.selectedIndex].value) ;       
        _concept_choice_id = select_fragment.options[select_fragment.selectedIndex].value ;       
    }

    function _build_concept_choices(json_list) {
        console.log("_build_concept_choices() got " + json_list.length)
        var select_fragment  = document.getElementById("etmm_concept_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
        if (json_list.length > 0) {
            _concept_choice_id = json_list[0].concept_id;
        }
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].concept_id;
            option_fragment.text=json_list[i].concept_code + " \"" + json_list[i].concept_name + "\"" ;
            select_fragment.appendChild(option_fragment);

            //option_fragment.addEventListener('change', _do_concept_select, false);
            select_fragment.addEventListener('change', _do_concept_select, false);
            if (i==0) {
                option_fragment.selected = true;
            }
        }
    }

    function _do_delete_button() {
        
        var delete_mapping_url = "/ui/delete_ohdsi_mapping/"
            + _study_id + "/"
            + _table_name + "/"
            + _column_name + "/"
            // + _from_where_clause + "/"
            // + _from_where_column + "/";
            +  "/"
            +  "/";
        console.log("DELETE MAPPING:" + delete_mapping_url)
        delete_url(delete_mapping_url).then(response => {
            console.log("ACK INSERT" + response)
            // send a  table name change to get the display to reload 
            _table_choice_cb(_table_name);
        });

    }

    function _do_edit_button() {
        //url(r'^edit_ohdsi_mapping/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)/(?P<from_where_clause>\w*)/(?P<from_where_column>\w*)/(?P<function_name>\w+)/(?P<concept_id>\d+)/(?P<to_table>\w+)/(?P<to_column>[\w_]+)/$', 
        
        to_table = document.getElementById("etmm_to_table_choice").value
        to_column = document.getElementById("etmm_to_column_choice").value

        var edit_mapping_url = "/ui/edit_ohdsi_mapping/"
            + _study_id + "/"
            + _table_name + "/"
            + _column_name + "/"
            + _from_where_clause + "/"
            + _from_where_column + "/"
            + _function_name +   "/"
            + _concept_choice_id +   "/"
            + to_table +  "/"
            + to_column +  "/";
        console.log("EDIT MAPPING:" + edit_mapping_url)
        put_url(edit_mapping_url).then(response => {
            // send a  table name change to get the display to reload
            _table_choice_cb(_table_name);
        });

    }

    function _do_insert_button() {

        if (_study_id == null) { 
            console.log("study_id is null, alerted.");
            alert("Choose a study from the list under \"Study\".");
        }
        if (_table_name == null) { // never happens
            console.log("table name is null, fix that");
        }
        if (_column_name == null) { // never happens
            console.log("column nameis null, fix that");
        }
        if (_function_name== null) { // never happens
            console.log("function name is null, should default to identity:q");
        }

        
        if (_concept_choice_id == null) {
            console.log("concept id is null, fix that");
            alert("Need to enter a search string and click the \"Search\" button under \"Vocabulary Search\" to create a list of concepts. Then choose one under \"Concept\".")
        }
        var _to_column = document.getElementById("etmm_to_column_choice").value
        var _to_table = document.getElementById("etmm_to_table_choice").value
        var put_mapping_url = "/ui/put_ohdsi_mapping/"
            + _study_id + "/"
            + _table_name + "/"
            + _column_name + "/"
            + _function_name + "/"
            + _concept_choice_id + "/" 
            + _to_table + "/"
            + _to_column + "/";
        console.log("PUT MAPPING:" + put_mapping_url)
        put_url(put_mapping_url).then(response => {
            // send a  table name change to get the display to reload 
            _table_choice_cb(_table_name);
        });
    }

    function _do_search_button() {
        _vocabulary_choice = document.getElementById("etmm_vocabulary_choice").value;
        mapped_checkbox_value = document.getElementById("etmm_concept_mapped_checkbox").checked;
        extract_checkbox_value = document.getElementById("etmm_concept_extract_checkbox").checked;
        console.log("checkboxes:" + mapped_checkbox_value + " "  + extract_checkbox_value);
        if (_vocabulary_choice == null || _vocabulary_choice == '') {
            _vocabulary_choice = initial_vocabulary_choice;
        }
        var search_term_input = document.getElementById("etmm_concept_string").value;
        console.log("------ do_search_button()" + search_term_input + ", " + _vocabulary_choice);
        var vocabularies_url = "/ui/get_concepts_like/" + _vocabulary_choice + "/" + search_term_input + "/" + mapped_checkbox_value + "/" + extract_checkbox_value + "/";
        load_url(vocabularies_url, _build_concept_choices);
    }

    function _build_vocabulary_choices(json_list) {
        var select_fragment  = document.getElementById("etmm_vocabulary_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
        if (json_list.length > 0) {
                _vocabulary_choice = json_list[0].name; 
        }
        //select_div.addEventListener('click', _do_column_choices, false); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i];
            option_fragment.text=json_list[i];
            select_fragment.appendChild(option_fragment);
            if (i==0) {
                option_fragment.selected = true;
            }
        }


        var search_term_button = document.getElementById("etmm_concept_button");
        search_term_button.addEventListener('click', _do_search_button, false); 
        var search_term_mapped_checkbox = document.getElementById("etmm_concept_mapped_checkbox");
        var search_term_extract_checkbox = document.getElementById("etmm_concept_extract_checkbox");
        var concept_string_widget = document.getElementById("etmm_concept_string");
        /* concept_string_widget.addEventListener('input', _do_search_button, false); # fires after each character */
        concept_string_widget.addEventListener('change', _do_search_button, false); 
    }

    function _do_vocabulary_choices() {
        var vocabularies_url = "/ui/get_common_vocabularies/";
        console.log("_do_vocabulary_choices()" + vocabularies_url);
        load_url(vocabularies_url, _build_vocabulary_choices);
    }

    function _set_function_value() {
        _function_name = document.getElementById("etmm_function_choice").value;
        console.log("FUNCTION " + _function_name);
    }


    function _build_function_choices(json_list) {
        var select_fragment  = document.getElementById("etmm_function_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
        if (json_list.length > 0) {
                _function_name = json_list[0].name; 
        }
        select_fragment.addEventListener('change', _set_function_value, false); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].name;
            option_fragment.text=json_list[i].name;
            select_fragment.appendChild(option_fragment);
            if (i==0) {
                option_fragment.selected = true;
            }
        }
    }

    function _do_function_choices() {

        if (_study_id)  {
            console.log("edit_table_mapping._do_function_choices()")
            var functions_url = "/ui/get_mapping_functions/" + _study_id + "/";
            console.log("_do_function_choices()" + functions_url);
            load_url(functions_url, _build_function_choices);
        }
    }

    function _clear_column_choices() {
        var select_fragment  = document.getElementById("etmm_column_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
    }

    function _set_column_value() {
        _column_name = document.getElementById("etmm_column_choice").value;
        console.log("COLUMN:" + _column_name);
    }

    function _build_column_choices(json_list) {
        var select_fragment  = document.getElementById("etmm_column_choice");
        _clear_column_choices();
        if (json_list.length > 0) {
                _column_name =  json_list[0].column_name;
        }
        select_fragment.addEventListener('change', _set_column_value, false);  // CR
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].column_name;
            option_fragment.text=json_list[i].column_name;
            select_fragment.appendChild(option_fragment);
            if (i==0) {
                option_fragment.selected = true;
            }
        }
    }

    function _do_column_choices() {
        _table_name = document.getElementById("etmm_table_choice").value;
        console.log("edit_table_mapping._do_column_choices()" + _table_name);

        _table_choice_cb(_table_name);

        var columns_url = "/ui/get_columns_for_study_table/" + _study_id + "/" + _table_name + "/";
        load_url(columns_url, _build_column_choices);
    }

    function _build_table_choices(json_list) {
        _clear_column_choices();
        var select_fragment  = document.getElementById("etmm_table_choice");
        while (select_fragment.length > 0) {
            select_fragment.remove(0);
        }
        if (json_list.length > 0) {
            _table_name = json_list[0].table_name;
            _table_choice_cb(_table_name);
        }
        select_fragment.addEventListener('change', _do_column_choices, false); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].table_name;
            option_fragment.text=json_list[i].table_name;
            select_fragment.appendChild(option_fragment);
            if (i==0) {
                option_fragment.selected = true;
            }
        }
        //option_fragment.change();
        // select first table, trigger _do_column_choices()
        var columns_url = "/ui/get_columns_for_study_table/" + _study_id + "/" + _table_name + "/";
        load_url(columns_url, _build_column_choices);
    }
 
    function _do_table_choices() {
        console.log("edit_table_mapping._do_table_choices()" + _study_id);
        var study_url = "/ui/get_tables_for_study/" + _study_id;
        load_url(study_url, _build_table_choices);
    }
   
    function get_study_id_update(study_id) {
        console.log("edit_table_mappings:" + study_id);
        _study_id = study_id;
        _do_table_choices();
        _do_function_choices();
    } 

    function init() {
        console.log("edit_table_mapping.init()")
        _do_vocabulary_choices();

        var insert_button = document.getElementById("etmm_insert_button");
        insert_button.addEventListener('click', _do_insert_button, false); 

        var delete_button = document.getElementById("etmm_delete_button");
        delete_button.addEventListener('click', _do_delete_button, false); 

        var edit_button = document.getElementById("etmm_edit_button");
        edit_button.addEventListener('click', _do_edit_button, false); 

        document.getElementById("etmm_concept_string").value = initial_search_term;
        _vocabulary_choice = initial_vocabulary_choice;
        _do_search_button();
    }

    return {
        get_study_id_update,
        init
    };
};
