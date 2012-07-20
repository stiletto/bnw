function login_win() {
    $("#dlg_inner2").html('<form onsubmit="return login_login();"><p>Имя: <input id="login_name" class="blueinput"></p><p>Пароль: <input id="login_pass" type="password" class="blueinput"></p><input type="submit"  class="styledbutton" value="[&lt; Войти &gt;]"><span id="login_progress"></span><input type="button" onclick="return login_cancel();" class="styledbutton" value="[&lt; Отмена &gt;]"></form>');
    var inner = $("#dlg_inner");
    inner.css("left", ($(window).width() - inner.width()) / 2);
    inner.css("top", ($(window).height() - inner.height()) / 2);
    inner.show()
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
