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
    $("code",node).each(function(i, e) {hljs.highlightBlock(e)});
    node.mouseover(function() {
        $(this).removeClass("outerborder_added");
        $(this).unbind("mouseover");
    });
    if (at_top) {
        node.prependTo(to);
        // Remove last message.
        if ($(to+">:visible").length > 19) {
            $(to).children().slice(-1).remove();
        }
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
            add_node(d.html, "#messages", true);
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
            var t = msg.find("div.sign").contents()[3];
            t.nodeValue = t.nodeValue.replace(/\([0-9]+(\+)?/, "("+d.num+"$1")
        }
    } else if (d.type == "upd_recommendations_count") {
        var msg = $("#"+d.id);
        if (msg.length) {
            var t = msg.find("div.sign").contents()[3];
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
        add_node(d.html, "#comments", false);
        add_message_page_actions(d.id, d.user);
    } else if (d.type == "del_comment") {
        var short_id = d.id.split("/")[1];
        var comment = $("#"+short_id);
        if (comment.length) {
            comment.removeClass("outerborder_added"
            ).addClass("outerborder_deleted");
            setTimeout(function() {
                comment.fadeOut("slow");
            }, 3000);
        }
    }
}


///////////////////////////////////////////////////////////////////////////
// Dynamic actions.
///////////////////////////////////////////////////////////////////////////

