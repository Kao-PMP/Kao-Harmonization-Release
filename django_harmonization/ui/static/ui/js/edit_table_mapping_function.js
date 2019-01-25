/****
module: edit_table_mapping_function
prefix: etmfm

********* TODO **************

****/

var createEditTableMappingFunctionModule = function() {

    let _study_id=1;

    function _shorten_table_name(long_name) {
        // lop of the schema name by splitting on the period
        return long_name.substring(long_name.indexOf(".") + 1)
    }
      
    function _build_function_table(json_list) {
        //console.log(JSON.stringify(json_list))
        var the_div = document.getElementById("etmfm_div");
        var html_string = "<table class=\"scroll\">"
        html_string += "<thead>";
        html_string += "<tr>"
        html_string += "<th>Study ID</th>"
        html_string += "<th>Table</th><th>Column</th><th>Function</th>"
        html_string += "<th>Vocabulary</th>"
        html_string += "<th>Concept</th>"
        html_string +="</tr>"
        html_string += "</thead>";
        html_string += "<tbody>"
        for (var i=0; i<json_list.length; i++) {
            let short_table_name = _shorten_table_name(json_list[i].from_table)
            html_string += "<tr>"
                         + "<td>" + json_list[i].study_id + "</td>"
                         + "<td>"
                             + "<input type=\"checkbox\" value=\"" + i + "\""  
                             + "</input>"
                             + short_table_name  + "</td>"
                         + "<td>" + json_list[i].from_column  + "</td>"
                         + "<td>" + json_list[i].function_name + "</td>"
                         + "<td>" + json_list[i].vocabulary_id + "</td>"
                         + "<td>" + json_list[i].concept_code + "</td>"
    
        } 
        html_string += "</tbody></table>";
        //console.log(html_string)
        the_div.innerHTML = html_string;
     };

    function _do_functions() {
        console.log("edit_table_mapping_function._do_table_choices()" + _study_id);
        var study_url = "/ui/get_study_to_ohdsi_mapping_functions/" + _study_id;
        load_url(study_url, _build_function_table);
    }

    function get_study_id_update(study_id) {
        _study_id = study_id;
        _do_functions();
    }
   
    function init() {
        console.log("edit_table_mapping_function_module.init()")
        _do_functions();
    }

    return {
        get_study_id_update,
        init
    };
};
