var favicon_notify;
$(function(){
    var favicon_changed = false;
    $(window).focus(function () {
        if (favicon_changed) {
            favicon.change("/favicon.ico");
            favicon_changed = false;
        }
    });
    favicon_notify = function () {
        if (!favicon_changed) {
            favicon.change("/static/favicon-event.ico");
            favicon_changed = true;
        }
    };
});

