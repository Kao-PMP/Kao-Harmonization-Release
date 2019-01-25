/****
module: source_table_column
prefix: stcm
events: 
****/

'use strict';
// revealing module pattern extended to take arguments, module must be instantiated by user
// param: callback. A function to call when any of (study_id, table_id, column_id) change
//   signature:callback(study_id, table_id, column_id) 

var createSourceTableColumnModule = function(callback) {

    var _callback = callback;
    var _study_id;
    var _table_name;
    var _column_name;

    function things_changed() {
        console.log("calling createScourceTableColumnModule callback:" + _study_id + " " + _table_name + " " + _column_name)
        _callback(_study_id, _table_name, _column_name);    
        if (_column_name) {
            _do_check_for_actual_row()
            _do_check_for_mapping_row()
        }
    }

    function _do_column_chosen() {
        var column_name = document.getElementById("stcm_column_choice").value;
        _column_name = column_name;
        things_changed();
    }

    function _delete_column_choices() {
        var select_div = document.getElementById("stcm_select_columns_div");
        while (select_div.hasChildNodes()) {
            select_div.removeChild(select_div.firstChild);
        }
    }

    function _build_column_choices(json_list) {
        var select_div = document.getElementById("stcm_select_columns_div");
        var select_fragment = document.createElement("select");
        select_fragment.id = "stcm_column_choice";
        select_div.append(select_fragment);
        select_div.addEventListener('click', _do_column_chosen, false); 
        select_div.addEventListener('change', _do_column_chosen, false); 
        for (var i=0; i< json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].column_name;
            option_fragment.text=json_list[i].column_name;
            select_fragment.appendChild(option_fragment);
        } 
    }

    function _clear_actual_row() {
        var div = document.getElementById("stcm_existing_actual_row");
        div.innerHTML="";
    }
    
    function _clear_mapping_row() {
        var div = document.getElementById("stcm_existing_mapping_row");
        div.innerHTML = ''; 
    } 
    
   
    // table choice was made 
    function _do_column_choices() {
        _delete_column_choices();
        _clear_mapping_row();
        _clear_actual_row();
        _column_name=null;
        var study_id = get_checked_radio_button("stcm_study_choice");
        console.log(study_id)
        var table_name = document.getElementById("stcm_table_choice").value
        _table_name = table_name;
        things_changed();
        var study_url = "/ui/get_columns_for_study_table/" + study_id + "/" + table_name + "/"; 
        load_url(study_url, _build_column_choices);
    }


    function _build_check_for_actual_row(json_list) {
        var div = document.getElementById("stcm_existing_actual_row");
        var html_string='';
        if (json_list.length > 0) {
            //html_string = "Table:" + json_list[0].from_table + ", Column:" + json_list[0].from_column  + " Values:" + json_list[0].value;
            html_string = json_list[0].from_column + ": " + json_list[0].value;
        }
        for (var i=1; i< json_list.length; i++) {
            //html_string = html_string + json_list[i].id + " " + json_list[i].value;
            html_string = html_string + ", " + json_list[i].value;
        }
        div.innerHTML = html_string;
    }
    
    function _do_check_for_actual_row() {
        // look for Actual Data
        if (_study_id && _table_name && _column_name) {
            var data_url = "/ui/get_study_values/" + _study_id + "/" + _table_name + "/" + _column_name + "/";
            load_url(data_url, _build_check_for_actual_row);
        }
    }
    
   
    function _build_check_for_mapping_row(json_list) {
        var div = document.getElementById("stcm_existing_mapping_row");
        var html_string='';
        for (var i=0; i< json_list.length; i++) {
            html_string = html_string + json_list[i].study_id  
                + " [" + json_list[i].from_table
                + ", " + json_list[i].from_column
                + "] --> " + json_list[i].function_name
                + " --> [" + json_list[i].vocabulary_id
                + ", " + json_list[i].concept_code
                + " ] [" + json_list[i].to_table
                + ", " + json_list[i].to_column
                + "] <br>";
        }
        div.innerHTML = html_string;
    }
    
    
    function _do_check_for_mapping_row() {
        // look for Mapping Data
        var check_url = "/ui/get_mapping_for_study_table_column/" + _study_id + "/" + _table_name + "/" + _column_name + "/"; 
        load_url(check_url, _build_check_for_mapping_row);
    }
    
    
    function _build_table_choices(json_list) {

        var select_div = document.getElementById("stcm_select_tables_div");
        while (select_div.hasChildNodes()) {
            select_div.removeChild(select_div.firstChild);
        }
        select_div.addEventListener('change', _do_column_choices, false);
        select_div.addEventListener('click', _do_column_choices, false);
        var select_fragment = document.createElement("select")
        select_fragment.id = "stcm_table_choice"
        select_div.append(select_fragment)
        for (var i=0; i< json_list.length; i++) {
            var option_fragment = document.createElement('option');
            option_fragment.value=json_list[i].table_name;
            option_fragment.text=json_list[i].table_name;
            select_fragment.appendChild(option_fragment);
        } 
    }
    

    // study choice was made
    function _do_table_choices() {
        _delete_column_choices();
        _clear_mapping_row();
        _clear_actual_row();
        _table_name=null;
        _column_name=null;
        var _study_id=get_checked_radio_button("stcm_study_choice");
        console.log("source_table_column._do_table_choices()" + _study_id);
        things_changed();
        var study_url = "/ui/get_tables_for_study/" + _study_id;
        load_url(study_url, _build_table_choices);
    }
    
    return {
    };
};
