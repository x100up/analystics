var months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
var monthNamesShort = ['янв', 'фев', 'март', 'апр', 'май', 'июнь', 'июль', 'авг', 'сен', 'окт', 'ноя', 'дек'];
var dayNamesMin = [ 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
var findModal = false;

$(function(){
    $('input.key_autocomplete').each(function(x, item){
        $(item).autocomplete({ serviceUrl:'/ajax/key_autocomplete?app=' + appCode , onSelect: onSelectKey.bind(item)});
    });

    $.datepicker.setDefaults( {'monthNames':months, 'dayNamesMin':dayNamesMin, 'firstDay':1, 'maxDate': Date.now(),
                                  dateFormat:'dd M yy', monthNamesShort:monthNamesShort} );

    $( "input.datepicker" ).datetimepicker({timeFormat: 'hh:mm'});
});

function onSelectKey(keyName, index) {
    $('#key_' + index).val(keyName)
    if (index === undefined)
        index = $(this).data('index')
    // загружаем конфигурацию
    $('div#key_' + index + '_tag_container').load('/ajax/key_configuration', {'key':keyName, 'app': appCode, 'index':index})
    $('#myModal').trigger('reveal:close');
    $('#key_header_' + index).addClass('key_loaded')
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

function switchInterval(li_object){
    $(li_object).parent().children().removeClass('selected');
    $('input#group_interval').val($(li_object).addClass('selected').data('value'));
}

/**
 * Запрещает редактировать дату
 * Выставляетя дату на новых и существующих ключах как на залоченом
 * @param index
 */
function lockDate(index) {
    var buttons = $('.button.lock')
    if (buttons.hasClass('unlock')) {
        // lock
        $('input.start').val($('input#start_' + index).val());
        $('input.end').val($('input#end_' + index).val());
        //$('input.datepicker').attr('disabled', 'disabled');
        buttons.removeClass('unlock')
    } else {
        // unlock
        buttons.addClass('unlock')
        //$('input.datepicker').removeAttr('disabled')
    }
}

/**
 *
 * @param index - key index
 * @param tag - tag name
 * @param operation - operation (sum, group, avg)
 */
function switch_key_op(index, tag, operation, html_hode) {
    var input = $('#tag_' + index + '_' + tag + '_ops');
    var val = input.val();
    var operations = []
    if (val) {
        operations = val.split('/');
    }
    var op_index = jQuery.inArray(operation, operations);
    console.log(operations)
    if (op_index != -1) {
        operations.splice(op_index, 1);
        $(html_hode).removeClass('selected');
    } else {
        operations.push(operation);
        $(html_hode).addClass('selected');
    }

    input.val(operations.join('/'))
}

/**
 * Добавляет дополительное текстовое поле
 * @param input
 */
function addTextField(input) {
    input = $(input);
    input.after(input.clone()).attr('onclick', '').removeClass('new')
    if ($('input[name|=' + input.attr('name') + ']').length == 5) {
        input.parent().addClass('more_value')
    }
}