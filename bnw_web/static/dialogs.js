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
    inner2.find("#dlg_ok").click(function() {
        inner.hide();
    });
    inner.css("left", ($(window).width() - inner.width()) / 2);
    inner.css("top", ($(window).height() - inner.height()) / 2 +
              $(window).scrollTop());
    inner.show();
}
