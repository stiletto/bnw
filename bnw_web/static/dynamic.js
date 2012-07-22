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


///////////////////////////////////////////////////////////////////////////
// Websocket handlers.
///////////////////////////////////////////////////////////////////////////

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
    node.fadeIn("slow");
    change_favicon();
}

function main_page_handler(e) {
    var d = JSON.parse(e.data);
    if (d.type == "new_message" &&
        window.location.search.indexOf("page") == -1) {
            // Add new messages only to first page.
            add_node(d.html, "div.messages", true);
            add_main_page_actions(d.id, d.user);
    } else if (d.type == "del_message") {
        var msg = $("#"+d.id);
        if (msg.length) {
            msg.removeClass("outerborder_added"
            ).addClass("outerborder_deleted");
            setTimeout(function() {
                msg.fadeOut("slow");
            }, 3000);
        }
    } else if (d.type == "upd_comments_count") {
        var msg = $("#"+d.id);
        if (msg.length) {
            var t = msg.find("div.sign").contents()[2];
            t.nodeValue = t.nodeValue.replace(/\([0-9]+(\+)?/, "("+d.num+"$1")
        }
    } else if (d.type == "upd_recommendations_count") {
        var msg = $("#"+d.id);
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
        add_message_page_actions(d.id, d.user);
    } else if (d.type == "del_comment") {
        var short_id = d.id.split("/")[1];
        var comment = $("#"+short_id);
        comment.removeClass("outerborder_added"
        ).addClass("outerborder_deleted");
        setTimeout(function() {
            comment.fadeOut("slow");
        }, 3000);
    }
}


///////////////////////////////////////////////////////////////////////////
// Dynamic actions.
///////////////////////////////////////////////////////////////////////////

function api_call(func, args, verbose, onsuccess, onerror) {
    args["login"] = $.cookie("bnw_loginkey");
    $.ajax({
        url: "/api/"+func,
        data: args,
        dataType: "json",
        success: function(d) {
            if (d.ok) {
                if (onsuccess) onsuccess();
                if (verbose) info_dialog("OK. "+d.desc);
            } else {
                if (onerror) onerror();
                info_dialog("ERROR. "+d.desc);
            }
        },
        error: function() {
            info_dialog("API request failed.");
        }
    });
}

// Common actions.
var actions = {
    D_button: function(id) {
        var D = $("<a/>").text("D").click(function(e) {
            confirm_dialog(
                "удалить сообщение #"+id,
                function() {
                    api_call("delete", {message: id});
                }, e);
        });
        D.css("cursor", "pointer");
        return D;
    },
    recommendation: function(message_id, message_user, is_recommended) {
        function r_button() {
            // TODO: Helper title.
            button = $("<a/>").text("!").click(function() {
                api_call("recommend",
                    {message: message_id}, true,
                    function() {
                        button.replaceWith(u_button());
                    });
            });
            button.css("cursor", "pointer");
            return button;
        }
        function u_button() {
            button = $("<a/>").text("!!").click(function() {
                api_call("recommend",
                    {message: message_id, unrecommend: true}, true,
                    function() {
                        button.replaceWith(r_button());
                    });
            });
            button.css("cursor", "pointer");
            return button;
        }

        if (auth_user == message_user) return;
        var button = is_recommended ? u_button() : r_button();
        $("#"+message_id).find(".msgb").append(" ").append(button);
    },
    message_delete: function(message_id, message_user) {
        if (auth_user == message_user) {
            $("#"+message_id).find(".msgb").append(" "
            ).append(actions.D_button(message_id));
        }
    },
}

function add_main_page_actions(message_id, message_user) {
    if (message_id) {
        // Add actions only to new message.
        actions.recommendation(message_id, message_user, false);
        actions.message_delete(message_id, message_user);
    } else {
        for (var id in message_info) {
            var info = message_info[id];
            actions.recommendation(id, info.user, info.is_recommended);
            actions.message_delete(id, info.user);
        }
    }
}

function add_message_page_actions(comment_id, comment_user) {
    function textarea() {
        $("#commenttextarea").keypress(function(event) {
            if (event.ctrlKey && (event.keyCode==13 || event.keyCode==10)) {
                $("#commentform").submit();
            }
        });
    }
    function dynamic_submit() {
        var form = $("#commentdiv");
        var form2 = $("#commentform");
        var hr2 = $("hr").last();
        var comment_text = form2.find("[name=comment]");
        var textarea = $("#commenttextarea");
        var clearb = $("#clear_replyto");
        var sendb = $("#send_comment");
        var old_value, iid;
        function before() {
            textarea.focus();
            clearb.attr("disabled", "disabled");
            sendb.attr("disabled", "disabled");
            old_value = sendb.val();
            sendb.val(".");
            iid = setInterval(function() {
                if (sendb.val().length > 4) {
                    sendb.val(".");
                } else {
                    sendb.val("."+sendb.val());
                }
            }, 300);
        }
        function after() {
            clearInterval(iid);
            sendb.val(old_value);
            clearb.removeAttr("disabled");
            sendb.removeAttr("disabled");
        }
        form2.submit(function() {
            if (ws.readyState != ws.OPEN) {
                // Use non-ajax submit if websocket not opened.
                form2.submit();
                return;
            }
            before();
            var id = message_id;
            if (comment_text.val()) {
                id += "/" + comment_text.val();
            }
            api_call(
                "comment", {message: id, text: textarea.val()}, false,
                // onsuccess
                function() {
                    after();
                    form.css("margin-left", "");
                    comment_text.val("");
                    textarea.val("");
                    hr2.after(form);
                    $("html, body").scrollTop($(document).height());
                },
                // onerror
                after);
            return false;
        });
    }
    function message_reply() {
        var form = $("#commentdiv");
        var comment_text = form.find("[name=comment]");
        var hr1 = $("hr").first();
        var hr2 = $("hr").last();
        $("#"+message_id).find(".msgid").click(function() {
            form.css("margin-left", "1em");
            comment_text.val("");
            hr1.before(form);
            $("#commenttextarea").focus();
            return false;
        });
        $("#clear_replyto").click(function() {
            form.css("margin-left", "");
            comment_text.val("");
            hr2.after(form);
            return false;
        });
    }
    function comment_reply(comment_id, comment_user, depth) {
        var form = $("#commentdiv");
        var short_id = comment_id.split("/")[1];
        var comment = $("#"+short_id);
        comment.find(".msgid").first().click(function() {
            if (!depth) {
                depth = 1;
            } else {
                depth += 1;
            }
            form.css("margin-left", depth+"em");
            form.find("[name=comment]").val(short_id);
            comment.after(form);
            $("#commenttextarea").focus();
            return false;
        });
    }
    function comment_delete(comment_id, comment_user) {
        if (comment_user == auth_user || message_user == auth_user) {
            var short_id = comment_id.split("/")[1];
            $("#"+short_id).find(".cmtb").append(" "
            ).append(actions.D_button(comment_id));
        }
    }

    if (comment_id) {
        // Add actions only to new comment.
        comment_reply(comment_id, comment_user);
        comment_delete(comment_id, comment_user);
    } else {
        textarea();
        dynamic_submit();
        message_reply();
        actions.message_delete(message_id, message_user);
        actions.recommendation(message_id, message_user, is_recommended);
        for (var id in comment_info) {
            var info = comment_info[id];
            // TODO: Pass comment node and short_id?
            comment_reply(id, info.user, info.depth);
            comment_delete(id, info.user);
        }
    }
}


// Add actions.
$(function() {
    $("#login_button").click(login_win);

    switch (page_type) {
    case "main":
        if (auth_user) {
            add_main_page_actions();
        }
        break;
    case "message":
        if (auth_user) {
            add_message_page_actions();
        }
        break;
    case "user":
        if (auth_user) {
            add_main_page_actions();
        }
        break;
    }
});
