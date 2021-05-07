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

function init_login_button() {
    var _btn = $("#BtnLogin");
    if (_btn != undefined) {
        _btn
            .unbind("click")
            .click(function(e) {
                $.get("/login")
                    .done(function(data) {
                        var _modal = $("#modal");
                        _modal.find("#placeholder_modal-title").html("Inloggen");
                        var _body_placeholder = _modal.find("#placeholder_modal-body");
                        _body_placeholder
                            .empty()
                            .append(data);
                        var _form = _body_placeholder.find("#FrmLogin");
                        _body_placeholder.find("#BtnDoLogin")
                            .unbind("click")
                            .click(function(e) {
                                e.preventDefault();
                                $.ajax({
                                    type: "POST",
                                    url: "/login.action",
                                    data: JSON.stringify(_form.serializeArray()),
                                    dataType: "json",
                                    success: function(loginResponse) {
                                        console.log(loginResponse);
                                        if (loginResponse['success'] == true) {
                                            window.location = "/"
                                        } else {
                                            var _box = _body_placeholder.find("#login-message-box");
                                            _box.find("strong").html(loginResponse.message);
                                            _box.show();
                                        }
                                    }
                                });
                            });
                        _modal.modal('show');
                   })
            })
    }
}

$(document).ready(function () {
    init_login_button();

    $(document).ajaxStart(function () {
        $("html").addClass("wait");
    });
    $(document).ajaxStop(function () {
        $("html").removeClass("wait");
    });
});
