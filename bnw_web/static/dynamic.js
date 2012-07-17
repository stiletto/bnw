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

function main_onmessage(e) {
    var d = JSON.parse(e.data);
    var outerbox = $("<div class='outerborder hentry ajax' id='"+d.id+"'>");
    var msg = $("<div class='msg'>");
    msg.append("<img class='avatar' alt='avatar' "+
                   "src='/u/"+d.user+"/avatar/thumb' />");
    msg.append(d.wtags);
    if (d.thumbs.length) {
        var previews = $("<div class='imgpreviews'>");
        d.thumbs.forEach(function(thumb) {
            previews.append("<a class='imglink' href='"+thumb[0]+"'>"+
                            "<img class='imgpreview ajax' src='"+thumb[1]+
                            "' /></a>")
        })
        msg.append(previews);
    }
    var pre = $("<pre class='pw entry-title entry-content'>");
    if (d.thumbs.length) {
        pre.addClass("hasthumbs");
    }
    pre.append(d.linkified);
    var sign = $("<div class='sign'>");
    sign.append("<a class='msgid' rel='bookmark' href='/p/"+d.id+
                "'>#"+d.id+"</a>");
    sign.append("<span id='msgb-"+d.id+"' class='msgb'></span> ");
    sign.append("("+d.replycount);
    var reccount = d.recommendations.length;
    if (reccount) { sign.append("+"+reccount); }
    sign.append(") / <a class='usrid' href='/u/"+d.user+"'>@"+d.user+"</a>");
    msg.append(pre);
    msg.append(sign);
    outerbox.append(msg);
    outerbox.prependTo($("div.messages")).show("slow");
    change_favicon();
}

function message_onmessage(e) {
    var d = JSON.parse(e.data);
    var comment_id = d.id.split('/')[1];
    var outerbox = $("<div class='outerborder hentry ajax' id='"+comment_id+"'>");
    var comment = $("<div class='comment'>");
    comment.append("<img class='avatar' alt='avatar' "+
                   "src='/u/"+d.user+"/avatar/thumb' />");
    if (d.thumbs.length) {
        var previews = $("<div class='imgpreviews'>");
        d.thumbs.forEach(function(thumb) {
            previews.append("<a class='imglink' href='"+thumb[0]+"'>"+
                            "<img class='imgpreview ajax' src='"+thumb[1]+
                            "' /></a>")
        })
        comment.append(previews);
    }
    var pre = $("<pre class='comment_body pw entry-title entry-content'>");
    if (d.thumbs.length) {
        pre.addClass("hasthumbs");
    }
    pre.append(d.linkified);
    var sign = $("<div class='sign'>");
    sign.append("<a class='msgid' rel='bookmark' href='/p/"+d.id+
                "'>#"+d.id+"</a>");
    sign.append("<span id='cmtb-"+d.id+"' class='cmtb'></span> / ");
    sign.append("<a class='usrid' href='/u/"+d.user+"'>@"+d.user+"</a>");
    if (d.replyto) {
        sign.append(" --&gt; <a class='usrid' "+
                    "href='/p/"+d.replyto.replace('/', '#')+"'>#"+
                    d.replyto+"</a>");
    }
    comment.append(pre);
    comment.append(sign);
    outerbox.append(comment);
    outerbox.appendTo($("div.comments")).show("slow");
    change_favicon();
}

var secure_connection = window.location.protocol=="https:";
switch (page_type) {
    case "main":
        ws_addr = (secure_connection ? "wss" : "ws" ) + "://" + websocket_base + "/ws";
        onmessage = main_onmessage;
        break;
    case "message":
        ws_addr = (secure_connection ? "wss" : "ws" ) + "://" + websocket_base + window.location.pathname + "/ws";
        onmessage = message_onmessage;
        break;
}

openws();
