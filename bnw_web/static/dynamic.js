var ws;
var ws_double_fail = false;
var ws_addr;
var onmessage;

function openws() {
    if ("WebSocket" in window) {
        ws = new WebSocket(ws_addr);
    } else {
        ws = new MozWebSocket(ws_addr);
    }

    ws.onopen = function () {
        if (ws_double_fail)
            $("#ws_status").text("WS Active (again)");
        else
            $("#ws_status").text("WS Active");
        ws_double_fail = false;
    }
    ws.onclose = function () {
        $("#ws_status").text("WS Closed");
        reopenws();
    }
    ws.onerror = function () {
        $("#ws_status").text("WS Error");
        reopenws();
    }
    ws.onmessage = onmessage;

    return ws;
}

function reopenws() {
    if (!ws_double_fail) {
        ws_double_fail = true;
        openws();
    }
}

var favicon_changed = false;
var timeout_id;

$(window).focus(function () {
    if (favicon_changed) {
        favicon.change("/favicon.ico");
        favicon_changed = false;
    }
});

function change_favicon() {
    if (!favicon_changed) {
        favicon.change("/static/favicon-event.ico");
        favicon_changed = true;
        if (timeout_id != undefined) {
            clearTimeout(timeout_id);
            timeout_id = undefined;
        }
        if (document.hasFocus()) {
            timeout_id = setTimeout(function() {
                favicon.change("/favicon.ico");
                favicon_changed = false;
                timeout_id = undefined;
            }, 2000);
        }
    }
}

function main_page_handler(e) {
    var d = JSON.parse(e.data);
    if (d.type == "new_message") {
        var msg = $(d.html);
        msg.addClass("outerborder_dynamic");
        msg.find("img.avatar").removeClass("avatar_ps");
        msg.find("img.imgpreview_ps").each(function() {
            $(this).removeClass("imgpreview_ps");
        });
        msg.hide().prependTo($("div.messages")).show("slow");
        change_favicon();
    }
}

function message_page_handler(e) {
    var d = JSON.parse(e.data);
    if (d.type == "new_comment") {
        var comment = $(d.html);
        comment.addClass("outerborder_dynamic");
        comment.find("img.avatar").removeClass("avatar_ps");
        comment.find("img.imgpreview_ps").each(function() {
            $(this).removeClass("imgpreview_ps");
        });
        comment.hide().appendTo($("div.comments")).show("slow");
        change_favicon();
    }
}

var secure_connection = window.location.protocol == "https:";
switch (page_type) {
    case "main":
        ws_addr = ((secure_connection ? "wss" : "ws" ) + "://" +
                   websocket_base + "/ws");
        onmessage = main_page_handler;
        openws();
        break;
    case "message":
        ws_addr = ((secure_connection ? "wss" : "ws" ) + "://" +
                   websocket_base + window.location.pathname + "/ws");
        onmessage = message_page_handler;
        openws();
        break;
}
