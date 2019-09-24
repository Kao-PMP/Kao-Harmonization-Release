
/***
    utilities
***/

function get_checked_radio_button(buttons_name) {
    var radio_buttons = document.getElementsByName(buttons_name);
    var value='';
    for (var i=0; i<radio_buttons.length; i++) {
        if (radio_buttons[i].checked) {
            value=radio_buttons[i].value;
            break;
        }
    }
    return value;
}

function get_checked_radio_button_id(buttons_name) {
    var radio_buttons = document.getElementsByName(buttons_name);
    var id='';
    for (var i=0; i<radio_buttons.length; i++) {
        if (radio_buttons[i].checked) {
            id=radio_buttons[i].id;
            console.log("radio button id:" + radio_buttons[i].name + " id:" + id );
            break;
        }
    }
    return id;
}

function set_selected_option(options_name) {
    console.log("SET SELECTED: " + options_name)
    var option_element = document.getElementById(options_name);
    option_element.selected = true
}

function load_url(url, callback) {
    console.log("load_url:" + url)
    dict = { 
        headers:{ 'Accept':'application/json', 'X-Requested-With':'XMLHttpRequest'}
    };
    fetch(url, dict)
        .then(response => { 
            if (response &&  response["text"]) {
                    var json_data="" // save in case of exception
                    response.text()
                        .then(function(data) { 
                            json_data=data
                            var json_data = JSON.parse(data);
                            callback(json_data);
                        })
                        .catch(function(x) { 
                            console.log("error in load_url " + url)
                            console.log("EXCEPTION:" + x)
                            console.log("JSON:\"" + json_data + "\"")
                            console.log(x.stack)
                        })
            }
            else {
                callback([])
                console.log("load_url() " + url + "  null response");     
            }   
        })
        .catch(err => {
            console.log("load_url() " + url + "  error");     
            document.getElementById("status_p").innerHTML = "status:" + " caught:" + err
            callback([])
        });
}

// from: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
// example call:
//     postData('http://example.com/answer', {answer: 42})
//       .then(data => console.log(data)) // JSON from `response.json()` call
//       .catch(error => console.error(error))
//     returns a future to hook the cb into...your deal
function post_url(url, data) {
  // Default options are marked with *
  return fetch(url, {
    body: JSON.stringify(data), // must match 'Content-Type' header
    cache: 'no-cache',
    // credentials: 'same-origin', // include, same-origin, *omit
    credentials: 'omit', // include, same-origin, *omit
    headers: {
      'user-agent': 'Mozilla/4.0 MDN Example',
      'content-type': 'application/json'
    },
    method: 'POST', 
    mode: 'cors', 
    redirect: 'follow', // manual, *follow, error
    referrer: 'no-referrer', // *client, no-referrer
  })
  .then(response => response.json()) // parses response to JSON
} 

//function put_url_w_data(url, data) {
//  return fetch(url, {
//    body: JSON.stringify(data), // must match 'Content-Type' header
//    cache: 'no-cache',
//    // credentials: 'same-origin', // include, same-origin, *omit
//    credentials: 'omit', // include, same-origin, *omit
//    headers: {
//      'user-agent': 'Mozilla/4.0 MDN Example',
//      'content-type': 'application/json'
//    },
//    method: 'PUT', 
//    mode: 'cors', 
//    redirect: 'follow', // manual, *follow, error
//    referrer: 'no-referrer', // *client, no-referrer
//  })
//  .then(response => response.json()) // parses response to JSON
//} 

function put_url(url) {
    console.log("PUT URL 1 " + url);
  return fetch(url, {
    //    body: JSON.stringify(data), // must match 'Content-Type' header
    cache: 'no-cache',
    // credentials: 'same-origin', // include, same-origin, *omit
    credentials: 'omit', // include, same-origin, *omit
    headers: {
      'user-agent': 'Mozilla/4.0 MDN Example',
      'content-type': 'application/json'
    },
    method: 'PUT', 
    mode: 'cors', 
    redirect: 'follow', // manual, *follow, error
    referrer: 'no-referrer', // *client, no-referrer
  })
  .then(response => response.text())
} 

function delete_url(url) {
    console.log("DELETE URL 1 " + url);
  return fetch(url, {
    //    body: JSON.stringify(data), // must match 'Content-Type' header
    cache: 'no-cache',
    // credentials: 'same-origin', // include, same-origin, *omit
    credentials: 'omit', // include, same-origin, *omit
    headers: {
      'user-agent': 'Mozilla/4.0 MDN Example',
      'content-type': 'application/json'
    },
    method: 'DELETE', 
    mode: 'cors', 
    redirect: 'follow', // manual, *follow, error
    referrer: 'no-referrer', // *client, no-referrer
  })
  .then(response => response.text())
} 

