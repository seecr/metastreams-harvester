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
                        _load_table_repositoryGroups(_frm.data("domainid"));
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


    function _load_table_targets(domainId) {
        var _placeholder = $("#placeholder_table_targets");
        $.get("/domain/table/targets", $.param({identifier: domainId}))
            .done(function(page) {
                _placeholder
                    .empty()
                    .append(page);
                init_table_targets();
            });
    }

    function init_table_targets() {
        var _placeholder = $("#placeholder_table_targets");
        _placeholder.find("button.deletable.seecr-btn")
            .unbind("click")
            .click(function(e) {
                var _btn = $(this);
                var _domainId = _btn.data('domainid');
                e.preventDefault();
                $.post("/actions/deleteTarget", $.param({identifier: _btn.data('targetid'), domainId: _domainId}))
                    .done(function(data) {
                        if (data['success'] == true) {
                            _load_table_targets(_domainId);
                        } else {
                            console.log(data);
                        }
                    })

            });
        _placeholder.find("tr.clickable-row")
            .unbind("click")
            .click(function(e) {
                e.preventDefault();
                var _row = $(this);

                $.get('/domain/popup/target', $.param({domainId: _row.data('domainid'), identifier: _row.data('targetid')}))
                    .done(function(data) {
                        var _modal = $("#modal");
                        var _modal_body = _modal.find("#placeholder_modal-body");
                        _modal.find("#placeholder_modal-title").html("Target");
                        _modal_body
                            .empty()
                            .append(data);
                        var _frm = _modal_body.find("#FrmUpdateTarget");
                        var _btn = _modal_body.find("#BtnUpdateTarget");

                        _btn
                            .unbind("click")
                            .click(function(e) {
                                e.preventDefault();
                                $.post("/action/updateTarget", _frm.serialize())
                                    .done(function(data) {
                                        if (data['success'] == true) {
                                            _load_table_targets(_row.data('domainid'));
                                            form_setBordersAndDisabled(_frm, _btn);
                                            form_resetBordersAndDisabled(_frm, _btn);
                                        } else {
                                            msg_Error(
                                                placeholder=$("#placeholder_FrmUpdateTarget"),
                                                identifier=undefined,
                                                text=data['message'] || "Er ging iets niet goed.");

                                        }
                                    });
                            });
                        form_setBordersAndDisabled(_frm, _btn);
                        form_resetBordersAndDisabled(_frm, _btn);
                        _modal.modal('show');
                   })
            });
    }
    init_table_targets();

    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/addTarget", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn, true);
                        _load_table_targets(_frm.data("domainid"));
                    } else {
                        msg_Error(placeholder=$("#placeholder_FrmCreateTarget"), identifier=undefined, text=data['message']);
                    }
                })
        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardMapping() {
    var _frm = $("#FrmCreateMapping");
    var _btn = $("#BtnCreateMapping");

    function _load_table_mappings(domainId) {
        var _placeholder = $("#placeholder_table_mappings");
        $.get("/domain/table/mappings", $.param({identifier: domainId}))
            .done(function(page) {
                _placeholder
                    .empty()
                    .append(page);
                init_table_mappings();
            });
    }

    function init_table_mappings() {
        var _placeholder = $("#placeholder_table_mappings");
        _placeholder.find("button.deletable.seecr-btn")
            .unbind("click")
            .click(function(e) {
                var _btn = $(this);
                var _domainId = _btn.data('domainid');
                e.preventDefault();
                $.post("/actions/deleteMapping", $.param({identifier: _btn.data('mappingid'), domainId: _domainId}))
                    .done(function(data) {
                        if (data['success'] == true) {
                            _load_table_mappings(_domainId);
                        } else {
                            console.log(data);
                        }
                    })

            });

        _placeholder.find("tr.clickable-row")
            .unbind("click")
            .click(function(e) {
                e.preventDefault();
                var _row = $(this);

                $.get('/domain/popup/mapping', $.param({domainId: _row.data('domainid'), identifier: _row.data('mappingid')}))
                    .done(function(data) {
                        var _modal = $("#modal");
                        var _modal_body = _modal.find("#placeholder_modal-body");
                        _modal.find("#placeholder_modal-title").html("Mapping");
                        _modal_body
                            .empty()
                            .append(data);


                        var _frm = _modal_body.find("#FrmUpdateMapping");
                        var _btn = _modal_body.find("#BtnUpdateMapping");

                        _btn
                            .unbind("click")
                            .click(function(e) {
                                e.preventDefault();
                                $.post("/action/updateMapping", _frm.serialize())
                                    .done(function(data) {
                                        if (data['success'] == true) {
                                            _load_table_mappings(_row.data('domainid'));
                                            form_setBordersAndDisabled(_frm, _btn);
                                            form_resetBordersAndDisabled(_frm, _btn);
                                        } else {
                                            msg_Error(
                                                placeholder=$("#placeholder_FrmUpdateMapping"),
                                                identifier=undefined,
                                                text=data['message'] || "Er ging iets niet goed.");
                                        }
                                    });
                            });
                        form_setBordersAndDisabled(_frm, _btn);
                        form_resetBordersAndDisabled(_frm, _btn);

                        _modal.modal('show');
                   })
            });
    }
    init_table_mappings();
    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/addMapping", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn, true);
                        _load_table_mappings(_frm.data("domainid"));
                    } else {
                        msg_Error(placeholder=$("#placeholder_FrmCreateMapping"), identifier=undefined, text=data['message']);
                    }
                })
        })
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardFieldDefinition() {
    var _frm = $("#FrmFieldDefinition");
    var _btn = $("#BtnFieldDefinition");

    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post("/actions/updateFieldDefinition", _frm.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        form_resetBordersAndDisabled(_frm, _btn, true);
                    } else {
                        msg_Error(placeholder=$("#placeholder_FrmFieldDefinition"), identifier=undefined, text=data['message']);
                    }
                })
        })
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

$(document).ready(function() {
    init_domainAttributes();
    init_cardRepositoryGroup();
    init_cardTarget();
    init_cardMapping();
    init_cardFieldDefinition();
})
