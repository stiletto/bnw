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
        '<input class="login_name blueinput" /></td></tr>'+
        '<tr><td>Пароль:</td><td>'+
        '<input type="password" class="login_pass blueinput" />'+
        '</td></tr><tr><td colspan="2" class="dlg_ok_cancel">'+
        '<input type="submit" class="styledbutton" '+
        'value="[&lt; Войти &gt;]" />'+
        '<input type="button" class="dlg_cancel styledbutton" '+
        'value="[&lt; Отмена &gt;]" />'+
        '</td></tr></table></form>');
    dialog.find("form").submit(function() {
        var l = dialog.find(".login_name").val();
        var p = dialog.find(".login_pass").val();
        api_call(
            "passlogin", {user: l, password: p}, false,
            // onsuccess
            function() {
                window.location = "/login?key="+d.desc;
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
        '<input type="button" class="dlg_yes styledbutton" '+
        'value="[&lt; Да &gt;]" />'+
        '<input type="button" class="dlg_no styledbutton" '+
        'value="[&lt; Нет &gt;]" />'+
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
        '<input type="button" class="dlg_ok styledbutton" '+
        'value="[&lt; OK &gt;]" />'+
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
