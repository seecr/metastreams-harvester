function init_table_groups() {
    $("#TblDomains").find(".clickable-row").click(function(e) {
        e.preventDefault();

        alert("Wanting to edit " + _row.data("id"));
    });
}

$(document).ready(function() {
    $("#BtnCreateDomain")
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            var _form = $("#FrmCreateDomain");
            $.post("/action/addDomain", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        $.get("/domains/table/domains")
                            .done(function(data) {
                                $("#placeholder_domains")
                                    .empty()
                                    .append(data);
                                init_table_domains();
                            })
                    }
                })
        })
    init_table_domains();
})
