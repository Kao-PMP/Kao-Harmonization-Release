/****
module: show_table_mappings
prefix: stmm
events: call to load_show_table_mappings when the vocabulary_id changes
****/

// https://addyosmani.com/resources/essentialjsdesignpatterns/book/#revealingmodulepatternjavascript

var createShowTableMappingsModule =  function(mapping_row_choice_cb) {

    const _prefix = "stmm";
    const _mapping_rows_choice_cb = mapping_row_choice_cb ;

    var _study_id=1;
    var _table_name=''; 


   function _clear() {
        var the_div = document.getElementById("stmm_show_table_mappings_div");
        the_div.innerHTML = "";
   }

    var get_study_id_update = function(study_id, table) {
        _study_id = study_id; 
        _clear();
    }

    var get_table_name_update = function(table_name) {
        console.log("_get_table_name_update() " + table_name);
        _table_name = table_name;

        var url = "/ui/get_mapped_columns_for_study_and_table/" + _study_id + "/" + table_name + "/";
        load_url(url, _build_columns_for_study);
    };

    function _shorten_table_name(long_name) {
        // lop of the schema name by splitting on the period
        return long_name.substring(long_name.indexOf(".") + 1)
    }

    function _get_concept_details(vocabulary_id, concept_code, i) {
        console.log("_get_concept_details()");
        url = "/ui/get_concept_by_vocab_and_concept_code/" + vocabulary_id + "/" + concept_code + "/";

        function _add_concept_details(json_list) {
            console.log("_get_concept_details()._add_concept_details() " + json_list.length);
            console.log("XX:" + JSON.stringify(json_list[0]));
            // i is in the scope...a true closure

            concept_name_span = document.getElementById("stmm_concept_name_" + i);
            concept_name_span.innerHTML = json_list[0].concept_name;
        }

        load_url(url, _add_concept_details)
    }

    function _build_columns_for_study(json_list) {
        console.log("_build_columns_for_study() " + json_list.length);
        //console.log(JSON.stringify(json_list))
        var the_div = document.getElementById("stmm_show_table_mappings_div");
        //var html_string = "<table class=\"scroll\" border=0>"
        var html_string = "<table class=\"scroll\">"
        html_string += "<thead>";
        html_string += "<tr>"
        html_string += "<th>Table</th><th>Column</th><th>Function</th>"
        html_string += "<th>Vocabulary/Concept</th>"
        html_string += "<th>Concept Name</th>"
        html_string += "<th>Table</th>"
        html_string += "<th>Column</th>"
        html_string +="</tr>"
        html_string += "</thead>";
        html_string += "<tbody>"

        choice_class_name= _prefix + "_mapping_row_choice" 
        for (var i=0; i<json_list.length; i++) {

            short_table_name = _shorten_table_name(json_list[i].from_table)
            html_string += "<tr>"
                         + "<td>"
                            // + "<input type=\"radio\" value=\"" + i + "\""
                            // + " class=\"" + choice_class_name + "\"" 
                            // + " name=\"" + choice_class_name + "\">" 
                            // + "</input>"
                             + short_table_name  + "</td>"
                         + "<td>" + json_list[i].from_column  + "</td>"
                         + "<td>" + json_list[i].function_name + "</td>"
                         + "<td>" + json_list[i].vocabulary_id + "/" + json_list[i].concept_code + "</td>"
                         + "<td>" + " <span id=\"stmm_concept_name_" + i + "\"></span></td>"
                         + "<td>" + json_list[i].to_table + "</td>"
                         + "<td>" + json_list[i].to_column + "</td>"
    
        } 
        html_string += "</tbody></table>";
        the_div.innerHTML = html_string;

        for (var i=0; i<json_list.length; i++) {
            _get_concept_details(json_list[i].vocabulary_id, json_list[i].concept_code, i);
        }
        
        for (e in document.getElementsByClassName(choice_class_name)) {
           e.click=_mapping_rows_choice_cb;
        }
     };

    console.log("show_table_mappings.ctor()")
    return {
        get_table_name_update,
        get_study_id_update
    };
}

