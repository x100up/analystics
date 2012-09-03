var months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
var dayNamesMin = [ 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
var findModal = false;

$(function(){
    $('input.key_autocomplete').each(function(x, item){
        $(item).autocomplete({ serviceUrl:'/ajax/key_autocomplete?app=' + appCode , onSelect: onSelectKey.bind(item)});
    });

    $.datepicker.setDefaults( {'monthNames':months, 'dayNamesMin':dayNamesMin, 'firstDay':1, 'maxDate': Date.now()} );

    $( "input.datepicker" ).datetimepicker({timeFormat: 'hh:mm'});
});

function onSelectKey(keyName, index) {
    $('#key_' + index).val(keyName)
    if (index === undefined)
        index = $(this).data('index')
    // загружаем конфигурацию
    $('div#key_'+index+'_tag_container').load('/ajax/key_configuration', {'key':keyName, 'app': appCode})
    $('#myModal').trigger('reveal:close');
}


function addKey(){
    var next_index = $('div.key_form_item').length
    do {
        next_index ++;
    } while ($('#key_' + next_index).length)

    $.ajax({
        url : '/ajax/get_key_form',
        type: 'post',
        data: {index: next_index},
        success: function(data) {
            $('div.add_key').before(data)
            removeSelection()
            $( "input.datepicker" ).datetimepicker({timeFormat: 'hh:mm'});
            $('input#key_' + next_index).autocomplete({ serviceUrl:'/ajax/key_autocomplete?app=' + appCode ,
                onSelect: onSelectKey.bind($('#key_' + next_index)[0])});
        }
    })
}

function deleteKey(key) {
    $('#key_container_' + key).remove();
}

function removeSelection(){
    if (window.getSelection) {
        if (window.getSelection().empty) {  // Chrome
            window.getSelection().empty();
        } else if (window.getSelection().removeAllRanges) {  // Firefox
            window.getSelection().removeAllRanges();
        }
    } else if (document.selection) {  // IE?
        document.selection.empty();
    }

}
function findKey(index){
    $.ajax({
        url: '/ajax/getKeys/' + appCode + '/',
        data: {index: index},
        success: function(data){
            findModal = $('#myModal').empty().append(data).reveal();
        }
    });
}

Function.prototype.bind = function (scope) {
    var fn = this;
    return function () {
        return fn.apply(scope, arguments);
    };
};