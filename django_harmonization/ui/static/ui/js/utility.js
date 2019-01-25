
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

function load_url(url, callback) {
    console.log("load_url:" + url)
    dict = { 
        headers:{ 'Accept':'application/json', 'X-Requested-With':'XMLHttpRequest',
            //	// TODO don't hardcode the security token
            //	'Authorization':'Token fa392aa886cad716b3e32e02256d4ef0e80b3080' }  
            'Authorization':'Token 48a21e6152daab6ed161c75ba1d236ec61307377'}
	    //{"token":"48a21e6152daab6ed161c75ba1d236ec61307377"}
    };
    fetch(url, dict)
        .then(response => { 
            if (response &&  response["text"]) {
                    response.text()
                        .then(function(data) { 
                            var json_data = JSON.parse(data);
                            callback(json_data);
                        })
                        .catch(function(x) { 
                            console.log("error in load_url " + url)
                            console.log("EXCEPTION:" + x)
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

