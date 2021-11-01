function init_domainAttributes() {
    var _frm = $("#FrmRepositoryGroupAttributes");
    var _btn = $("#BtnRepositoryGroupAttributes");
    _btn
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/updateRepositoryGroup", _frm.serialize())
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

function init_cardRepositories() {
    var _frm = $("#FrmCreateRepository");
    var _btn = $("#BtnCreateRepository");
    console.log(_btn);

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

    _btn
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/addRepository", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn, true);
                        _load_table_repositories(_frm.data("domainid"), _frm.data("repositorygroupid"));
                    } else {
                        msg_Error(placeholder=$("#placeholder_FrmCreateRepository"), identifier=undefined, text=data['message']);
                    }
                })
        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

$(document).ready(function() {
    init_domainAttributes();
    init_cardRepositories();
})
