$(document).ready(function() {
    $("#BtnUpdateGroup")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _form = $("#FrmUpdateGroup");
            $.post("/groups.action/updateGroup", _form.serialize())
                .done(function(data) {
                    if (data['success'] == false) {
                        errorMessage(data['message']);
                    }
                })
        })
})
