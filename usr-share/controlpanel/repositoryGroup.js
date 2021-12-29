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

function init_domainAttributes() {
    form_init(
        $("#FrmRepositoryGroupAttributes"), "/actions/updateRepositoryGroup",
        $("#BtnRepositoryGroupAttributes"), $("iplaceholder_FrmRepositoryGroupAttributes"));
}

function init_cardRepositories() {
    var _frm = $("#FrmCreateRepository");
    var _btn = $("#BtnCreateRepository");

    function _load_table_repositories(domainId, repositoryGroupId) {
        var _placeholder = $("#placeholder_table_repositories");
        $.get("/repositoryGroup/table/repositories", $.param({domainId: domainId, repositoryGroupId: repositoryGroupId}))
            .done(function(page) {
                _placeholder
                    .empty()
                    .append(page);
                init_table_repositories();
            });
    }


    function init_table_repositories() {
        var _placeholder = $("#placeholder_table_repositories");
        _placeholder.find("button.deletable.seecr-btn")
            .unbind("click")
            .click(function(e) {
                var _btn = $(this);
                var _domainId = _btn.data('domainid');
                var _repositoryGroupId = _btn.data('repositorygroupid');
                e.preventDefault();
                $.post("/actions/deleteRepository", $.param({identifier: _btn.data('identifier'), domainId: _domainId, repositoryGroupId: _repositoryGroupId}))
                    .done(function(data) {
                        if (data['success'] == true) {
                            _load_table_repositories(_domainId, _repositoryGroupId);
                        } else {
                            console.log(data);
                        }
                    })

            })
    }
    init_table_repositories();

    form_init(
        _frm, "/actions/addRepository",
        _btn, $("#placeholder_FrmCreateRepository"),
        function() {_load_table_repositories(_frm.data("domainid"), _frm.data("repositorygroupid"))});
}

$(document).ready(function() {
    init_domainAttributes();
    init_cardRepositories();
    
    init_button_status(); // from common.js
})
