function errorMessage(txt) {
    var _box = $("#message-box");
    if (_box != undefined) {
        _box.find("svg")
            .html(txt)
            .show();
    }
}

$(document).ready(function () {
    $(document).ajaxStart(function () { $("html").addClass("wait"); });
    $(document).ajaxStop(function () { $("html").removeClass("wait"); });
});
