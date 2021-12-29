/* begin license *
 *
 * "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
 * the translation of traditional metadata into modern events streams.
 *
 * Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
 *
 * This file is part of "Metastreams Harvester"
 *
 * "Metastreams Harvester" is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * "Metastreams Harvester" is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with "Metastreams Harvester"; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * end license */

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
