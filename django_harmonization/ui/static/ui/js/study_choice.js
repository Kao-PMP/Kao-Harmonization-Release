/****
module: study_choice
prefix: scm
****/

var createStudyChoiceModule = function(study_id_callback) {

    function _change() {
        study_id=get_checked_radio_button("scm_study_choice");
        if (study_id != null && study_id != '') {
            study_id_callback(study_id);
        }
    }

    function _build_study_choices(json_list) {
        console.log("study_choice._build_study_choices() " + json_list.length);
        var choice_div = document.getElementById("scm_select_study_div");

        choice_div.addEventListener('change', _change, false);
        choice_div.addEventListener('click', _change(), false);

        var radio_html = "<table><tr><th>Study</th>";
        for (var i=1; i< json_list.length; i++) {
            radio_html += '<td><input type="radio" name="scm_study_choice"'
                + ' id="scm_study_choice_' + i + '"'
                + ' value="' + json_list[i].study_id + '"/> '
                + json_list[i].study_name  + " </td>"
        } 
        radio_html += "</tr>\n";

        radio_html += "<tr><th>Loaded</th>";
        for (var i=1; i< json_list.length; i++) {
            var status_html = '<td>'
                + '<div id="scm_study_migrate_status_' + json_list[i].study_id + '"> '
                + json_list[i].loaded
                + " </div></td>\n  "
            radio_html += status_html;
        }
        radio_html += "</tr>\n";

        radio_html += "<tr><th>Migrated</th>";
        for (var i=1; i< json_list.length; i++) {
            var status_html = '<td>'
                + '<div id="scm_study_migrate_status_' + json_list[i].study_id + '"> '
                + json_list[i].migrated
                + " </div></td>\n  "
            radio_html += status_html;
        }
        radio_html += "</tr>\n";

        radio_html += "<tr><th>Calculated</th>";
        for (var i=1; i< json_list.length; i++) {
            var status_html = '<td>'
                + '<div id="scm_study_calculate_status_'
                + json_list[i].study_id + '"> '
                + json_list[i].calculated
                + " </div></td>\n  "
            radio_html += status_html;
        }
        radio_html += "</tr></table>";

        var radio_fragment = document.createElement('span');
        radio_fragment.innerHTML = radio_html; 
        choice_div.append(radio_fragment);

        // initial value
        if (json_list.length > 1) {
            document.getElementById('scm_study_choice_1').checked=true;
            study_id_callback(json_list[1].study_id);
        }
    }
    
    function _do_study_choices() {
        var study_url = "/ui/get_all_studies/";
        load_url(study_url, _build_study_choices);
    }

    _do_study_choices();

    return {
    };
};
