function init_table_groups(placeholder) {
    placeholder.find(".clickable-row").click(function(e) {
        e.preventDefault();

        var _row = $(this);
        window.location.href = "/group?id=" + _row.data("id");
    });
}

$(document).ready(function() {
    var _form = $("#FrmCreateGroup");
    var _createButton = $("#BtnCreateGroup");

    _createButton
        .prop('disabled', true)
        .unbind("click")
        .click(function(e) {
            e.preventDefault();

            $.post("/groups.action/createGroup", _form.serialize())
                .done(function(data) {
                    if (data['success'] == true) {
                        $.get("/groups/table/groups")
                            .done(function(data) {
                                var _placeholder = $("#placeholder_groups");
                                _placeholder
                                    .empty()
                                    .append(data);
                                _form.trigger("reset");
                                _createButton.prop('disabled', true);
                                _form.find('.border-warning').each(function() {
                                    $(this).removeClass('border-warning');
                                })
                                init_table_groups(_placeholder);
                            })
                    }
                })
        })

    init_table_groups($("#placeholder_groups"));

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
