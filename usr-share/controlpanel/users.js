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
    init_UpdateUser(placeholder, load_table_users); // From user_functions.js
    init_ChangePassword(placeholder);               // From user_functions.js
}

function load_table_users() {
    $.get("/users/table/users")
        .done(function(data) {
            var _placeholder = $("#placeholder_users");
            _placeholder
                .empty()
                .append(data);
            init_table_users(_placeholder);
        });
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
                        resetErrorMessage();
                        _form.trigger("reset");
                        _createButton.prop('disabled', true);
                        _form.find('.border-warning').each(function() {
                            $(this).removeClass('border-warning');
                        });
                        load_table_users();
                    } else {
                        errorMessage(data['message']);
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
