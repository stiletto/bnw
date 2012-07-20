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
        var msg = $("div#"+d.id);
        msg.removeClass("outerborder_added"
        ).addClass("outerborder_deleted");
        setTimeout(function() {
            msg.hide("slow");
        }, 3000);
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
        // TODO: Send already shorted id or create helper function.
        var short_id = d.id.split('/')[1];
        add_message_page_actions($("#"+short_id));
    } else if (d.type == "del_comment") {
        var comment = $("#"+d.id);
        comment.removeClass("outerborder_added"
        ).addClass("outerborder_deleted");
        setTimeout(function() {
            comment.hide("slow");
        }, 3000);
        change_favicon();
    }
}

function api_call(func, args, verbose) {
    args["login"] = $.cookie("bnw_loginkey");
    $.ajax({
        url: "/api/"+func,
        data: args,
        dataType: "json",
        success: function(d) {
            if (d.ok) {
                if (verbose) {
                    info_dialog("OK. "+d.desc);
                }
            } else {
                info_dialog("ERROR. "+d.desc);
            }
        },
        error: function(d, status) {
            alert("API request failed.");
            return false;
        }
    });
}

function confirm_dialog(desc, f, e) {
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
        f();
    });
    inner2.find("#dlg_no").click(function() {
        inner.hide();
    });
    inner.css("left", e.pageX+15);
    inner.css("top", e.pageY+15);
    inner.show();
}

function info_dialog(desc) {
    var inner = $("#dlg_inner");
    var inner2 = $("#dlg_inner2");
    inner2.html(
        '<form id="dlg_centered">'+
        '<span>'+desc+'</span><br /><br />'+
        '<input type="button" id="dlg_ok" class="styledbutton" value="[&lt; OK &gt;]">'+
        '</form>');
    inner2.find("#dlg_ok").click(function() {
        inner.hide();
    });
    inner.css("left", ($(window).width() - inner.width()) / 2);
    inner.css("top", ($(window).height() - inner.height()) / 2 +
              $(window).scrollTop());
    inner.show();
}

function add_message_page_actions(comment) {
    function recommendation() {
        var r = $("<a/>").text("r").click(function(e) {
            confirm_dialog("рекомендовать сообщение #"+message_id,
            function() {
                api_call("recommend", {message: message_id});
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
    function dynamic_submit() {
        var form = $("#commentdiv");
        var form2 = $("#commentform");
        var comment_text = form2.find("[name=comment]");
        var textarea = $("#commenttextarea");
        var hr2 = $("hr").last();
        form2.submit(function() {
            if (ws.readyState != ws.OPEN) {
                form2.submit();
                return;
            }

            var id = message_id;
            var short_id = comment_text.val();
            if (short_id) {
                id += "/" + short_id;
            }
            api_call("comment", {message: id, text: textarea.val()});
            form.css("margin-left", "");
            comment_text.val("");
            textarea.val("");
            hr2.after(form);
            $("html, body").scrollTop($(document).height());
            return false;
        });
    }
    function comment_reply(comment) {
        var form = $("#commentdiv");
        function set_reply_link(i, e, depth) {
            var comment = $(e);
            var short_id = comment.attr("id");
            var id = message_id + "/" + short_id;
            comment.find(".msgid").first().click(function() {
                if (depth == undefined) {
                    depth = comment_info[id].depth + 1;
                }
                form.css("margin-left", depth+"em");
                form.find("[name=comment]").val(short_id);
                comment.after(form);
                form.find("textarea").focus();
                return false;
            });
        }

        if (comment) {
            // Add link only to new comment.
            set_reply_link(0, comment, 1);
            return;
        }
        $("div.comments").children().each(set_reply_link);
        var hr1 = $("hr").first();
        var hr2 = $("hr").last();
        $("#"+message_id).find(".msgid").click(function() {
            form.css("margin-left", "1em");
            form.find("[name=comment]").val("");
            hr1.before(form);
            form.find("textarea").focus();
            return false;
        });
        $("#clear_replyto").click(function() {
            form.css("margin-left", "");
            form.find("[name=comment]").val("");
            hr2.after(form);
            return false;
        });
    }
    function comment_delete(comment) {
        function D_button(id) {
            var D = $("<a/>").text("D").click(function(e) {
                confirm_dialog("удалить сообщение #"+id,
                function() {
                    api_call("delete", {message: id});
                }, e);
            });
            D.css("cursor", "pointer");
            return D;
        }

        if (comment) {
            // Add D button only to new comment.
            var comment_user = comment.find(".usrid").text().slice(1);
            // TODO: div's ids should be in full form.
            var id = message_id + "/" + comment.attr("id");
            if (comment_user == auth_user || message_user == auth_user) {
                comment.find(".cmtb").append(" ").append(D_button(id));
            }
            return;
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

    if (comment) {
        // Add actions only to new comment.
        comment_reply(comment);
        comment_delete(comment);
    } else {
        recommendation();
        textarea();
        dynamic_submit();
        comment_reply();
        comment_delete();
    }
}


var is_auth_user = $.cookie("bnw_loginkey") != null;

$(function() {
    switch (page_type) {
    case "main":
        break;
    case "message":
        if (is_auth_user) {
            add_message_page_actions();
        }
        break;
    }
});
