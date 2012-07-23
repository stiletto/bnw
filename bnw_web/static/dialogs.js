function login_win() {
    $("#dlg_inner2").html('<form onsubmit="return login_login();"><p>Имя: <input id="login_name" class="blueinput"></p><p>Пароль: <input id="login_pass" type="password" class="blueinput"></p><input type="submit"  class="styledbutton" value="[&lt; Войти &gt;]"><span id="login_progress"></span><input type="button" onclick="return login_cancel();" class="styledbutton" value="[&lt; Отмена &gt;]"></form>');
    var inner = $("#dlg_inner");
    inner.css("left", ($(window).width() - inner.width()) / 2);
    inner.css("top", ($(window).height() - inner.height()) / 2);
    inner.show()
    return false;
}

function login_cancel() {
    $("#dlg_inner").hide()
    return false;
}

function login_login() {
    var l=$("#login_name").val();
    var p=$("#login_pass").val();
    $("#dlg_inner2.styledbutton").hide();
    $("#login_progress").text("Выполняется вход...");
    $.ajax({ url: "/api/passlogin",
        data:{user:l,password:p},
        dataType:'json',
        success: function (data) {
            if (data.ok) {
                 window.location = '/login?key='+data.desc;
                 $("#dlg_inner").hide()
            } else {
                 $("#login_progress").text(data.desc+"\n");
                 $("#dlg_inner2.styledbutton").css("display","inline-block");
            }
        },
        error: function (data,status) {
                $("#login_progress").text("Fucked up");
                $("#login_progress").text(data.status);  }});
    return false;
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
    var ok_b = $("#dlg_ok");
    ok_b.click(function() {
        inner.hide();
        focused.focus();
    });
    inner.css("left", ($(window).width() - inner.width()) / 2);
    inner.css("top", ($(window).height() - inner.height()) / 2 +
              $(window).scrollTop());
    inner.show();
    var focused = $("*:focus");
    ok_b.focus();
}

function new_post_dialog() {
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


$(function() {
    if (auth_user) {
        new_post_dialog();
    }
});
