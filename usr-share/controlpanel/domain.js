function init_domainAttributes() {
    var _frm = $("#FrmDomainAttributes");
    var _btn = $("#BtnDomainAttributes");
    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            $.post)

            alert("DomainAttributes");

        });
    form_setBordersAndDisabled(_frm, _btn);
    form_resetBordersAndDisabled(_frm, _btn);
}

function init_cardRepositoryGroup() {
    var _frm = $("#FrmCreateRepositoryGroup");
    var _btn = $("#BtnCreateRepositoryGroup");
    _btn
        .unbind("click")
        .click(function(e) {
            e.preventDefault();
            alert("CreateRepositoryGroup");
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
