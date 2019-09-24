/****
module: show_study_metrics_module
prefix: ssmm

****/

"use strict";
const prefix="ssmm";

    function c3LabelFormat(v, id, i, j) {
        return "yak";
    }

var createShowStudyMetricsModule = function() {

    let _study_id=1;
    let _tables_json=null;
    let _table_columns={};

    function get_study_id_update(study_id) {
        _study_id = study_id;

        const display_div = document.getElementById("ssmm_top");
        // clear out existing display
        while (display_div.hasChildNodes()) {
            display_div.removeChild(display_div.firstChild);
        }
        do_combined()
    }

    var create_chart_input = function(row, label, div_name) {
        // totally specific for data from get_study_value_by_table_column
        // This code gets one of two kinds of sets of rows:
        // One is n/min/avg/med/max, the other is just a series of categories.
        // Pluck out or calculate n as necessary, then add to the label.
        let columns_data = [label]
        let categories = []
        let n=0
        let sum=0

        let keyset = new Set(Object.keys(row)); 
        if (keyset.has('min')) { 
            var value_keys = Object.keys(row)
        } else {
            var value_keys = Object.keys(row).sort()
        }
        for (let index in value_keys) {
            let key = value_keys[index];
            if (key != 'n') {
                columns_data.push(row[key]);
                categories.push(key);
                sum = sum + row[key]
            } else {
                n = row[key];
            }
        }
        if (n==0) {
            columns_data[0] = columns_data[0] + ' n:' + sum;
        } else {
            columns_data[0] = columns_data[0] + ' n:' + n; 
        }
        let data = { columns: [columns_data], type: 'bar', labels:true};
        let attrs = { width: { ratio:0.5 } };
        let chart_input_data = { bindto:'#' + div_name, 
                            size: {width: 500, height: 200},
                            bar:{width:20},
                            padding:{right:10, bottom:0, left:100, top:10},
                            axis:{ x:{ padding:{left:0, right:0}, type: 'category', categories: categories, }},
            data, attrs}; 
        return(chart_input_data);
    }

    //// ONE GRAPH  TABLE
    function _do_column_stats(study_id, table_name, column_name, concept_code, parent_div) {
        const url = "/ui/get_study_value_by_table_column/" + study_id + "/" + table_name + "/" + column_name + "/";
        //nconsole.log(url);

        // create the div before the database call comes back, so it gets created with this call, no asynchronously later
        let clean_table_name = table_name.replace(/\./g,'_')
        let chart_div_name = "chart_column_stats_" + clean_table_name + "_" + column_name + "_" + concept_code;
        let column_fragment = document.createElement('span');
        let html = "<span id=\"" + chart_div_name + "\"></span>";
        column_fragment.innerHTML = html;
        parent_div.appendChild(column_fragment);

        load_url(url, 
            function(columns_json) {
                for (let i=0; i<columns_json.length; i++) {
                    let input=create_chart_input(columns_json[i], table_name + " " +  column_name,  chart_div_name);
                    c3.generate(input);
                }
            });
    }
    
    //////////////////////////////////////////////////////////////////////////////////////////

    var create_ohdsi_chart_input = function(rows, label, div_name) {
        // The data is raw rows and needs to be counted first
        // {newid: "HFACT00641", value_as_number: "36.3", value_as_string: null, value_as_concept_id: null, date: "2015-01-01"}


        // SUMMARIZE
        let values_dict={}
        let values_array=[]
        let n=0;    
        let sum=0; 
        let min=Number.MAX_SAFE_INTEGER;
        let max=0;
        let type="";
        for (let key in rows) {
            let row=rows[key]
            let as_number=null;
            if (row['value_as_number'] != null) {
                as_number = parseFloat(row['value_as_number']);
            }
            let as_string = row['value_as_string'];
            let as_concept = row['value_as_concept_id']
            let date = row['date'];
            if (as_number != null) {
                // console.log("number: ", label, row);
                type="number";
                if (values_dict[as_number]) {
                    values_dict[as_number] += 1;
                } else {
                    values_dict[as_number] = 1;
                }

                if (as_number > max) { max = as_number; }
                if (as_number < min) { min = as_number; }
                n += 1
                sum += parseInt(as_number)
                values_array.push(as_number)
            } else if (as_string != null) {
                // console.log("string: ", label, row);
                type="string"
                n += 1
                if (values_dict[as_string]) {
                    values_dict[as_string] += 1;
                } else {
                    values_dict[as_string] = 1;
                }
            } else if (as_concept != null) {
                // console.log("concept:", label, row);
                type="concept"
                n += 1
                if (values_dict[as_concept]) {
                    values_dict[as_concept] += 1;
                } else {
                    values_dict[as_concept] = 1;
                }
            }
        }

        // PREPARE FOR DISPLAY
        let columns_data = [label]
        let categories = []
        let value_keys = Object.keys(values_dict).sort()
        if (Object.keys(values_dict).length < 10) {
            for (let index in value_keys) {  
                var key = value_keys[index];
                categories.push(key); 
                columns_data.push(values_dict[key]);
            }
        } 
        else {
            // JS thinks the dates are numbers, so I'll use the string var that records where the value came from in OHDSI
            // if (typeof(values_dict[value_keys[0]]) == typeof(1) || typeof(values_dict[value_keys[0]]) == typeof(1.0)) {
            if (type == 'number') {
                // min/med/avg/max
                categories.push('min'); columns_data.push(min.toFixed(2));
                if (values_array.length > 0) {
                    let median=0;
                    let sorted=values_array.sort((a, b) => a - b);
                    //numArray.sort((a, b) => a - b);
                    if (values_array.length % 2 > 0 ) {
                        // odd, pick the middle value
                        let median_index = Math.floor(values_array.length/2) ;
                        median=sorted[median_index];
                    } else { 
                        // even, average the two middle values
                        let median_index = Math.floor(values_array.length/2) ;
                        median=(sorted[median_index -1] + sorted[median_index]) / 2.0;
                    }
                    categories.push('med'); columns_data.push(median.toFixed(5));
                }
                categories.push('avg'); columns_data.push((sum/n).toFixed(2));
                categories.push('max'); columns_data.push(max).toFixed(2);
            } else {
                // the values aren't numbers, so the values for min/max/avg are bogus
                categories.push('a_too'); columns_data.push(0);
                categories.push('b_many'); columns_data.push(0);
                categories.push('c_non_numerical'); columns_data.push(0);
                categories.push('d_values'); columns_data.push(n);
            }
        } 

        columns_data[0] = columns_data[0] + ' n:' + n; //  + " " + "  " + div_name;
        let data = { columns: [columns_data], type: 'bar', labels:true};
        let attrs = { width: { ratio:0.5 } };
        let chart_input_data = { bindto:'#' + div_name, 
                            size: {width: 500, height: 200},
                            bar:{width:20},
                            padding:{right:10, bottom:0, left:100, top:10},
                            axis:{ x:{ padding:{left:0, right:0}, type: 'category', categories: categories, }},
            data, attrs}; 
        return(chart_input_data);
    }

    //// ONE GRAPH OHDSI
    function _do_term_stats(study_id, vocabulary_id, concept_code, to_table, to_column, from_column, parent_div) {
        const url = "/ui/get_ohdsi_value_by_vocabulary_concept/" + study_id + "/" 
                    + vocabulary_id + "/" + concept_code + "/" + to_table + "/"
        console.log("show_study_metrics._do_term_stats()", url);

        // create the div before the database call comes back, so it gets created with this call, no asynchronously later
        let clean_vocab = vocabulary_id.replace(/\./g,'_')
        let chart_div_name = "chart_ohdsi_stats_" + clean_vocab + "_" + concept_code + "_" + from_column;
        let column_fragment = document.createElement('span'); 
        let html = "<span id=\"" + chart_div_name + "\"></span>";
        column_fragment.innerHTML = html;
        parent_div.appendChild(column_fragment);

        load_url(url, 
            function(columns_json) {
                let input=create_ohdsi_chart_input(columns_json, vocabulary_id + " " +  concept_code,  chart_div_name);
                c3.generate(input);
        });
    }

    //////////////////////////////////////////////////////////////////////////////////////////

    var debug_column_set = new Set(['pcangina', 'cvcad', 'diahis', 'cvduratn', 'group', 'eos_dt', 'pcsex', 'randate', 'brsex']);

    function _build_combined_by_table(json_list) {
        const top_div = document.getElementById("ssmm_top");
        for (let i=0; i<json_list.length; i++) {
            let row = json_list[i];
            //if (debug_column_set.has(row.from_column)) {

                let pair_fragment = document.createElement('div'); // <-------------------------------------- !!
                pair_fragment.innerHTML='<div id="row_div_' + i + '" class="border_style"></div>';
                top_div.appendChild(pair_fragment);
    
                if (row.from_column) {
                    _do_column_stats(row.study_id, row.from_table, row.from_column, row.concept_code, pair_fragment)
                } else {
                    console.log("STUDY ERROR", row);
                }
    
                if (row.concept_code) {
                    _do_term_stats(row.study_id,row.vocabulary_id, row.concept_code, row.to_table, row.to_column, row.from_column, pair_fragment); 
                } else {
                    let error_child = document.createElement('span');
                    error_child.innerHTML = "<span>No concept mapped for " + row.from_table + " " + row.to_table + ". This graph intentionally left blank.";
                    pair_fragment.appendChild(error_child); 
                    console.log("OHDSI ERROR", row);
                }
            //}
        }
    }

    function _do_combined_by_table(table_name) {
        let ohdsi_url = "/ui/get_mapping_for_study_table/" + study_id + "/" + table_name + "/";     
        load_url(ohdsi_url, _build_combined_by_table);
    }

    function _build_combined(tables_json) {
       _tables_json = tables_json; 
        for (let i=0; i<_tables_json.length; i++) {
            _do_combined_by_table(tables_json[i].table_name);
        }
    }

    function do_combined() {
        let ohdsi_url = "/ui/get_mapping_for_study/" + study_id + "/";
        load_url(ohdsi_url, _build_combined_by_table);
    }
    
    //////////////////////////////////////////////////////////////////////////////////////////
 
    function build_display() {
    }

    return {
        get_study_id_update,    
        c3LabelFormat
        
    };
}
