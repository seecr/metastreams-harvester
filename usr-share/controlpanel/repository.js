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

function init_cardRepositoryAttributes() {
    var _frm = $("#FrmRepositoryAttributes");
    var _btn = $("#BtnRepositoryAttributes");
    _btn
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/action/updateRepositoryAttributes", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn);
                    } else {
                        msg_Error(placeholder=$("#placeholder_FrmRepositoryAttributes"), identifier=undefined, text=data['message']);
                    }
                })
        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardClosingHours() {
    var _frm = $("#FrmCreateClosingHours");
    var _btn = $("#BtnCreateClosingHours");

    function _load_table_closinghours(domainId, repositoryId) {
        var _placeholder = $("#placeholder_table_closinghours");
        $.get("/repository/table/closingHours", $.param({domainId: domainId, identifier: repositoryId}))
            .done(function(page) {
                _placeholder
                    .empty()
                    .append(page);
                init_table_closinghours();
            });
    }


    function init_table_closinghours() {
        var _placeholder = $("#placeholder_table_closinghours");
        _placeholder.find("button.deletable.seecr-btn")
            .unbind("click")
            .click(function(e) {
                var _btn = $(this);
                var _domainId = _btn.data('domainid');
                var _repositoryId = _btn.data('repositoryid'); 
                e.preventDefault();
                $.post("/action/deleteRepositoryClosingHours", $.param({
                        repositoryId: _repositoryId,
                        domainId: _domainId,
                        closingHour: _btn.data('closinghour')
                    }))
                    .done(function(data) {
                        if (data['success'] == true) {
                            _load_table_closinghours(_domainId, _repositoryId);
                        } else {
                            msg_Error(placeholder=$("#placeholder_FrmCreateClosingHours"), identifier=undefined, text=data['message']);
                        }
                    })

            })
    }
    init_table_closinghours();

    _btn
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/action/addRepositoryClosingHours", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn, true);
                        _load_table_closinghours(_frm.data("domainid"), _frm.data("repositoryid"));
                    } else {
                        msg_Error(placeholder=$("#placeholder_FrmCreateClosingHours"), identifier=undefined, text=data['message']);
                    }
                })
        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardRepositoryActions() {
    form_init(
        $("#FrmRepositoryActions"), "/action/updateRepositoryActionAttributes",
        $("#BtnRepositoryActions"), $("#placeholder_FrmRepositoryActions"));
}

function init_cardRepositoryFieldDefinitions() {
    form_init(
        $("#FrmFieldDefinition"), "/action/updateRepositoryFieldDefinitions",
        $("#BtnFieldDefinition"), $("#placeholder_FrmFieldDefinition"));
}

function init_cardHeaders() {
    let _frm = $("#FrmAddHeader");
    let _btn = $("#BtnAddHeader");

    function _load_table_headers(domainId, repositoryId) {
        var _placeholder = $("#placeholder_headers_list");
        $.get("/repository/table/headers", $.param({domainId: domainId, identifier: repositoryId}))
            .done(function(page) {
                _placeholder
                    .empty()
                    .append(page);
                init_table_headers();
            });
    }
    function init_table_headers() {
        var _placeholder = $("#placeholder_headers_list");
        _placeholder.find("button.deletable.seecr-btn")
            .unbind("click")
            .click(function(e) {
                e.preventDefault();
                var _btn = $(this);
                let _frm = _btn.closest("form");
                $.post("/action/remove_header", _frm.serialize())
                    .done(function(data) {
                        if (data['success'] == true) {
                            _load_table_headers(data['domainId'], data['repositoryId']);
                        } else {
                            msg_Error(placeholder=$("#placeholder_headers_add"), identifier=undefined, text=data['message']);
                        }
                    })
            })
    }

    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/action/add_header", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        _load_table_headers(data['domainId'], data['repositoryId']);
                        form_resetBordersAndDisabled(_frm, _btn, true);
                    } else {
                        msg_Error(placeholder=$("#placeholder_headers_add"), identifier=undefined, text=data['message']);
                    }
                })
        })
    init_table_headers();
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

$(document).ready(function() {
    init_cardRepositoryAttributes();
    init_cardRepositoryActions();
    init_cardRepositoryFieldDefinitions();
    init_cardClosingHours();
    init_cardHeaders();


    init_button_status(); // from common.js

    $("button.helpText").each(function(index) {
        var _btn = $(this);
        _btn
            .unbind("click")
            .click(function(e) {
                e.preventDefault();
                var _modal = $("#modal");
                _modal.find("#placeholder_modal-title").html(_btn.data('caption'));
                $.get("/page2/modal/helpText", $.param({"text": _btn.data("helptext")}))
                    .done(function(data) {
                        _modal.find("#placeholder_modal-body")
                            .empty()
                            .append(data)
                        _modal.find("button")
                            .unbind("click")
                            .click(function(e) {
                                e.preventDefault();
                                _modal.modal("hide");
                            });
                    });
                _modal.modal("show");
            });
    })

})
