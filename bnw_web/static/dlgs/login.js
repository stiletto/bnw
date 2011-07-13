function login_win() {
    $("#dlg_inner2").html('<form onsubmit="return login_login();"><p>Имя: <input id="login_name" class="blueinput"></p><p>Пароль: <input id="login_pass" type="password" class="blueinput"></p><input type="submit"  class="styledbutton" value="[&lt; Войти &gt;]"><span id="login_progress"></span><input type="button" onclick="return login_cancel();" class="styledbutton" value="[&lt; Отмена &gt;]"></form>');
    $("#dlg_outer").css("display","table");
}   

function login_cancel() {
    $("#dlg_outer").css("display","none");
    return false;
}

function login_login() {
    var l=$("#login_name").val();
    var p=$("#login_pass").val();
    $("#dlg_inner2 .styledbutton").css("display","none");
    $("#login_progress").text("Выполняется вход...");
    $.ajax({ url: "/api/passlogin",
        data:{user:l,password:p},
        dataType:'json',
        success: function (data) { 
            if (data.ok) {
                 $.cookie("bnw_loginkey",data.desc,{ expires: 30 });
                 $("#dlg_outer").css("display","none");
            } else {
                 $("#login_progress").text(data.desc+"\n");
                $("#dlg_inner2 .styledbutton").css("display","inline-block");
            }
        },
        error: function (data,status) {
                $("#login_progress").text("Fucked up"); 
                $("#login_progress").text(data.status);  }});
    return false;
}

        