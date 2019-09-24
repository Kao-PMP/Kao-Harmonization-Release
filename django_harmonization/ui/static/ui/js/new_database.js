/****
module: new_database
prefix: ndm
****/

"use strict";

var createNewDatabaseModule = function() {
    var dbname;
    var message_div;

    function sleep(milliseconds) {
        var start = new Date().getTime();
        for (var i = 0; i < 1e7; i++) {
            if ((new Date().getTime() - start) > milliseconds){
                break;
            }
        }
    }

    /**
     * like load_url, but calling fetch() as fetch() should be used: with promises
     *
     * returns a promise that calls with the parsed string that came back from the REST call.
     * ...use the same callback you would with load_url() in utilities.js
     **/ 
    function get_fetch_url_promise(url) {
        var dict = { 
            headers:{ 'Accept':'application/json', 'X-Requested-With':'XMLHttpRequest'}
        };
        var p = fetch(url, dict).then(response => { 
                if (!response.ok) { 
                    var message = "url failure:" + url + " " + response.statusText;
                    console.log(message);
                    message_div.innerHTML = message;
                    throw Error(response.statusText); 
                } 
                else { 
                    return response.text();
                }
        });
        var q = p.then(response => { return JSON.parse(response); });
        return q;
    }
   
    function _create_step_promise(url, name, status_div) {
        var p = get_fetch_url_promise(url)
        if (p) {
            p.then(
                x => { 
                    console.log("  step \"" + name + "\" complete"); 
                    status_div.innerHTML= "COMPLETE"
                })
                .catch( err => {
                    console.log("  step \"" + name + "\" failed." + err); 
                    status_div.innerHTML= "FAILED"
                });
        } else {
            console.log("  step \"" + name + "\" failed 2." + err); 
            status_div.innerHTML= "FAILED 2"
        }

        return p;
    }

    async function start_pipeline() {
//        dbname = document.getElementById("ndm_database_name").value;
        dbname="heart_db" 
        var steps = [
            // chicken and egg until there is a starter database and way to deal with > 1
            //["/ui/create_db/" + dbname, "create db", "ndm_create_status" ],
            ["/ui/load_ohdsi/" + dbname + "/", 
                "load ohdsi", "ndm_ohdsi_status"], 
            ["/ui/load_studies/" + dbname + "/", 
                "load studies", "ndm_studies_status"], 
            ["/ui/load_mappings/" + dbname + "/", 
                "load mappings", "ndm_mapping_status"], 
        ];
        for (var i=0; i<steps.length ; i++) {
            var step = steps[i]
            var status_div = document.getElementById(step[2]);
            if (status_div) {
                status_div.innerHTML= ""
            } 
        }
        for (var i=0; i<steps.length ; i++) {
            var step = steps[i]
            console.log("starting step:" + step[1]);
            var status_div = document.getElementById(step[2]);
            status_div.innerHTML= "running"
            var p =  _create_step_promise(step[0], step[1], status_div);
            var status=0;
            p.catch(err => { console.log("step \"" + step[1] + "\" failed"); status=1;})
            await p;
            if (status == 0) {
                console.log(" done step:" + step[1]);
            } else {
                console.log(" failed step:" + step[1]);
                break;
            }
        }
    }

    function init() {
        message_div = document.getElementById("ndm_message");
        var button = document.getElementById("ndm_button");
        button.addEventListener('click', start_pipeline, false); 

        /**
        var test_button = document.getElementById("ndm_test_button");
        test_button.addEventListener('click', do_test, false); 
        **/
    }

    return {
        init
    };
}
