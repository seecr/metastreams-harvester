function init_table_users(placeholder) {
    placeholder.find(".clickable-row").click(function(e) {
        e.preventDefault();

        var _row = $(this);
        var _username = _row.data("id");
        $.get("/users/modal/user", "username=" + _username)
            .done(function(data) {
                var _modal = $("#modal");
                _modal.find("#placeholder_modal-title").html("Bewerken gebruiker '" + _username + "'");
                var _body_placeholder = _modal.find("#placeholder_modal-body");
                _body_placeholder
                    .empty()
                    .append(data);
                init_modal_user(_body_placeholder);
                _modal.modal('show');
            })
    });
}

function init_modal_user(placeholder) {
    /*
     * General properties
     */
    var _form = placeholder.find("#FrmUpdateUser");
    var _updateButton = placeholder.find("#BtnUpdateUser");
    _updateButton
        .prop('disabled', 'true')
        .unbind('click')
        .click(function(e) {
            e.preventDefault();

            $.post("/users.action/updateUser", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_form, _updateButton, false);
                    }
                });
        });
    form_setBordersAndDisabled(_form, _updateButton);

    /*
     * Change Password
     */
    var _passwordForm = placeholder.find("#FrmChangePassword");
    var _changeButton = placeholder.find("#BtnChangePassword");
    _changeButton
        .prop('disabled', 'true')
        .unbind('click')
        .click(function(e) {
            e.preventDefault();

            $.post('/users.action/changePasswordFor', _passwordForm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_passwordForm, _changeButton, true);
                    } else {
                        alert(data['message']);
                        form_resetBordersAndDisabled(_passwordForm, _changeButton, true);
                    }
                });
        });
    form_setBordersAndDisabled(_passwordForm, _changeButton);
}


$(document).ready(function() {
    var _form = $("#FrmCreateUser");
    var _createButton = $("#BtnCreateUser");

    _createButton
        .prop('disabled', true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            $.post("/users.action/createUser", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        $.get("/users/table/users")
                            .done(function(data) {
                                var _placeholder = $("#placeholder_users");
                                _placeholder
                                    .empty()
                                    .append(data);
                                _form.trigger("reset");
                                _createButton.prop('disabled', true);
                                _form.find('.border-warning').each(function() {
                                    $(this).removeClass('border-warning');
                                })
                                init_table_users(_placeholder);
                            })
                    }
                })
        })

    init_table_users($("#placeholder_users"));

	_form.find("input").keyup(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (_createButton.prop('disabled') == true) {
            _createButton.prop('disabled', false);
        }
	});
})
