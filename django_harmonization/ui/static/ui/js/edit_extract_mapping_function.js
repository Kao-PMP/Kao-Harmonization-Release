/****
module: edit_extract_mapping_function
prefix: eemfm

********* TODO **************

****/

var createEditExtractMappingFunctionModule = function() {

    let _extract_study_id=1;

    function _shorten_table_name(long_name) {
        // lop of the schema name by splitting on the period
        return long_name.substring(long_name.indexOf(".") + 1)
    }
      
    function _build_function_div(json_row) {
        var the_div = document.getElementById("eemfm_function_div");
        var html_string="<table><thead>";
       // html_string += "<tr><th>Name</th><th>Value</th></tr>";
        html_string += "</thead><tbody>"; 
        html_string += "<tr><th align=\"left\">Long Name:</th><td>" + json_row.long_name + "</td>"
                    + "<th align=\"left\">Short Name:</th><td>" + json_row.short_name + "</td></tr>";
        html_string += "<tr>"
                    + "<th align=\"left\">Function Name:</th><td>" + json_row.function_name + "</td>"
                    + "<th align=\"left\">Vocabulary:</th><td>" + json_row.from_vocabulary_id + "</td>"
                    + "<th align=\"left\">Concept:</th><td>" + json_row.from_concept_code + "</td></tr>";
        html_string += "<tr><th align=\"left\">from table:</th><td>" + json_row.from_table + "</td></tr>";
        html_string += "</tbody></table>";
        
        the_div.innerHTML = html_string;
    }

    function _get_concept_details(concept_id, i) {
        console.log("_get_concept_details()");
        url = "/ui/get_concept_by_id/" + concept_id + "/";

        function _add_concept_details(json_list) {
            console.log("_get_concept_details()._add_concept_details()");
            // i is in the scope...a true closure
            vocab_span = document.getElementById("eemfm_vocab_" + i);
            vocab_span.innerHTML = json_list[0].vocabulary_id;

            concept_id_span = document.getElementById("eemfm_concept_" + i);
            concept_id_span.innerHTML = json_list[0].concept_code;

            concept_name_span = document.getElementById("eemfm_concept_name_" + i);
            concept_name_span.innerHTML = json_list[0].concept_name;
        }

        load_url(url, _add_concept_details)
    }


    function _find_value_type(row) {
        // the number or value_limit value might be null and be the one, so default to that..
        value_type = 'number';
        if (row.from_string) {
            value_type = 'string';
        }
        if (row.from_concept_id) {
            value_type = 'concept';
        }
        return value_type;
    }

    function _build_parameters_div(json_list) {
        console.log("_build_parameters()")
        if (json_list.length > 0) {
            value_type = _find_value_type(json_list[0]);    
            var the_div = document.getElementById("eemfm_params_div");
            var html_string = "<table>"
            html_string += "<thead><tr>";
            if (value_type == 'number') {
                html_string += "<th>Value Limit</th>";
            }  
            if (value_type == 'string') {
                html_string += "<th>Value as String</th>";
            }
            if (value_type == 'concept') {
                html_string += "<th>Value as Concept</th>";
                html_string += "<th>Vocabulary/Concept</th>";
                html_string += "<th>Concept Name</th>";
            }
            html_string += "<th>Rank</th>";
            html_string += "</tr></thead><tbody>";
            
            for (var i=0; i<json_list.length; i++) {
                html_string += "<tr>"
                if (value_type == 'number') {
                    html_string += "<td>" + json_list[i].value_limit + "</td>";
                }
                if (value_type == 'string') {
                    html_string += "<td>" + json_list[i].from_string + "</td>";
                }
                if (value_type == 'concept') {
                    html_string += "<td>" + json_list[i].from_concept_id + "</td>";
                    html_string += "<td><span id=\"eemfm_vocab_" + i  + "\"></span>"
                                + "  <span id=\"eemfm_concept_" + i + "\"></span></td>";
                    html_string += "<td><span id=\"eemfm_concept_name_" + i + "\"></span></td>"; // id's used up in _get_concept_details() above
                }
                html_string += "<td>" + json_list[i].rank + "</td>";
                html_string += "</tr>"
            }
    
            html_string += "</tbody></table>";
            the_div.innerHTML = html_string;
    
            console.log("_build_parameters()" + html_string); 

            // now daisy-chain out and lookup, then display, the vocabulary_id and concept_code 
            // TODO might make this a FK join back in django, but for the composite key on vocabulary_id and concept_code
            for (var i=0; i<json_list.length; i++) {
                if (json_list[i].from_concept_id) {
                    _get_concept_details(json_list[i].from_concept_id, i);
                }
            }
        } else {
            var the_div = document.getElementById("eemfm_params_div");
            the_div.innerHTML ="";
        }
    }

    function _do_function_parameters(json_row) {
        var url = "/ui/get_categorization_function_parameters/" + json_row.extract_study + "/" + json_row.function_name + "/" + json_row.long_name + "/";
        console.log("edit_extract_mapping_functions._do_function_parameters() " + _extract_study_id + " " + url);
        load_url(url, _build_parameters_div);
    }

    function get_extract_study_id_update(extract_study_id) {
        _extract_study_id = extract_study_id;
    }
   
    function get_extract_function_row_choice(function_row_obj) {
        console.log("EditExtractMappingFunctionModule.get_extract_row_choice() " + JSON.stringify(function_row_obj));
        _build_function_div(function_row_obj);
        _do_function_parameters(function_row_obj);
    }

    function init() {
        console.log("edit_extract_mapping_function.init()")
    }

    return {
        get_extract_study_id_update,
        get_extract_function_row_choice,
        init
    };
};
