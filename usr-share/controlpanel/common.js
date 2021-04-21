function errorMessage(txt) {
    var _box = $("#message-box");
    if (_box != undefined) {
        console.log("_box", _box.find("svg"));
        _box.find("strong").html(txt);
        _box.show();
    }
}

$(document).ready(function () {
    $(document).ajaxStart(function () { $("html").addClass("wait"); });
    $(document).ajaxStop(function () { $("html").removeClass("wait"); });
});
