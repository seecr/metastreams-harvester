function init_domainAttributes() {
    form_init($("#FrmDomainAttributes"), "/actions/updateDomain", $("#BtnDomainAttributes"), $("#placeholder_FrmDomainAttributes"));
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
    form_init(_frm, "/actions/addRepositoryGroup", _btn, $("#placeholder_FrmCreateRepositoryGroup"), function() {_load_table_repositoryGroups(_frm.data("domainid"))});
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
                            msg_Error(
                                placeholder=_placeholder,
                                text=data['message'] || "Er ging iets niet goed.");
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
                        form_init(
                            $("#FrmUpdateTarget"), "/action/updateTarget",
                            $("#BtnUpdateTarget"), $("#placeholder_FrmUpdateTarget"),
                            function() {_load_table_targets(_row.data('domainid'))})
                        _modal.modal('show');
                   })
            });
    }
    init_table_targets();
    form_init(
        _frm, "/actions/addTarget", _btn,
        $("#placeholder_FrmCreateTarget"),
        function() {_load_table_targets(_frm.data("domainid"))});
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

                        form_init(
                            $("#FrmUpdateMapping"), "/action/updateMapping",
                            $("#BtnUpdateMapping"), $("#placeholder_FrmUpdateMapping"),
                            function() {_load_table_mappings(_row.data('domainid'))})
                        _modal.modal('show');
                   })
            });
    }
    init_table_mappings();
    form_init(
        _frm, "/actions/addMapping", _btn, $("#placeholder_FrmCreateMapping"),
        function() {_load_table_mappings(_frm.data("domainid"))});
}

function init_cardFieldDefinition() {
    form_init(
        $("#FrmFieldDefinition"), "/actions/updateFieldDefinition",
        $("#BtnFieldDefinition"), $("#placeholder_FrmFieldDefinition"));
}

$(document).ready(function() {
    init_domainAttributes();
    init_cardRepositoryGroup();
    init_cardTarget();
    init_cardMapping();
    init_cardFieldDefinition();

    init_button_status(); // from common.js
})