function escapeHTML(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function api_call(func, args, verbose, onsuccess, onerror) {
    args["login"] = $.cookie("bnw_loginkey");
    $.ajax({
        url: "/api/"+func,
        type: "POST",
        data: args,
        dataType: "json",
        success: function(d) {
            if (d.ok) {
                if (onsuccess) onsuccess(d);
                if (verbose) info_dialog("OK. "+escapeHTML(d.desc));
            } else {
                if (onerror) onerror(d);
                info_dialog("ERROR. "+escapeHTML(d.desc));
            }
        },
        error: function() {
            if (onerror) onerror();
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
    subscribe: function(message_id, is_subscribed) {
        function s_button() {
            // TODO: Helper title.
            button = $("<a/>").text("S").click(function() {
                api_call("subscriptions/add", {message: message_id}, true,
                    function() {
                        button.replaceWith(u_button());
                    });
            });
            button.css("cursor", "pointer");
            return button;
        }
        function u_button() {
            button = $("<a/>").text("U").click(function() {
                api_call("subscriptions/del", {message: message_id}, true,
                    function() {
                        button.replaceWith(s_button());
                    });
            });
            button.css("cursor", "pointer");
            return button;
        }

        var button = is_subscribed ? u_button() : s_button();
        $("#"+message_id).find(".sign").prepend(" ").prepend(button);
    },
    message_delete: function(message_id, message_user) {
        if (auth_user == message_user) {
            $("#"+message_id).find(".msgb").append(" "
            ).append(actions.D_button(message_id));
        }
    },
    message_update: function(message_id, message_user) {
        if (auth_user != message_user) {
            return;
        }
        function show_edit_input() {
            var clubs_t = clubs.map(function(t){return "!"+t}).join(",");
            var tags_t = tags.map(function(t){return "*"+t}).join(",");
            if (clubs_t && tags_t) clubs_t += ",";
            var text = clubs_t + tags_t;
            input.val(text);
            input.attr("size", (text.length > 39) ? 60 : text.length + 20);
            tags_div.hide();
            form.show();
            var val = input.val();
            input.val("");
            input.focus();
            input.val(val);
        }
        function update_tags() {
            // Update tags.
            var _clubs = [];
            var _tags = [];
            if (input.val()) {
                var spl = input.val().split(",");
                for (var i = 0; i < spl.length; i++) {
                    if (spl[i].length > 1 && spl[i][0] == "!") {
                        var club = spl[i].slice(1);
                        _clubs.push(club);
                    } else if (spl[i].length > 1 && spl[i][0] == "*") {
                        var tag = spl[i].slice(1);
                        _tags.push(tag);
                    } else {
                        info_dialog("ERROR. Wrong format!");
                        return false;
                    }
                }
            }
            api_call("update",
                {message: message_id, clubs: _clubs.join(","),
                 tags: _tags.join(","), api: true}, false,
                // onsuccess
                function() {
                    clubs = _clubs;
                    tags = _tags;
                    tags_div.empty();
                    for (var i=0; i<clubs.length; i++) {
                        var a = $("<a/>");
                        a.addClass("club");
                        a.attr("href", "/c/"+clubs[i]);
                        a.text(clubs[i]);
                        tags_div.append(a).append(" ");
                    }
                    for (var i=0; i<tags.length; i++) {
                        var a = $("<a/>");
                        a.addClass("tag");
                        a.attr("href", "/t/"+tags[i]);
                        a.text(tags[i]);
                        tags_div.append(a).append(" ");
                    }
                    tags_div.append(editb);
                    // Rebind click because we have used empty on tags_div.
                    editb.click(show_edit_input);
                    form.hide();
                    tags_div.show();
                });
                return false;
        }

        var tags_div = $("#"+message_id).find(".tags");
        var form = $('<form><input class="blueinput" /></form>').append(" ");
        form.hide();
        tags_div.after(form);
        form.submit(update_tags);
        var input = form.find("input");
        input.attr("title", "!Клубы и *теги через запятую");
        var clubs = tags_div.find(".club").map(function(i,o){return o.text}).get();
        var tags = tags_div.find(".tag").map(function(i,o){return o.text}).get();
        var editb = $("<a/>");
        editb.attr("title", "Редактировать теги");
        editb.text("±");
        editb.addClass("ajax_link");
        editb.css("cursor", "pointer");
        editb.click(show_edit_input);
        var okb = $("<a/>");
        okb.attr("title", "Сохранить");
        okb.text("✔");
        okb.addClass("ok_button");
        okb.css("cursor", "pointer");
        okb.click(update_tags);
        var cancelb = $("<a/>");
        cancelb.attr("title", "Отменить");
        cancelb.text("✘");
        cancelb.addClass("cancel_button");
        cancelb.css("cursor", "pointer");
        cancelb.click(function() {
            form.hide();
            tags_div.show();
        });
        form.append(okb).append(" ").append(cancelb);

        tags_div.append(editb);
    }
}

function add_main_page_actions(message_id, message_user) {
    if (!auth_user) {
        return;
    }
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
    if (!auth_user) {
        return;
    }
    function textarea() {
        var sendb = $("#send_comment")[0];
        $("#comment_textarea").keypress(function(event) {
            if (event.ctrlKey && (event.keyCode==13 || event.keyCode==10) &&
                !sendb.disabled) {
                    $("#comment_form").submit();
            }
        });
    }
    function dynamic_submit() {
        var form = $("#comment_div");
        var form2 = $("#comment_form");
        var hr2 = $("hr").last();
        var comment_text = form2.find("[name=comment]");
        var textarea = $("#comment_textarea");
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
                return true;
            }
            var id = message_id;
            if (comment_text.val()) {
                id += "/" + comment_text.val();
            }
            before();
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
        var form = $("#comment_div");
        var comment_text = form.find("[name=comment]");
        var hr1 = $("hr").first();
        var hr2 = $("hr").last();
        $("#"+message_id).find(".msgid").click(function() {
            form.css("margin-left", "1em");
            comment_text.val("");
            hr1.before(form);
            $("#comment_textarea").focus();
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
        var form = $("#comment_div");
        var short_id = comment_id.split("/")[1];
        var comment = $("#"+short_id);
        comment.find(".msgid").first().click(function() {
            var d = depth;
            if (!d) {
                d = 1;
            } else {
                d += 1;
            }
            form.css("margin-left", d+"em");
            form.find("[name=comment]").val(short_id);
            comment.after(form);
            $("#comment_textarea").focus();
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
        actions.subscribe(message_id, is_subscribed);
        actions.message_delete(message_id, message_user);
        actions.message_update(message_id, message_user);
        actions.recommendation(message_id, message_user, is_recommended);
        for (var id in comment_info) {
            var info = comment_info[id];
            comment_reply(id, info.user, info.depth);
            comment_delete(id, info.user);
        }
    }
}

function new_post() {
    var newb = $("#new_post");
    if (page_type != "user") {
        newb.attr("href", "/u/"+auth_user+"#write");
        return;
    } else {
        newb.attr("href", "#");
    }

    // Add actions.
    function show_hide() {
        if (window.location.hash == "#write") {
            window.location.hash = "";
        }
        if (post_div.is(":visible")) {
            post_div.hide();
        } else {
            post_div.show();
            textarea.focus();
        }
        return false;
    }
    function before() {
        textarea.focus();
        hideb.attr("disabled", "disabled");
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
        hideb.removeAttr("disabled");
        sendb.removeAttr("disabled");
    }
    var post_div = $("#post_div");
    var post_form = $("#post_form");
    var tags_text = post_form.find("[name=tags]");
    var clubs_text = post_form.find("[name=clubs]");
    var textarea = $("#post_textarea");
    var sendb = $("#send_post");
    var hideb = $("#hide_post");
    var old_value, iid;
    newb.click(show_hide);
    hideb.click(show_hide);
    post_form.submit(function() {
        if (ws.readyState != ws.OPEN) {
            // Use non-ajax submit if websocket not opened.
            return true;
        }
        before();
        api_call(
            "post", {tags: tags_text.val(), clubs: clubs_text.val(),
                     text: textarea.val()}, false,
            // onsuccess
            function() {
                after();
                tags_text.val("");
                clubs_text.val("");
                textarea.val("");
                show_hide();
            },
            // onerror
            after);
        return false;
    });
    textarea.keypress(function(event) {
        if (event.ctrlKey && (event.keyCode==13 || event.keyCode==10) &&
            !sendb[0].disabled) {
                post_form.submit();
        }
    });

    // Finally, show form if user clicked on new post button
    // on another page.
    if (window.location.hash == "#write") {
        show_hide();
    }
}


// Add actions.
$(function() {
    if (auth_user) {
        new_post();
    } else {
        login_dialog();
    }

    switch (page_type) {
    case "main":
        add_main_page_actions();
        break;
    case "message":
        treeing_complete = function() {
            add_message_page_actions();
        }
        break;
    case "user":
        add_main_page_actions();
        break;
    }
});
