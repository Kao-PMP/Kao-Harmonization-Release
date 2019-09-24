/****
module: reports
prefix: rm
****/

/* "use strict"; */


var createReportsModule = function() {
    var dbname;
    var message_div;
    var studyChoiceModule;
    var extractStudyChoiceModule;
    var study_id;
    var extract_study_id;

    function sleep(milliseconds) {
        var start = new Date().getTime();
        for (var i = 0; i < 1e7; i++) {
            if ((new Date().getTime() - start) > milliseconds){
                break;
            }
        }
    }


    function get_fetch_url_promise_2(url) {
        var return_name = ' - ';
        var dict = { 
            headers:{ 'Accept':'application/json', 'X-Requested-With':'XMLHttpRequest'}
        };
        return fetch(url, dict)
            .then(response => { return response.text()})
            .then(text_response => { return JSON.parse(text_response) }) 
    }


    /**
     * like load_url, but calling fetch() using promises rather than hiding them
     * This function layers some promises on top of what comes back from fetch that
     * get the response text and parse the JSON. It returns a promise that will call
     * a supplied function with parsed JSON data.
     **/ 
    function get_fetch_url_promise(url) {
        var dict = { 
            headers:{ 'Accept':'application/json', 'X-Requested-With':'XMLHttpRequest' }
        };
        var p = fetch(url, dict).then( async function(response) { 
                if (response) {
                    if (!response.ok) { 
                        for (var x in response) { console.log("get_fetch_url_promise() response property:" + x); }
                        var responseText = await response.text();
                        console.log("pipeline.get_fetch_url_promise() Error 1:" + responseText)
                        console.log("pipeline.get_fetch_url_promise() Error 1: (no value, reponse not OK)")
                    message_div.innerHTML = message_div.innerHTML + "<br>" +  url + "  " + responseText;
                        message_div.innerHTML = message_div.innerHTML + "<br>" +  url 
                        throw Error(responseText); 
                    } 
                    else { 
                        console.log("get_fetch_url_promise() SUCCESS: " +  url  + " " + response.statusText);
                        if (response["text"]) {
                            console.log("...text" +  url);
                            if (response.text) {
                                console.log("...text" +  url  + " " + response.text);
                                var responseText = await response.text();
                                if (responseText) {
                                    console.log("pipeline.get_fetch_url_promise() " + url + " success:" + responseText)
                                } else {
                                    console.log("pipeline.get_fetch_url_promise() " + url + " success: null text")
                                }
                            }
                            else {
                                console.log("...text null" +  url);
                            }
                        }
                        var message =  "SUCCESS: " +  url  + " " + response.statusText
                        message_div.innerHTML = message_div.innerHTML + "<br>" + message
                        console.log("..." + message);
                        return message;
                    }
                } else { 
                    var message = "pipeline.get_fetch_url_promise() Error 2: (no value) " + url
                    console.log(message)
                    message_div.innerHTML = message_div.innerHTML + "<br>" + message
                    return message;
                }
        });

        var q = p.then(response => { 
            if (response && response["text"] && response.text) {
                return JSON.parse(response.text); 
            } else {
                var message = "get_fetch_url_promise() " + url + "  had null response.text (so we're not parsing it as JSON)";
                console.log(message);
                return  message
            }
        });
        return q;
    }
  
    
    async function migrate() {
        // var study_name = document.getElementById("pm_migrate_study").value;
        var migrate_button = document.getElementById("pm_migrate_button");

        var study_name =  await get_study_name(study_id)

        var url =  "/ui/run_migrate/" + study_name + "/"
        var status_div = document.getElementById("pm_migrate_message");
        status_div.innerHTML= "running"
        var p = get_fetch_url_promise(url)
        if (p) {
            p.then(
                x => { 
                    console.log(" migrate  complete"); 
                    status_div.innerHTML= "COMPLETE"
                })
                .catch(err => {
                    console.log(" migrate failed." + err); 
                    status_div.innerHTML= "FAILED " + err
                });
        } else {
            console.log("  migrate failed 2." + url); 
            status_div.innerHTML= "FAILED 2 " + url
        }

        var status=0;
        p.catch(err => { console.log("migrate failed"); status=1;})
        await p;
        if (status == 0) {
            console.log(" done migrate");
        } else {
            console.log(" failed migrate:");
        }
    }

   function report_cb() {
        report_type_id =get_checked_radio_button_id("rm_report_type")
        var report_type = document.getElementById(report_type_id).value 

        var detail_val; 
        if ($("#rm_detail").is(":checked")) {
            detail_val = 'True'
        }
        else {
            detail_val = 'False';
        }

        var used_val;
        if  ($("#rm_used").is(":checked")) {
            used_val = 'True';
        }
        else {
            used_val = 'False';
        }

        var base_url = "/ui/spreadsheet_params/" 
        if (report_type == 'HTML') {
            base_url = "/ui/spreadsheet_params_html/" 
        }

        var url = base_url
            + report_type + "/" 
            + extract_study_id + "/" 
            + detail_val + "/"
            + used_val + "/";
        console.log("show_extract_mappings.get_extract_study_id_update() " + url);
        window.open(url, '_blank');
    }
    

    function init() {
        console.log("init");
        message_div = document.getElementById("pm_message");

        $("#rm_report_button").on('click', report_cb); 

        extractStudyChoiceModule = createExtractStudyChoiceModule(
            function(new_extract_study_id) {
                console.log("pipeline.createExtractStudyChoiceModule()'s CB:   got a study_id:\"" + new_extract_study_id + "\"");
                extract_study_id = new_extract_study_id
            }
        );  
    }

    return {
        init
    };
}
