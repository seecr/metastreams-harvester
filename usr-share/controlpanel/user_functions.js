function init_UpdateUser(placeholder, callback) {
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
                        if (callback != undefined) {
                            callback();
                        }
                    }
                });
        });
    form_setBordersAndDisabled(_form, _updateButton);
}
function init_ChangePassword(placeholder) {
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

            $.post('/users.action/changePassword', _passwordForm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        msg_Success(placeholder=placeholder, id="MsgChangePassword", text="Wachtwoord aangepast.");
                    } else {
                        msg_Error(placeholder=placeholder, id="MsgChangePassword", text=data['message']);
                    }
                    form_resetBordersAndDisabled(_passwordForm, _changeButton, true);
                });
        });
    form_setBordersAndDisabled(_passwordForm, _changeButton);
}
