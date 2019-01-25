
/***
module:destination_concept_module
param: callback(concept_id)
prefix: dcm

To avoid  parsing a composite key of vocabulary_id:concept_code, this thing just returns a concept_id in the OHDSI universe. 
It probably means a lookup into the OHDSI concept table to get back to display-friendly vocabulary_id/concept_code.
***/
function createDestinationConceptModule(callback) {

    var _base_url = "/ui/get_concepts_like/";
    var _concept_id;
    var _vocabulary_id;
    var _concept_code;

    var button = document.getElementById("dcm_button");
    button.addEventListener('click', _do_concept_search, false); 

    var concept_div = document.getElementById("dcm_choice_box_div");
    concept_div.addEventListener('click', _do_concept_selected, false); 

    function _do_concept_selected() {
        _concept_id = get_checked_radio_button("dcm_concept_choice");
        mangled_code = get_checked_radio_button_id("dcm_concept_choice");
        _concept_code = mangled_code.substring(4);
        console.log("concept_selected: id:" + _concept_id + " mangled:" + mangled_code +  " code:" + _concept_code + " vocab:" + _vocabulary_id);
        
        callback(_concept_id, _vocabulary_id, _concept_code); 
    }

    function _build_concept_choice_buttons(json_list) {
        var choice_div = document.getElementById("dcm_choice_box_div");
    
        while (choice_div.hasChildNodes()) {
            choice_div.removeChild(choice_div.firstChild);
        }
        for (var i=0; i< json_list.length; i++) {
            // for scrollable list of buttons: https://select2.github.io/examples.html
            var radioHtml = '<input type="radio"'
                + ' name="dcm_concept_choice"'
                + ' value="' + json_list[i].concept_id + '"'
                + ' id="dcm_' + json_list[i].concept_code + '"/> '
                + json_list[i].concept_name + '" (' + json_list[i].vocabulary_id + ', '  + json_list[i].concept_code + ')';
            var radioFragment = document.createElement('div');
            radioFragment.innerHTML = radioHtml; 
            choice_div.append(radioFragment);
        } 
    };
    
    function _do_concept_search() { 
        _vocabulary_id = get_checked_radio_button("dcm_vocabulary_id");
        var search_string  =  document.getElementById("dcm_string").value ;
        var my_url  = _base_url + _vocabulary_id + "/" + search_string + "/";
        console.log("_do_concept_search() " + _vocabulary_id + " " + search_string + " " + my_url);

        load_url(my_url, _build_concept_choice_buttons);
    };

    function things_changed() {
    }

    return {
    }
}
