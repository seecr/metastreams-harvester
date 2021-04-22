/* begin license *
 *
 * "Seecr Metastreams" is a fork of Meresco Harvester that demonstrates
 * the translation of traditional metadata into modern events streams.
 *
 * Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
 *
 * This file is part of "Seecr Metastreams"
 *
 * "Seecr Metastreams" is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * "Seecr Metastreams" is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with "Seecr Metastreams"; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * end license */

/* ---------- Users */
function reload_userscard(groupId) {
    $.get("/group/card/users", "groupId="+groupId)
        .done(function(data) {
            var _card = $("#placeholder_userscard");
            _card
                .empty()
                .append(data);
            init_userscard(_card);
        })
}

function init_userscard(placeholder) {
    placeholder.find("#BtnAddUserToGroup")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _form = $("#FrmAddUserToGroup");
            $.post("/groups.action/addUsername", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_userscard(_groupId);
                    }
                })
        });

    placeholder.find("#TblGroupUsers").find(".deletable")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _button = $(this);
            var _form = _button.closest("form");
            $.post("/groups.action/removeUsername", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_userscard(_groupId);
                    }
                });
        });
}

/* ---------- Domains */
function reload_domainscard(groupId) {
    $.get("/group/card/domains", "groupId="+groupId)
        .done(function(data) {
            var _card = $("#placeholder_domainscard");
            _card
                .empty()
                .append(data);
            init_domainscard(_card);
        })
}

function init_domainscard(placeholder) {
    placeholder.find("#BtnAddDomainIdToGroup")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _form = $("#FrmAddDomainIdToGroup");
            $.post("/groups.action/addDomain", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_domainscard(_groupId);
                    }
                })
        });

    placeholder.find("#TblGroupDomains").find(".deletable")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _button = $(this);
            var _form = _button.closest("form");
            $.post("/groups.action/removeDomain", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_domainscard(_groupId);
                    }
                });
        });
}

$(document).ready(function() {
    init_domainscard($("#placeholder_domainscard"));
    init_userscard($("#placeholder_userscard"));
})
