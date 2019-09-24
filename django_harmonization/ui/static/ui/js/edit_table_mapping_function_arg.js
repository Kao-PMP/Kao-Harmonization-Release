/****
module: edit_table_mapping
prefix: etmm

****/

var createEditTableMappingFunctionArgModule = function() {

    function create_widgets(function_name, factor, shift, number, string, from_vocab, from_concept_code,
        to_vocab, to_concept_code) {

        console.log("TableMappingFunctionArgs.created_widgets(): " + function_name);
        switch(function_name) {
            case 'linear_equation':
                $("#etmfam_in")[0].innerHTML = "factor:<input>" + "shift:<input>";
                break;

            case 'map_number':
                $("#etmfam_in")[0].innerHTML = "number:<input>";
                break; 

            case 'map_string':
                $("#etmfam_in")[0].innerHTML = "string:<input>";
                break; 
    
            case 'map_concept_id':
                $("#etmfam_in")[0].innerHTML = "vocabulary:<input/> concept_code:<input/>";
                break;
    
            case 'identity':
                $("#etmfam_in")[0].innerHTML = "(not necessary)";
                break;
        }
        
    }

    function get_key_update(keymap) {
        console.log("edit function arg:" +  JSON.stringify(keymap));
        console.log("edit function arg:" + 
                    " study:" +    keymap['study_id'] +
                    " table:" +    keymap['from_table'] +
                    " col:"   +    keymap['from_column'] +
                    " fun:"   +    keymap['function_name'] +
                    " w col:" +    keymap['from_where_column'] +
                    " w cla:" +    keymap['from_where_clause'] + 
                    " m num:" +    keymap['mapped_number'] + 
                    " m str:" +    keymap['mapped_string'] + 
                    " m voc:" +    keymap['mapped_concept_vocabulary_id'] + 
                    " m con:" +    keymap['mapped_concept_code'] + 
                    " t fac:" +    keymap['transform_factor'] + 
                    " t sh:"  +    keymap['transform_shift'] + 
                    " to v:"  +    keymap['to_concept_vocabulary_id'] + 
                    " to c:"  +    keymap['to_concept_code'] 
        );
        $("#etmfam_from_table")[0].innerText = keymap['from_table'];
        $("#etmfam_from_column")[0].innerText = keymap['from_column'];
        $("#etmfam_function_name")[0].innerText=keymap['function_name'];

        if (keymap['from_where_column'] ||  keymap['from_where_clause']) {
            console.log("XXX where");
            $("#etmfam_where")[0].innerText= "where:" + keymap['from_where_column']
                + " value:" + keymap['from_where_clause'];
        }

        if (keymap['transform_factor'] || keymap['transform_shift']) {
            // TRANSFORM
            console.log("transform " + keymap['transform_factor'] + " " + keymap['transform_shift']);
            ele = $("#etmfam_in")[0]
            ele.innerText = "transform factor:" + keymap['transform_factor']
                + " transform shift:" + keymap['transform_shift'];
        } else if (keymap['mapped_number']) {
            // MAP NUMBER
            console.log("m.number");
            $("#etmfam_in")[0].innerText="number " + keymap['mapped_number'];
        } else if (keymap['mapped_string']) {
            // MAP STRING
            console.log("m.string");
            $("#etmfam_in")[0].innerText="string " + keymap['mapped_string'];
        } else if (keymap['mapped_concept_vocacbulary_id'] && keymap['mapped_concept_code']) {
            // MAP CONCEPT
            console.log("m.concept");
            $("#etmfam_in")[0].innerText="concept " + keymap['mapped_concept_vocacbulary_id']
             + " ," + keymap['mapped_concept_code'];
        }

        $("#etmfam_out_vocabulary_id")[0].innerText=keymap['to_concept_vocabulary_id'];
        $("#etmfam_out_concept_code")[0].innerText=keymap['to_concept_code'];

       create_widgets(keymap['function_name'], keymap['transform_factor'], keymap['transform_shift'], 
            keymap['mapped_number'], keymap['mapped_string'], 
            keymap['from_vocab'], keymap['from_concept_code'], keymap['to_concept_vocabulary_id'], keymap['to_concept_code']);
    }

    function init(cb) {
        console.log("edit_table_mapping_fn_arg.init()");
    } 

    return {
        init,
        get_key_update
    }
}
