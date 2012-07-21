var ws;
var ws_addr;
var opening = false;
var last_try = (new Date).getTime();
var tries_count = 0;
var onmessage;

function openws() {
    if ("WebSocket" in window) {
        ws = new WebSocket(ws_addr);
    } else {
        ws = new MozWebSocket(ws_addr);
    }

    ws.onopen = function() {
        tries_count = 0;
    }
    ws.onclose = reopenws;
    /*ws.onerror = function() {
        if (ws.readyState == ws.OPEN) {
            ws.close()
        }
        reopenws();
    }*/
    ws.onmessage = onmessage;

    return ws;
}

function reopenws() {
    if (!opening) {
        opening = true;
        _reopenws();
    }
}

function _reopenws() {
    var tnow = (new Date).getTime()
    // 3 times for 5 seconds
    if (tries_count < 3) {
        if (tnow - last_try >= 5000) {
            tries_count++;
            opening = false;
            openws();
        } else {
            setTimeout(_reopenws, 5000);
        }
    // 30 times for 1 minute
    } else if (tries_count < 30) {
        if (tnow - last_try >= 60000) {
            tries_count++;
            opening = false;
            openws();
        } else {
            setTimeout(_reopenws, 60000);
        }
    } // In other cases seems like server in deep down, give up.
    last_try = tnow;
}


var secure_connection = window.location.protocol == "https:";

switch (page_type) {
    case "main":
        ws_addr = ((secure_connection ? "wss" : "ws" ) + "://" +
                   websocket_base + "/ws?v=2");
        onmessage = main_page_handler;
        openws();
        break;
    case "message":
        ws_addr = ((secure_connection ? "wss" : "ws" ) + "://" +
                   websocket_base + window.location.pathname + "/ws?v=2");
        onmessage = message_page_handler;
        openws();
        break;
}
