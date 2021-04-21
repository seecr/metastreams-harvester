function init_table_groups() {
    $("#placeholder_groups").find(".clickable-row").click(function(e) {
        e.preventDefault();

        var _row = $(this);
        window.location.href = "/group?id=" + _row.data("id");
    });
}

$(document).ready(function() {
    $("#BtnCreateGroup")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _form = $("#FrmCreateGroup");
            $.post("/groups.action/createGroup", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        $.get("/groups/table/groups")
                            .done(function(data) {
                                $("#placeholder_groups")
                                    .empty()
                                    .append(data);
                                init_table_groups();
                            })
                    }
                })
        })
    init_table_groups();
})
