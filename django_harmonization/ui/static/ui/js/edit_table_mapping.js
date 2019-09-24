/****
module: edit_table_mapping
prefix: etmm

****/

var createEditTableMappingModule = function(table_choice_cb) {


    const INITIAL_SEARCH_TERM = 'heart';
    const INITIAL_VOCABULARY_CHOICE = 'LOINC';
    var _table_choice_cb = table_choice_cb;
    const _from_where_clause = '';
    const _from_where_column = '';
    var _study_id;
    var _table_name;
    var _column_name;
    var _vocabulary_choice;
    var _concept_choice_id; // an OHDSI concept_id, not the vocabulary's id called concept_code in OHDSI
    var _function_name ; 
    var select_div = $("#etmm_select_columns_div")[0];

    function _do_concept_select() {
        var select_fragment  = $("#etmm_concept_choice")[0]; // JQ
        _concept_choice_id = select_fragment.options[select_fragment.selectedIndex].value ;       
    }

    function _build_concept_choices(json_list) {
        console.log("_build_concept_choices() got " + json_list.length)

        $(".etmm_concept_choices").remove(); 
        if (json_list.length > 0) {
            _concept_choice_id = json_list[0].concept_id;
        }
        var select_fragment  = $("#etmm_concept_choice")[0];
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].concept_id;
            option_fragment.text=json_list[i].concept_code + " \"" + json_list[i].concept_name + "\"" ;
            $(option_fragment).addClass("etmm_concept_choices");
            select_fragment.appendChild(option_fragment);

            $(select_fragment).on('change', _do_concept_select);
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
        
        to_table = $("#etmm_to_table_choice").val();
        to_column = $("#etmm_to_column_choice").val();

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
        // url(r'^put_ohdsi_mapping/(?P<study_id>\d+)/(?P<from_table>[\w.]+)/(?P<from_column>\w+)
        //       / /(?P<function_name>\w+)/(?P<concept_id>\d+)/(?P<to_table>\w+)/(?P<to_column>[\w_]+)/$', 
        var _to_table = $("#etmm_to_table_choice").val();
        var _to_column = $("#etmm_to_column_choice").val();
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
        _vocabulary_choice = $("#etmm_vocabulary_choice").val();
        mapped_checkbox_value = $("#etmm_concept_mapped_checkbox").prop('checked');
        extract_checkbox_value = $("#etmm_concept_extract_checkbox").prop('checked');
        console.log("checkboxes:" + mapped_checkbox_value + " "  + extract_checkbox_value);
        if (_vocabulary_choice == null || _vocabulary_choice == '') {
            _vocabulary_choice = INITIAL_VOCABULARY_CHOICE;
        }
        var search_term_input = $("#etmm_concept_string").val();
        console.log("------ do_search_button()" + search_term_input + ", " + _vocabulary_choice);
        var vocabularies_url = "/ui/get_concepts_like/" + _vocabulary_choice + "/" + search_term_input + "/" 
            + mapped_checkbox_value + "/" + extract_checkbox_value + "/";
        load_url(vocabularies_url, _build_concept_choices);
    }

    function _build_vocabulary_choices(json_list) {
        var select_fragment  = $("#etmm_vocabulary_choice")[0];
        $(".etmm_vocabulary_choices").remove(); 
        if (json_list.length > 0) {
                _vocabulary_choice = json_list[0].name; 
        }
        //select_div.addEventListener('click', _do_column_choices, false); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i];
            option_fragment.text=json_list[i];
            $(option_fragment).addClass("etmm_vocabulary_choices");
            select_fragment.appendChild(option_fragment);
            if (i==0) {
                option_fragment.selected = true;
            }
        }

        $("#etmm_concept_button").on('click', _do_search_button); 
        $("#etmm_concept_string").on('change', _do_search_button); 
    }

    function _do_vocabulary_choices() {
        var vocabularies_url = "/ui/get_common_vocabularies/";
        load_url(vocabularies_url, _build_vocabulary_choices);
    }

    function _build_function_choices(json_list) {
        var select_fragment  = $("#etmm_function_choice")[0];
        $(".etmm_function_choices").remove(); 
        if (json_list.length > 0) {
                _function_name = json_list[0].name; 
        }
        $(select_fragment).on('change',
            function()  { _function_name = $("#etmm_function_choice").val(); }
        ); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].name;
            option_fragment.text=json_list[i].name;
            $(option_fragment).addClass("etmm_function_choices"); 
            select_fragment.appendChild(option_fragment);
            if (i==0) {
                option_fragment.selected = true;
            }
        }
    }

    function _do_function_choices() {

        if (_study_id)  {
            var functions_url = "/ui/get_mapping_functions/" + _study_id + "/";
            load_url(functions_url, _build_function_choices);
        }
    }

    function _build_column_choices(json_list) {
        var select_fragment  = $("#etmm_column_choice")[0];
        $(".etmm_column_choices").remove(); 
        if (json_list.length > 0) {
                _column_name =  json_list[0].column_name;
        }
        $(select_fragment).on('change', 
            function() { _column_name = $("#etmm_column_choice").val(); } )
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].column_name;
            option_fragment.text=json_list[i].column_name;
            $(option_fragment).addClass("etmm_column_choices");
            select_fragment.appendChild(option_fragment);
            if (i==0) {
                option_fragment.selected = true;
            }
        }
    }

    function _do_column_choices() {
        _table_name = $("#etmm_from_table_choice").val();
        _table_choice_cb(_table_name);
        var columns_url = "/ui/get_columns_for_study_table/" + _study_id + "/" + _table_name + "/";
        load_url(columns_url, _build_column_choices);
    }

    function _build_table_choices(json_list) {
        $(".etmm_from_table_choices").remove(); 
        var select_fragment  = $("#etmm_from_table_choice")[0];
        if (json_list.length > 0) {
            _table_name = json_list[0].table_name;
            _table_choice_cb(_table_name);
        }
        $(select_fragment).on('change', _do_column_choices); 
        for (var i=0; i<json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].table_name;
            option_fragment.text=json_list[i].table_name;
            option_fragment.class="etmm_from_table_choices";
            $(option_fragment).addClass("etmm_from_table_choices"); 
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
        var study_url = "/ui/get_tables_for_study/" + _study_id;
        load_url(study_url, _build_table_choices);
    }
   
    function get_study_id_update(study_id) {
        _study_id = study_id;
        _do_table_choices();
        _do_function_choices();
    } 

    function _get_concept_name_for_update(vocabulary_id, concept_code, option_ele) {
        url = "/ui/get_concept_by_vocab_and_concept_code/" + vocabulary_id + "/" + concept_code + "/";

        load_url(url, function (json_list) {
                option_ele.text = concept_code + " " + json_list[0].concept_name;
        });
    }

    function get_row_key_update(from_table, from_column, function_name, from_where_column, from_where_clause,
        vocabulary_id, concept_code, to_table, to_column) {
        console.log("edit table: " + from_table + " " + from_column + " " + function_name + " " + from_where_column + " " + from_where_clause
            + " v:"   + vocabulary_id  + " c:" + concept_code + " " + to_table + " " + to_column) 

        $(".etmm_from_table_choices[value=\"" + from_table + "\"]").prop('selected', true); // redundant and the periods cause problems
        $(".etmm_column_choices[value=\"" + from_column + "\"]").prop('selected', true);
        $(".etmm_function_choices[value=\"" + function_name + "\"]").prop('selected', true);
        $(".etmm_vocabulary_choices[value=\"" + vocabulary_id + "\"]").prop('selected', true); // UCD.Kao has a period
        $(".etmm_to_table_choices[value=\"" + to_table + "\"]").prop('selected', true);
        $(".etmm_to_column_choices[value=\"" + to_column + "\"]").prop('selected', true);

        // clear the search term
        $("#etmm_concept_string").val("");

        // why? I think because you don't fetch the whole list to show just the one that's been selected.
        // must add this concept to the select
        var concept_select_ele = $("#etmm_concept_choice")[0];
        var concept_option_ele = document.createElement('option');
        concept_option_ele.value=9999
        concept_option_ele.text=concept_code
        concept_option_ele.id= "etmm_concept_choice_" + concept_code;
        concept_select_ele.appendChild(concept_option_ele);
        concept_option_ele.selected = true;


        _get_concept_name_for_update(vocabulary_id, concept_code, concept_option_ele)
    }
        

    function init() {
        console.log("edit_table_mapping.init()")
        _do_vocabulary_choices();

        $("#etmm_insert_button").on('click', _do_insert_button); 
        $("#etmm_delete_button").on('click', _do_delete_button); 
        $("#etmm_edit_button").on('click', _do_edit_button); 

        $("#etmm_concept_string").val(INITIAL_SEARCH_TERM);
        _vocabulary_choice = INITIAL_VOCABULARY_CHOICE;
        _do_search_button();
    }

    return {
        get_study_id_update,
        init,
        get_row_key_update
    };
};
