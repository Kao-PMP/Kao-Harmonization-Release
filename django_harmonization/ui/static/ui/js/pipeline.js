/****
module: new_database
prefix: ndm
****/

/* "use strict"; */


var createPipelineModule = function() {
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


    function test_ohdsi_load(the_div) {
        var url  = "/ui/get_concepts_like/SNOMED/heart/";
        try {
            load_url(url, function(json_list) {
                console.log("have_ohdsi=:" + json_list.length)
                if (json_list.length > 0) {
                    the_div.innerHTML = "true"
                } 
                else {
                    the_div.innerHTML = "false"
                }
            })
        }
        catch(x) {
            console.log("have_ohdsi=: NO " + x)
            the_div.innerHTML = "False"
        }
    }

    function test_studies_load(the_div) {
        console.log("test_studies_load()")
        var study_url = "/ui/get_all_studies/";
        var status_string = " Loaded Studies: "
        var status_bool=true
        try {
            load_url(study_url, function(study_json_list) {
                console.log("test_studies_load() function()")
                if (study_json_list.length > 0) {
                    for (var i=0; i< study_json_list.length; i++) {
                        var study_json = study_json_list[i]
                        var loaded_url = "/ui/get_study/"  + study_json.study_name + "/"
                        load_url(loaded_url, function(status_json_list) {
                            for (var j=0; j< status_json_list.length; j++) {
                                var status_json = status_json_list[j]
                                if (status_json.study_name != 'NULL') {
                                    status_string = status_string + status_json.study_name  + ":" + status_json.loaded + ", "
                                    status_bool = status_bool && (status_json.loaded == 'true')
                                }
                                the_div.innerHTML = status_bool
                                if (status_bool) {
                                    console.log("have_studies=: yes" + status_string)
                                    the_div.innerHTML = "loaded"
                                } else {
                                    console.log("have_studies=: no" + status_string + "  \"" + status_bool + "\"")
                                    the_div.innerHTML = status_string 
                                }
                            }
                        });
                    }
                } 
                else {
                    console.log("test_studies_load() function() no json")
                    the_div.innerHTML = "false"
                }
            });
        }
        catch(x) {
            console.log("test_studies_load() have_studies: no " + x)
            the_div.innerHTML = "False"
        }
        return status_string;
    }

    function test_mapping_load(the_div) {
        var mapping_url = "/ui/get_mapped_columns_for_study/1/";
        var status="-"
        try {
            load_url(mapping_url, function(json_list) {
                if (json_list.length > 0) {
                    status = "true"
                } else {
                    status = "false"
                }
                console.log("have_mappings=:" + status)
                the_div.innerHTML = status
            });
        }
        catch(x) {
            console.log("have_mappings=: error  no " + x)
            the_div.innerHTML = "False"
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
  
    function _create_step_promise(url, name, status_div) {
        var p = get_fetch_url_promise(url)
        if (p) {
            p = p.then(
                x => { 
                    console.log("  step \"" + name + "\" complete"); 
                    status_div.innerHTML= "COMPLETE"
                })
                .catch( err => {
                    console.log("  step \"" + name + "\" failed." + err + " url:" + url); 
                    status_div.innerHTML= "FAILED"
                });
        } else {
            console.log("  step \"" + name + "\" failed 2." + err + " " + url); 
            status_div.innerHTML= "FAILED 2"
        }

        return p;
    }

    const pipeline_steps = [
            // chicken and egg until there is a starter database and way to deal with > 1
            //["/ui/create_db/" + dbname, "create db", "pm_create_status", "/ui/get_db_status_but_chicken_egg" ],

            ["/ui/load_ohdsi/",    "load ohdsi",    "pm_ohdsi_status",    test_ohdsi_load], 
            ["/ui/load_mappings/", "load mappings", "pm_mapping_status",  test_mapping_load], 
            ["/ui/load_studies/",  "load studies",  "pm_studies_status",  test_studies_load], 
        ];

    //returns false on error
    async function _do_pipeline_step(i) {
            var pipeline_status_div = document.getElementById("pm_message")
            pipeline_status_div.innerHTML = "doing pipeline step " + pipeline_steps[i][1];
            console.log("_do_pipeline_step " + i + " " + pipeline_steps[i][1])
            var step = pipeline_steps[i]
            var status_div = document.getElementById(step[2]);
            status_div.innerHTML= "running"
            var p =  _create_step_promise(step[0], step[1], status_div);
            p.catch(err => { console.log("step \"" + step[1] + "\" failed"); status=1;})
            return(p)
    }

    async function _start_pipeline() {
        console.log("_start_pipeline()")

        dbname="heart_db_v2"  // TODO hard-coded db name!
// reconcile with the value in django settings.py!!!! TODO  
// reconcile with the environment variables!!! Yuk!!!


        //  dbname = document.getElementById("pm_database_name").value;

        for (var i=0; i< pipeline_steps.length ; i++) {
            var step = pipeline_steps[i]
            var status_div = document.getElementById(step[2]);
            if (status_div) {
                status_div.innerHTML= ""
            } 
        }


        await _do_pipeline_step(0);
        await _do_pipeline_step(1);
        await _do_pipeline_step(2);
    }

    async function get_study_name(study_id) {
        var study_name_url = "/ui/get_study_by_id/" + study_id + "/" ;
        var study_results_promise = get_fetch_url_promise_2(study_name_url) ;
        var r =  await study_results_promise
        return r[0].study_name
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
    

    async function calculate() {
        var study_name =  await get_study_name(study_id)
        var url =  "/ui/run_calculate/" + study_name + "/"
        var status_div = document.getElementById("pm_calculate_message");
        status_div.innerHTML= "running"

        var p = get_fetch_url_promise(url)
        if (p) {
            p.then(
                x => { 
                    console.log("pipeline.calculate()  complete" + x.message); 
                    //status_div.innerHTML= "COMPLETE " + x.message
                    status_div.innerHTML= "COMPLETE " +  JSON.stringify(x)
                })
                .catch( err => {
                    console.log("pipeline.calculate() failed." + err.message); 
                    status_div.innerHTML= "FAILED " + err.message + " " + JSON.stringify(err) 
                });
        } else {
            console.log("pipeline.calculate() failed 2." ); 
            status_div.innerHTML= "FAILED 2 "
        }

        var status=0;
        p.catch(err => { console.log("pipeline.calculate() failed" + err); status=1;})
        await p;
        if (status == 0) {
            console.log("pipeline.calculate() done calculate");
        } else {
            console.log("pipeline.calculate() failed calculate:");
        }
    }

    async function extract() {
        var study_name =  await get_study_name(study_id)
        var url =  "/ui/run_extract/" + study_name + "/" + extract_study_id + "/"
        var status_div = document.getElementById("pm_extract_message");
        status_div.innerHTML= "running"

        var p = get_fetch_url_promise(url)
        if (p) {
            p.then(
                x => { 
                    console.log(" extract  complete"); 
                    status_div.innerHTML= "COMPLETE"
                })
                .catch( err => {
                    console.log(" extract failed." + err); 
                    status_div.innerHTML= "FAILED"
                });
        } else {
            console.log("  extract failed 2." + err); 
            status_div.innerHTML= "FAILED 2"
        }

        var status=0;
        p.catch(err => { console.log("extract failed"); status=1;})
        await p;
        if (status == 0) {
            console.log(" done extract");
        } else {
            console.log(" failed extract:");
        }
    }

    function init() {
        console.log("init");
        message_div = document.getElementById("pm_message");

        // display status of pipeline steps
        for (var i=0; i< pipeline_steps.length ; i++) {
            var step = pipeline_steps[i]
           console.log("pipeline status " + step[2]);
           var status_div = document.getElementById(step[2])
            step[3](status_div)
        }

        var button = document.getElementById("pm_button");
        button.addEventListener('click', _start_pipeline, false); 

        var migrate_button = document.getElementById("pm_migrate_button");
        migrate_button.addEventListener('click', migrate, false); 

        var calculate_button = document.getElementById("pm_calculate_button");
        calculate_button.addEventListener('click', calculate, false); 

        var extract_button = document.getElementById("pm_extract_button");
        extract_button.addEventListener('click', extract, false); 

        var ohdsi_button = document.getElementById("pm_ohdsi_button")
        ohdsi_button.addEventListener('click', () => { _do_pipeline_step(0) }, false);

        var mapping_button = document.getElementById("pm_mapping_button")
        mapping_button.addEventListener('click', () => { _do_pipeline_step(1) }, false);

        var studies_button = document.getElementById("pm_studies_button")
        studies_button.addEventListener('click', () => { _do_pipeline_step(2) }, false);

        studyChoiceModule = createStudyChoiceModule(
            function(new_study_id) {
                console.log("pipeline.createStudyChoiceModule()'s CB:   got a study_id:\"" + new_study_id + "\"");
                study_id = new_study_id
            }
        );  
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
