var ws_addr;
var opening = false;
var last_try = (new Date).getTime();
var tries_count = 0;
var onmessage;

function openws() {
    var ws;

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


var favicon_changed = false;
var timeout_id;

$(window).focus(function () {
    if (favicon_changed) {
        favicon.change("/favicon.ico");
        favicon_changed = false;
    }
});

function change_favicon() {
    if (timeout_id != undefined) {
        clearTimeout(timeout_id);
        timeout_id = undefined;
    }
    if (!favicon_changed) {
        favicon.change("/static/favicon-event.ico");
        favicon_changed = true;
    }
    if (document.hasFocus()) {
        timeout_id = setTimeout(function() {
            favicon.change("/favicon.ico");
            favicon_changed = false;
            timeout_id = undefined;
        }, 2000);
    }
}


function add_node(html, to, at_top) {
    var node = $(html).hide();
    node.addClass("outerborder_added");
    node.find("img.avatar").removeClass("avatar_ps");
    node.find("img.imgpreview_ps").each(function() {
        $(this).removeClass("imgpreview_ps");
    });
    node.mouseover(function() {
        $(this).removeClass("outerborder_added");
        $(this).unbind("mouseover");
    });
    if (at_top) {
        node.prependTo(to);
    } else {
        node.appendTo(to);
    }
    node.show("slow");
    change_favicon();
}

function main_page_handler(e) {
    var d = JSON.parse(e.data);
    if (d.type == "new_message" &&
        window.location.search.indexOf("page") == -1) {
            // Add new messages only to first page.
            add_node(d.html, "div.messages", true);
    } else if (d.type == "del_message") {
        $("div#"+d.id).removeClass("outerborder_added"
        ).addClass("outerborder_deleted");
        change_favicon();
    } else if (d.type == "upd_comments_count") {
        var msg = $("div#"+d.id);
        if (msg.length) {
            var t = msg.find("div.sign").contents()[2];
            t.nodeValue = t.nodeValue.replace(/\([0-9]+(\+)?/, "("+d.num+"$1")
        }
    } else if (d.type == "upd_recommendations_count") {
        var msg = $("div#"+d.id);
        if (msg.length) {
            var t = msg.find("div.sign").contents()[2];
            var val = t.nodeValue;
            var re = /\+[0-9]+\)/;
            var new_val = d.num ? "+"+d.num+")" : ")";
            if (val.match(re)) {
                t.nodeValue = val.replace(re, new_val);
            } else {
                t.nodeValue = val.replace(/\)/, new_val);
            }
        }
    }
}

function message_page_handler(e) {
    var d = JSON.parse(e.data);
    if (d.type == "new_comment") {
        add_node(d.html, "div.comments", false);
    } else if (d.type == "del_comment") {
        $("div#"+d.id).removeClass("outerborder_added"
        ).addClass("outerborder_deleted");
        change_favicon();
    }
}


function api_call_alert(func, args, verbose) {
    args["login"] = $.cookie("bnw_loginkey");
    $.ajax({
        url: "/api/"+func,
        data: args,
        dataType: "json",
        success: function (d) {
            if (verbose) {
                if (d.ok)
                    alert("OK. "+d.desc);
                else
                    alert("ERROR. "+d.desc);
            }
        },
        error: function(d, status) {
            alert("API request failed.");
            return false;
        }
    });
}

function confirm_action(desc, f, e) {
    var inner = $("#dlg_inner");
    var inner2 = $("#dlg_inner2");
    inner2.html(
        '<form id="dlg_centered">'+
        '<span>Вы уверены, что хотите '+desc+'?</span><br /><br />'+
        '<input type="button" id="dlg_yes" class="styledbutton" value="[&lt; Да &gt;]">'+
        '<input type="button" id="dlg_no" class="styledbutton" value="[&lt; Нет &gt;]">'+
        '</form>');
    inner2.find("#dlg_yes").click(function() {
        inner.hide();
        $("body").unbind("click");
        f();
    });
    inner2.find("#dlg_no").click(function() {
        inner.hide();
        $("body").unbind("click");
    });
    inner.css("left", e.pageX+15);
    inner.css("top", e.pageY+15);
    inner.show();
}

function add_message_page_actions() {
    function recommendation() {
        var r = $("<a/>").text("r").click(function(e) {
            confirm_action("рекомендовать сообщение #"+message_id,
            function() {
                api_call_alert("recommend", {message: message_id});
            }, e);
        });
        r.css("cursor", "pointer");
        $("#"+message_id).find(".msgb").append(" ").append(r);
    }
    function textarea() {
        $("#commenttextarea").keypress(function(event) {
            if (event.ctrlKey && (event.keyCode==13 || event.keyCode==10)) {
                $("#commentform").submit();
            }
        });
    }
    function comment_reply() {
        var form = $("#commentdiv");
        $("div.comments").children().each(function() {
            var comment = $(this);
            var short_id = comment.attr("id");
            var id = message_id + "/" + short_id;
            comment.find(".msgid").first().click(function() {
                var depth = comment_info[id].depth + 1;
                form.css("margin-left", depth+"em");
                form.find("[name=comment]").val(short_id);
                comment.after(form);
                form.find("textarea").focus();
                return false;
            });
        });
        var hr = $("hr").last();
        function clear_replyto() {
            form.css("margin-left", "");
            form.find("[name=comment]").val("");
            hr.after(form);
            $("html,body").scrollTop($(document).height());
            form.find("textarea").focus();
            return false;
        }
        $("#"+message_id).find(".msgid").click(clear_replyto);
        $("#clear_replyto").click(clear_replyto);
    }
    function comment_delete() {
        function D_button(id) {
            var D = $("<a/>").text("D").click(function(e) {
                confirm_action("удалить сообщение #"+id,
                function() {
                    api_call_alert("delete", {message: id});
                }, e);
            });
            D.css("cursor", "pointer");
            return D;
        }

        for (var id in comment_info) {
            var comment = comment_info[id];
            var short_id = id.split('/')[1];
            if (comment["user"] == auth_user || message_user == auth_user) {
                $("#"+short_id).find(".cmtb").append(" ").append(D_button(id));
            }
        }
        if (message_user == auth_user) {
            $("#"+message_id).find(".msgb").append(" "
            ).append(D_button(message_id));
        }
    }

    recommendation();
    textarea();
    comment_reply();
    comment_delete();
}


var secure_connection = window.location.protocol == "https:";
var is_auth_user = $.cookie("bnw_loginkey") != null;

$(function() {
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
        if (is_auth_user) {
            add_message_page_actions();
        }
        break;
    }
});
