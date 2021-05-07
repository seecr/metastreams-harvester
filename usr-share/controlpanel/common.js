function errorMessage(txt) {
    var _box = $("#message-box");
    if (_box != undefined) {
        _box.find("strong").html(txt);
        _box.show();
    }
}

function resetErrorMessage(txt) {
    var _box = $("#message-box");
    if (_box != undefined) {
        _box.hide();
    }
}

function form_setBordersAndDisabled(form, button) {
	form.find("input").keyup(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (button.prop('disabled') == true) {
            button.prop('disabled', false);
        }
	});
}

function form_resetBordersAndDisabled(form, button, reset) {
    button.prop('disabled', true);
    form.find('.border-warning').each(function() {
        $(this).removeClass('border-warning');
    });
    if (reset) {
        form.trigger('reset');
    }
}

$(document).ready(function () {
    $(document).ajaxStart(function () { $("html").addClass("wait"); });
    $(document).ajaxStop(function () { $("html").removeClass("wait"); });
});
