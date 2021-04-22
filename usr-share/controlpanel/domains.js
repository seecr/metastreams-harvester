function init_table_domains(placeholder) {
    placeholder.find(".clickable-row").click(function(e) {
        e.preventDefault();

        var _row = $(this);
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
                                var _placeholder = $("#placeholder_domains");
                                _placeholder
                                    .empty()
                                    .append(data);
                                init_table_domains(placeholder);
                            })
                    }
                })
        })

    init_table_domains($("#placeholder_domains"));
})
