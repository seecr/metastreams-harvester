
/* ---------- Users */
function reload_userscard(groupId) {
    $.get("/group/card/users", "groupId="+groupId)
        .done(function(data) {
            var _card = $("#placeholder_userscard");
            _card
                .empty()
                .append(data);
            init_userscard(_card);
        })
}

function init_userscard(placeholder) {
    placeholder.find("#BtnAddUserToGroup")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _form = $("#FrmAddUserToGroup");
            $.post("/groups.action/addUsername", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_userscard(_groupId);
                    }
                })
        });

    placeholder.find("#TblGroupUsers").find(".deletable")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _button = $(this);
            var _form = _button.closest("form");
            $.post("/groups.action/removeUsername", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_userscard(_groupId);
                    }
                });
        });
}

/* ---------- Domains */
function reload_domainscard(groupId) {
    $.get("/group/card/domains", "groupId="+groupId)
        .done(function(data) {
            var _card = $("#placeholder_domainscard");
            _card
                .empty()
                .append(data);
            init_domainscard(_card);
        })
}

function init_domainscard(placeholder) {
    placeholder.find("#BtnAddDomainIdToGroup")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _form = $("#FrmAddDomainIdToGroup");
            $.post("/groups.action/addDomain", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_domainscard(_groupId);
                    }
                })
        });

    placeholder.find("#TblGroupDomains").find(".deletable")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _button = $(this);
            var _form = _button.closest("form");
            $.post("/groups.action/removeDomain", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        var _groupId = _form.find('input[name="groupId"]').val();
                        reload_domainscard(_groupId);
                    }
                });
        });
}

$(document).ready(function() {
    init_domainscard($("#placeholder_domainscard"));
    init_userscard($("#placeholder_userscard"));
})
