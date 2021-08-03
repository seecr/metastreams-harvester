function init_domainAttributes() {
    var _frm = $("#FrmDomainAttributes");
    var _btn = $("#BtnDomainAttributes");
    _btn
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/updateDomain", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn);
                    } else {
                        alert("Something went wrong!");
                    }
                })
        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardRepositoryGroup() {
    var _frm = $("#FrmCreateRepositoryGroup");
    var _btn = $("#BtnCreateRepositoryGroup");

    function _load_table_repositoryGroups(domainId) {
        var _placeholder = $("#placeholder_table_repositorygroups");
        $.get("/domain/table/repositoryGroup", $.param({identifier: domainId}))
            .done(function(page) {
                _placeholder
                    .empty()
                    .append(page);
                init_table_repositoryGroups();
            });
    }


    function init_table_repositoryGroups() {
        var _placeholder = $("#placeholder_table_repositorygroups");
        _placeholder.find("button.deletable.seecr-btn")
            .unbind("click")
            .click(function(e) {
                var _btn = $(this);
                var _domainId = _btn.data('domainid');
                e.preventDefault();
                $.post("/actions/deleteRepositoryGroup", $.param({identifier: _btn.data('groupid'), domainId: _domainId}))
                    .done(function(data) {
                        if (data['success'] == true) {
                            _load_table_repositoryGroups(_domainId);
                        } else {
                            console.log(data);
                        }
                    })

            })
    }
    init_table_repositoryGroups();
    _btn
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/addRepositoryGroup", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn, true);
                        _load_table_repositoryGroups(_frm.data("domainId"));
                    } else {
                        msg_Error(placeholder=$("#placeholder_FrmCreateRepositoryGroup"), identifier=undefined, text=data['message']);
                    }
                })
        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardTarget() {
    var _frm = $("#FrmCreateTarget");
    var _btn = $("#BtnCreateTarget");
    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            alert("CreateTarget");
        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardMapping() {
    var _frm = $("#FrmCreateMapping");
    var _btn = $("#BtnCreateMapping");
    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            alert("CreateMapping");
        })
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

$(document).ready(function() {
    init_domainAttributes();
    init_cardRepositoryGroup();
    init_cardTarget();
    init_cardMapping();
})
