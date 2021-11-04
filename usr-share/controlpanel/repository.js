function init_cardRepositoryAttributes() {
    var _frm = $("#FrmRepositoryAttributes");
    var _btn = $("#BtnRepositoryAttributes");
    _btn
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/updateRepositoryAttributes", _frm.serialize())
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
                $.post("/actions/deleteRepositoryClosingHours", $.param({
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
            $.post("/actions/addRepositoryClosingHours", _frm.serialize())
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
        $("#FrmRepositoryActions"), "/actions/updateRepositoryActionAttributes",
        $("#BtnRepositoryActions"), $("#placeholder_FrmRepositoryActions"));
}

$(document).ready(function() {
    init_cardRepositoryAttributes();
    init_cardRepositoryActions();
    init_cardClosingHours();

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
