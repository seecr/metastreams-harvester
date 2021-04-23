function init_table_domains(placeholder) {
    placeholder.find(".clickable-row").click(function(e) {
        e.preventDefault();

        var _row = $(this);
        alert("Wanting to edit " + _row.data("id"));
    });
}

$(document).ready(function() {
    var _form = $("#FrmCreateDomain");
    var _createButton = $("#BtnCreateDomain");

    _createButton
        .prop("disabled", true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            $.post("/action/addDomain", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        $.get("/domains/table/domains")
                            .done(function(data) {
                                var _placeholder = $("#placeholder_domains");
                                _placeholder
                                    .empty()
                                    .append(data);
                                _form.trigger("reset");
                                _createButton.prop('disabled', true);
                                _form.find('.border-warning').each(function() {
                                    $(this).removeClass('border-warning');
                                })
                                init_table_domains(_placeholder);
                            })
                    }
                })
        })

    init_table_domains($("#placeholder_domains"));

	_form.find("input").keyup(function(e) {
        var _input = $(this);
        if (!_input.hasClass("border-warning")) {
            _input.addClass("border-warning");
        }
        if (_createButton.prop('disabled') == true) {
            _createButton.prop('disabled', false);
        }
	});
})
