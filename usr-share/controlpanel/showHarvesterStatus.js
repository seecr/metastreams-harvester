
function init_status() {
    var _table = $("#status-table");

    _table.find(".seecr-show-error")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _btn = $(this);
            var _domainId = _btn.data('domainid'); 
            var _repositoryGroupId = _btn.data('repositorygroupid'); 
            var _repositoryId = _btn.data('repositoryid');
            $.get("/showHarvesterStatus/data/error?" + $.param({
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

function init_table() {
	$("#status-table").dataTable({
        searching: false,
        paging: false,
        info: false,
        columnDefs: [
            {
                searchable: false,
                orderable: false,
                targets: 8
            }
        ],
    });
}

$(document).ready(function() {
	init_status();
	init_table();
});
