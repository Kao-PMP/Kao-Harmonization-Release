/****
module: show_extract_mappings
prefix: semm
events: call to load_show_extract_mappings when the extract_study_id changes
****/


var createShowExtractMappingsModule =  function(extract_mapping_choice_cb) {
    const _prefix = "semm";
    let _json_list;
    const  _mapping_cb = extract_mapping_choice_cb;

    var get_extract_study_id_update = function(extract_study_id) {
        if (extract_study_id != null) {
            var url = "/ui/get_extract_mapping_list/" + extract_study_id + "/";
            console.log("show_extract_mappings.get_extract_study_id_update() " + url);
            load_url(url, _build_columns_for_extract_study);
        } else {
            console.log("no bueno" + study_id)
        }
    };

    function _radio_cb() {
        x = get_checked_radio_button("semm_mapping_row_choice_");
        console.log(_json_list[x]);
        console.log(_mapping_cb); 
        console.log(JSON.stringify(_mapping_cb));
        _mapping_cb(_json_list[x]);
    }

    function _get_concept_details(vocabulary_id, concept_code, i) {
        url = "/ui/get_concept_by_vocab_and_concept_code/" + vocabulary_id + "/" + concept_code + "/";
        console.log("_get_concept_details() " + url);

        function _add_concept_details(json_list) {
            //console.log("_get_concept_details()._add_concept_details() " + json_list.length);
            //console.log("XX:" + JSON.stringify(json_list[0]));
            // i is in the scope...a true closure

            concept_name_span = document.getElementById("semm_concept_name_" + i);
            concept_name_span.innerHTML = json_list[0].concept_name;
        }

        load_url(url, _add_concept_details)
    }

   
    function _build_columns_for_extract_study(json_list) {
        console.log("building...");
        _json_list = json_list;
        // console.log(JSON.stringify(json_list))
        name_base= _prefix + "_mapping_row_choice_" ;
        var the_div = document.getElementById("semm_show_extract_mappings_div");
        var html_string = "";
        html_string += "<table class=\"scroll\">";
        html_string += "<thead><tr>";
        html_string += "<th>Vocabulary/Concept</th>";
        html_string += "<th>Concept Name</th>";
        html_string += "<th>Table</th>";
        html_string += "<th>Column</th>";
        html_string += "<th>Function</th>";
        html_string += "<th>Name</th>";
        html_string += "<th>Short Name</th>";
        html_string += "</tr></thead>";
        html_string += "<tbody>";
        choice_class_name= _prefix + "_mapping_row_choice" ;
        name_base= _prefix + "_mapping_row_choice_" ;
        for (var i=0; i<json_list.length; i++) {
            id =  name_base  + i;
            html_string += "<tr><td>" 
                             //+ "<input value=\"" + i  + "\""
                             //+ " class=\"" + choice_class_name  + "\""
                             //+ " type=\"radio\"" 
                             //+ " name=\"" + name_base +  "\""
                             //+ " id=\"" + id +  "\">"
                         + json_list[i].from_vocabulary_id + "/" + json_list[i].from_concept_code 
                         //+ "</input>" 
                         + "</td>"
                + "<td>" + " <span id=\"semm_concept_name_" + i + "\"></span></td>"
                + "<td>" + json_list[i].from_table  + "</td>"
                + "<td>" + json_list[i].from_column + "</td>"
                + "<td>" + json_list[i].function_name + "</td>"
                + "<td>" + json_list[i].long_name + "</td>"
                + "<td>" + json_list[i].short_name + "</td>"
        } 
        html_string += "</tbody></table></select>";
        the_div.innerHTML = html_string;

        var select_div = document.getElementById("semm_show_extract_mappings_div");
        select_div.addEventListener('change', _radio_cb, false);

        for (var i=0; i<json_list.length; i++) {
            _get_concept_details(json_list[i].from_vocabulary_id, json_list[i].from_concept_code, i);
        }
     };

    console.log("show_extract_mappings.ctor()")
    return {
        get_extract_study_id_update
    };
}

