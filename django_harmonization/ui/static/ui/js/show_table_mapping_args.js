/****
module: show_table_mapping_args
prefix: stmam

********* TODO **************

****/

var createShowTableMappingArgsModule = function(arg_selected_cb) {

    let _arg_selected_cb = arg_selected_cb;
    let _study_id=1;
    let _from_table=""
    let _from_column=""
    let _function_name=""
    let _from_where_column=""
    let _from_where_clause=""
    let _args_json_list = []

    function get_row_key_update(study_id, from_table, from_column, function_name, from_where_column, from_where_clause,
        vocabulary_id, concept_code, to_table, to_column) {
        console.log("edit study id: " + study_id + " table: " + from_table + " " + from_column + " " + function_name + " " + from_where_column + " " + from_where_clause
            + " v:"   + vocabulary_id  + " c:" + concept_code + " " + to_table + " " + to_column) 
        var the_div = document.getElementById("stmam_row_key_div");
        if (the_div) {
            the_div.innerHTML = "<b>Table:</b> " + from_table + " <b>Column:</b>" + from_column + " <b>Fn:</b>" + function_name 
                + " <b>Where Column:</b>" + from_where_column + " <b>Where Value:</b>" + from_where_clause;
        }

        _study_id=study_id
        _from_table=from_table
        _from_column=from_column
        _function_name=function_name
        _from_where_column=from_where_column
        _from_where_clause=from_where_clause

        _do_functions();
    }

    function _shorten_table_name(long_name) {
        // lop of the schema name by splitting on the period
        return long_name.substring(long_name.indexOf(".") + 1)
    }

    function _get_concept_name_and_populate_dom(vocabulary_id, concept_code, target_div_id) {
        console.log("_get_concept_details()");
        url = "/ui/get_concept_by_vocab_and_concept_code/" + vocabulary_id + "/" + concept_code + "/";

        function _add_concept_details(json_list) {
            console.log("_get_concept_details()._add_concept_details() " + json_list.length 
                       + " " + json_list[0].concept_name + " " + target_div_id);
            var target_div = document.getElementById(target_div_id);
            //target_div.innerHTML = json_list[0].concept_name;
            target_div.innerText = json_list[0].concept_name;
        }

        load_url(url, _add_concept_details)
    }

    function _build_arguments_table(json_list) {

        _args_json_list = json_list;
        var the_div = document.getElementById("stmam_rows_div");
        if (!the_div) {
            console.log("XXXX  stmam_rows_div")
        }
        if (json_list.length > 0) {
              var html_string = "<table  border=0 >"
              html_string += "<thead>";
              html_string += "<tr>"
              html_string += "<th>select</th>"
              html_string += "<th>Study ID</th>"
              html_string += "<th>Table</th><th>Column</th><th>Function</th>"
                
              if (json_list[0] && json_list[0].transform_factor != null  && json_list[0].transform_shift != null ) {
                html_string += "<th>factor</th>"
                html_string += "<th>shift</th>"
              } else {
                if (json_list[0].mapped_string != null) {
                    html_string += "<th>String</th>"
                }
                if (json_list[0].mapped_number != null) {
                    html_string += "<th>Number</th>"
                }
                if (json_list[0].mapped_concept_code != null) {
                    html_string += "<th>Vocabulary</th>"
                    html_string += "<th>Concept ID</th>"
                }

                html_string += "<th>Vocabulary</th>"
                html_string += "<th>Concept</th>"
                html_string += "<th>Concept Name</th>"
              }
              html_string +="</tr>"
              html_string += "</thead>";
              html_string += "<tbody>"
              for (var i=0; i<json_list.length; i++) {
                  let short_table_name = _shorten_table_name(json_list[i].from_table)
                  button_id =  "stmam_button_" + i
                  html_string += "<tr>"
                               + "<td>" + "<input type=\"checkbox\" value=\"" + i + "\" id=\"" + button_id  + "\"> </input>" + "</td>"
                               + "<td>" + json_list[i].study_id + "</td>"
                               + "<td>" + short_table_name  + "</td>"
                               + "<td>" + json_list[i].from_column  + "</td>"
                               + "<td>" + json_list[i].function_name + "</td>"
                  if (json_list[i] && json_list[i].transform_factor != null  && json_list[i].transform_shift != null ) {
                      html_string += "<td>" + json_list[i].transform_factor + "</td>"
                               + "<td>" + json_list[i].transform_shift + "</td>"
                  } else {
                      if (json_list[0].mapped_string != null) {
                          html_string += "<td>" + json_list[i].mapped_string + "</td>"
                       }
                       if (json_list[0].mapped_number != null) {
                          html_string += "<td>" + json_list[i].mapped_number + "</td>"
                       }
                       if (json_list[0].mapped_concept_code != null) {
                          html_string += "<td>" + json_list[i].mapped_concept_vocabulary_id + "</td>"
                               + "<td>" + json_list[i].mapped_concept_code + "</td>"
                       }
                       html_string +=  "<td>" + json_list[i].to_concept_vocabulary_id + "</td>"
                                     + "<td>" + json_list[i].to_concept_code + "</td>"
                                     + "<td><div id=\"stmam_argument_vocab_name_" + i + "\">(promises, promises)</td>"
                  }
          
                  console.log("i " + JSON.stringify(json_list[i]))
              } 
              html_string += "</tbody></table>";
              the_div.innerHTML = html_string;
            
              for (var i=0; i<json_list.length; i++) {
                  button_id =  "stmam_button_" + i
                  button = document.getElementById(button_id);
                  console.log("=================:" + i + ":" + _args_json_list.length + ":" + JSON.stringify(_args_json_list[i]));
                  let json_map = _args_json_list[i];
                    function local_cb(key) {
                        const j=i
                        const local_json_map = json_map
                        arg_selected_cb(local_json_map);
                    }
                  button.addEventListener('click', local_cb, false); 


                  div_id = "\"stmam_argument_vocab_name_" + i + "\"" 
                  the_div = document.getElementById(div_id)
// promises, promises, CR TODO need to work out either some brutal synch. execution here, or promises so
// that the update to the_div.innerHTML happens only after the dom is populated with it.
//                  //_get_concept_name_and_populate_dom( json_list[i].to_concept_vocabulary_id,
//                  //      json_list[i].to_concept_code, div_id)
              }
    
              var status_div = document.getElementById("stmam_status");
        } else {
            the_div.innerHTML = "<br> (no args) <br>"
            status_div.innerHTML = " (no args)  "
        }
       };
  
      function _do_functions() {
    
          console.log("show_table_mapping_args._do_table_choices()" + _study_id);
            if (_from_where_column && _from_where_clause ) {
                console.log("both");
                var mapping_arguments_url = "/ui/get_study_mapping_arguments"  
                    + "/" + _study_id 
                    + "/" + _from_table
                    + "/" + _from_column
                    + "/" + _function_name
                    + "/" + _from_where_column
                    + "/" + _from_where_clause + "/"
                load_url(mapping_arguments_url, _build_arguments_table);
                var status_div = document.getElementById("stmam_status");

            } else {
                console.log("not both");
                var mapping_arguments_url = "/ui/get_study_mapping_arguments"  
                    + "/" + _study_id 
                    + "/" + _from_table
                    + "/" + _from_column
                    + "/" + _function_name
                    + "/";
                load_url(mapping_arguments_url, _build_arguments_table);
                var status_div = document.getElementById("stmam_status");
            }
      }
   
    function init() {
        console.log("show_table_mapping_args.init()");
    }

    return {
        get_row_key_update,
        init
    };
};
