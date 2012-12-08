$(function(){$('#appSwitcher').selectbox({
    onChange: function (val, inst) {
        if ($('#appSwitcher').val()){
            $('#switchApp').submit()
        }
    },
    effect: "slide"
    });
});
