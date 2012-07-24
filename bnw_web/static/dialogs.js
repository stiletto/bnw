// Base dialog class.
function Dialog() {
    this.outer = $("<div/>").addClass("dlg_outer");
    this.inner = $("<div/>").addClass("dlg_inner");
    this.outer.append(this.inner);
    $("body").append(this.outer);

    this.html = function(text) {
        this.inner.html(text);
    }
    this.find = function(s) {
        return this.inner.find(s);
    }
    this.show = function() {
        this.outer.show();
    }
    this.show_centered = function(speed) {
        this.show(speed);
        this.outer.css("left", ($(window).width() - this.inner.width()) / 2);
        this.outer.css("top", ($(window).height() - this.inner.height()) / 2 +
                              $(window).scrollTop());
    }
    this.show_near_mouse = function(e, speed) {
        this.outer.css("left", e.pageX+15);
        this.outer.css("top", e.pageY+15);
        this.show(speed);
    }
    this.destroy = function() {
        this.outer.remove();
    }
}

function login_dialog() {
    $("#login_button").click(login_win);
}

function login_win() {
    var dialog = new Dialog;
    dialog.html(
        '<form><table>'+
        '<tr><td>Имя:</td><td>'+
        '<input class="login_name blueinput"></td></tr>'+
        '<tr><td>Пароль:</td><td>'+
        '<input type="password" class="login_pass blueinput">'+
        '</td></tr><tr><td colspan="2" class="dlg_ok_cancel">'+
        '<input type="submit" class="styledbutton" value="[&lt; Войти &gt;]">'+
        '<input type="button" class="dlg_cancel styledbutton" '+
        'value="[&lt; Отмена &gt;]">'+
        '</td></tr></table></form>');
    dialog.find("form").submit(function() {
        var l = dialog.find(".login_name").val();
        var p = dialog.find(".login_pass").val();
        // TODO: That's duplicate api_call dynamic.js function.
        $.ajax({
            url: "/api/passlogin",
            type: "POST",
            data: {user: l, password: p},
            dataType: "json",
            success: function (d) {
                if (d.ok) {
                    window.location = "/login?key="+d.desc;
                } else {
                    info_dialog(d.desc);
                }
            },
            error: function () {
                info_dialog("API request failed.");
            }
        });
        return false;
    });
    dialog.find(".dlg_cancel").click(function() {
        dialog.destroy();
    });
    dialog.show_centered();
    return false;
}

function confirm_dialog(desc, f, e) {
    var dialog = new Dialog;
    dialog.html(
        '<form class="dlg_centered">'+
        '<span>Вы уверены, что хотите '+desc+'?</span><br /><br />'+
        '<input type="button" class="dlg_yes styledbutton" value="[&lt; Да &gt;]">'+
        '<input type="button" class="dlg_no styledbutton" value="[&lt; Нет &gt;]">'+
        '</form>');
    dialog.find(".dlg_yes").click(function() {
        dialog.destroy();
        f();
    });
    dialog.find(".dlg_no").click(function() {
        dialog.destroy();
    });
    dialog.show_near_mouse(e);
}

function info_dialog(desc) {
    var dialog = new Dialog;
    dialog.html(
        '<form class="dlg_centered">'+
        '<span>'+desc+'</span><br /><br />'+
        '<input type="button" class="dlg_ok styledbutton" value="[&lt; OK &gt;]">'+
        '</form>');
    var ok_b = dialog.find(".dlg_ok");
    ok_b.click(function() {
        dialog.destroy();
        focused.focus();
    });
    var focused = $("*:focus");
    dialog.show_centered();
    ok_b.focus();
}

function new_post() {
    var newb = $("#new_post");
    if (page_type != "user") {
        newb.attr("href", "/u/"+auth_user+"#write");
        return;
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
            post_form.submit();
            return;
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
});
