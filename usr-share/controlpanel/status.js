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

function _init_status_table() {
    var _table = $("#status-table");

    console.log(_table.find(".seecr-show-error"));
    _table.find(".seecr-show-error")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _btn = $(this);
            var _domainId = _btn.data('domainid'); 
            var _repositoryGroupId = _btn.data('repositorygroupid'); 
            var _repositoryId = _btn.data('repositoryid');
            $.get("status/data/error?" + $.param({
                    domainId: _domainId, 
                    repositoryGroupId: _repositoryGroupId, 
                    repositoryId: _repositoryId}))
                .done(function(data) {
                    var _error_modal = $("#modal_error");
                    var _error_modal_body = _error_modal.find("#placeholder_modal-error-body");
                    _error_modal.find("#placeholder_modal-error-title").html(_domainId + " > " + _repositoryGroupId + " > " + _repositoryId);
                    _error_modal_body
                        .empty()
                        .append(data);
                    _error_modal.find("button.btn-close")
                        .unbind("click")
                        .click(function(e) {
                            e.preventDefault();
                            _error_modal.modal("hide");
                        });
                    _error_modal.modal("show");
            });
        });
}


function old_init_status_table(domainId, repositoryGroupId, repositoryId) {
    var _table = $("#status-table");
    var _table_tbody = $("#status-table tbody");


    _table.DataTable({
        searching: false,
        paging: false,
        info: false,
        ajax: "/status/data/status?" + $.param({
            domainId: domainId,
            repositoryGroupId: repositoryGroupId,
            repositoryId: repositoryId}),
        columnDefs: [
          {  targets: 5,
             render: function (data, type, row, meta) {
                 console.log(meta);
                return data + '<button class="btn btn-sm btn-primary id="n-' + meta.row + '">Bekijk</button>';
             }

          }
        ]
    });
    _table_tbody.delegate("tr", "click", function (e) {
        e.preventDefault();

        var _icon = $(this);
        alert("clicked on " + _icon)
    });
}
