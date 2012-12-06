var months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
var monthNamesShort = ['янв', 'фев', 'март', 'апр', 'май', 'июнь', 'июль', 'авг', 'сен', 'окт', 'ноя', 'дек'];
var dayNamesMin = [ 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
var findModal = false;
var isLockDate = false;
var synchronizedTags = [];
var maxIndex = 0;

function initNewTask() {
    $('input.key_autocomplete').each(function(x, item){
        $(item).autocomplete({ serviceUrl:'/ajax/key_autocomplete?app=' + app , onSelect: onSelectKey.bind(item)});
    });

    $.datepicker.setDefaults( {'monthNames':months, 'dayNamesMin':dayNamesMin, 'firstDay':1, 'maxDate': Date.now(),
                                  dateFormat:'dd M yy', monthNamesShort:monthNamesShort} );

    attachDateTimePicker($( "input.datepicker" ));
    maxIndex = globalData['eventLoaded'];
}

function attachDateTimePicker(obj){
    obj.datetimepicker({timeFormat: 'hh:mm', onSelect: onDateSelect});
}

function selectAppEvent(eventCode) {
    // create event index
    maxIndex++;
    $('#formContainer').append('<div id="key_' + maxIndex + '_tag_container"></div>');

    $('div#key_' + maxIndex + '_tag_container').load(
        '/ajax/key_configuration',
        {eventCode: eventCode, appCode: app, index: maxIndex},
        function (responseText, textStatus, XMLHttpRequest) {
            initLoadedKey(maxIndex);
            $('#formSaveBlock').show();
        });
    globalData['eventLoaded']++;
}


function getNextKeyIndex(){
    var next_index = $('div.key_form_item').length
    do {
        next_index ++;
    } while ($('#key_' + next_index).length)
    return next_index
}

function addKey(){
    var next_index = getNextKeyIndex();
    $.ajax({
        url : '/ajax/get_key_form',
        type: 'post',
        data: {index: next_index, appCode: app },
        success: function(data) {
            $('div.add_key').before(data)
            removeSelection()
            initLoadedKeyForm(next_index)
        }
    })
}

/**
 * Событие при выборе даты
 * Синхронизирует даты при локе
 * @param dateText
 * @param inst
 */
function onDateSelect(dateText, inst) {
    var input;
    if (typeof inst.id == 'undefined'){
        input = inst.$input[0];
    } else {
        input = inst.input[0];
    }
    // --- корректировка
    var is_start = input.id.indexOf("start") != -1;
    input = $(input);
    var index = input.data('index');
    var startField = is_start ? input : $('#start_' + index);
    var endField = !is_start ? input: $('#end_' + index);
    var startDate = parseDate(startField.val());
    var endDate = parseDate(endField.val());
    var changeEnd =false;
    var changeStart =false;


    if (startDate >= endDate) {
        // если начало больше конца
        if (is_start) {
            endDate = new Date(startDate.getTime() + 86400000);
            changeEnd = true;
        } else {
            startDate = new Date(endDate.getTime() - 86400000);
            changeStart = true;
        }
    }

    var startVal = toDateString(startDate);
    var endVal = toDateString(endDate);

    if (changeEnd) {
        endField.val(endVal);
    }
    if (changeStart) {
        startField.val(startVal);
    }



    // --- синхронизация
    if (isLockDate) {
        if (is_start || changeStart) {
            $('input.start').val(startVal);
            isLockDate[0] = startVal
        }
        if (!is_start || changeEnd) {
            $('input.end').val(endVal);
            isLockDate[1] = endVal
        }
    }
}

function parseDate(str_val) {
    var result = null;
    for (var i in monthNamesShort) {
        var name = monthNamesShort[i];
        var isFind = str_val.indexOf(name) != -1;
        if (isFind) {
            var date = str_val.replace(name, parseInt(i) + 1);
            // меняем месяц и день местам
            date = date.replace(/^(\d+) (\d+)/, '$2 $1');
            result = new Date(Date.parse(date));
            break;
        }
    }
    return result;
}

function toDateString(date) {
    var d = date.getDate();
    var h = date.getHours();
    var m = date.getMinutes();
    return (d < 10 ? '0' + d : d) + ' ' + monthNamesShort[date.getMonth()] + ' ' + date.getFullYear() + ' '
        + (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m);
}

/**
 * При загрузки формы выбора ключа
 * @param index
 */
function initLoadedKeyForm(index) {
    attachDateTimePicker($( "#start_" + index ));
    attachDateTimePicker($( "#end_" + index ));
    if (isLockDate) {
        $("#start_" + index).val(isLockDate[0]);
        $("#end_" + index).val(isLockDate[1]);
        $('.button.lock').removeClass('unlock');
    }
}

function switchUserUnique(index, button) {
    var input = $('#userUnique' + index);
    var isChecked = input.attr('checked') != undefined;
    if (isChecked){
        input.removeAttr('checked');
        $(button).removeClass('checked');
    } else {
        input.attr('checked', 'checked');
        $(button).addClass('checked');
    }
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
        isLockDate = [$('input#start_' + index).val(), $('input#end_' + index).val()];
        $('input.start').val(isLockDate[0]);
        $('input.end').val(isLockDate[1]);
        buttons.removeClass('unlock')
    } else {
        // unlock
        isLockDate = false;
        buttons.addClass('unlock')
    }
}

/**
 * Инициализирует загруженную форму ключа
 * @param index
 */
function initLoadedKey(index) {
    initLoadedKeyForm(index);
    $('#key_header_' + index).addClass('key_loaded');

    // синхронизация значени тегов
    for (var i in synchronizedTags) {
        var tag_name = synchronizedTags[i];
        $('.sync_' + tag_name).addClass('selected');
    }
}

/**
 * Удаляет ключ
 * @param key
 */
function deleteKey(key) {
    $('#key_' + key + '_tag_container').remove();
    globalData['eventLoaded']--;
    if (globalData['eventLoaded'] < 1) {
        $('#formSaveBlock').hide();
    }
}




/**
 * Переключалка интервалов
 * @param li_object
 */
function switchInterval(li_object){
    $(li_object).parent().children().removeClass('selected');
    $('input#group_interval').val($(li_object).addClass('selected').data('value'));
}


/**
 *
 * @param index - key index
 * @param tag - tag name
 * @param operation - operation (sum, group, avg)
 * ! пока нельзя выбрать сумму и среднее одновременно
 */
function switchKeyOp(index, tag, operation, html_node) {
    var input = $('#tag_' + index + '_' + tag + '_ops');
    var val = input.val();
    var operations = [];
    if (val) {
        operations = val.split('/');
    }
    var op_index = jQuery.inArray(operation, operations);
    if (op_index != -1) {
        // уже есть
        operations.splice(op_index, 1);
        $(html_node).removeClass('selected');
    } else {
        // убираем
        /*
        if (operation == 'sum' || operation == 'avg') {
            var remove = operation == 'sum' ? 'avg' : 'sum';
            var op_index_r = jQuery.inArray(remove, operations);
            if (op_index_r != -1) { operations.splice(op_index_r, 1); }
            $('#' + remove + '_' + index + '_' + tag).removeClass('selected');
        }*/
        // ----------------
        operations.push(operation);
        $(html_node).addClass('selected');
    }

    input.val(operations.join('/'))
}

/**
 * Синхронизирует теги
 * @param index
 * @param tag_name
 * @param tag
 */
function switchTagSync(index, tag_name, tag) {
    tag = $(tag);
    if (tag.hasClass('selected')) {
        $('.sync_' + tag_name).removeClass('selected');
        var i = jQuery.inArray(tag_name, synchronizedTags);
        if (i != -1) {
            synchronizedTags.splice(i, 1);
        }
    } else {
        $('.sync_' + tag_name).addClass('selected');
        synchronizedTags.push(tag_name);
        // первоначальное копирование значений
    }
}

/**
 * Добавляет дополительное текстовое поле
 * @param input
 */
function addTextField(index, tag_name) {

    var isSync = synchronizedTags.indexOf(tag_name) != -1;
    console.log(synchronizedTags, isSync)
    if (isSync) {
        inputs = $('.new.tag_' + tag_name);
    } else {
        inputs = $('#' + tag_name + '_value_cloner_' + index);
    }
    inputs.each(function(i){
        var input = $(inputs[i]);
        var fi = parseInt($(input.prev()).data('index')) + 1;
        input.after(input.clone()).attr('onclick', '').removeAttr('id').removeClass('new').addClass('i_' + fi).data('index', fi);
        if ($('input[name|=' + input.attr('name') + ']').length == 5) {
            input.parent().addClass('more_value')
        }
    });
}

/**
 *
 * @param input
 * @param tag_name
 * @param index
 */
function tagValueChange(type, input, tag_name, index) {
    var isSync = synchronizedTags.indexOf(tag_name) != -1;
    if (!isSync) return;

    input = $(input);
    switch (type) {
        case 'string':
            // текстовое поле
            var inputIndex = input.data('index');
            $('.tag_' + tag_name + '.i_' + inputIndex).val(input.val());
        break;
    }

}

function sendForm() {
    if (globalData['eventLoaded']){
        $('#new_task_form').submit()
    } else {
        alert('Вы должны выбрать как минимум 1 ключ');
    }

}

/**
 * Модальное окно шаблона
 */
function saveTemplate(){
    $.ajax({
               url: '/ajax/getTemplateModal',
               data: {},
               success: function(data){
                   findModal = $('#myModal').empty().append(data).reveal();
               }
           });
}

function selectTemplate(){
    $.ajax({
               url: '/ajax/getTemplateListModal/' + app,
               data: {},
               success: function(data){
                   $('#myModal').empty().append(data).reveal();
               }
           });
}

/**
 * Сохранение шаблона
 */
function doSaveTemplate(){
    if (globalData['eventLoaded']){
        $('#new_task_form').append($('#template_modal_form')).attr('action', '/template/create/' + app).submit();
    } else {
        alert('Вы должны выбрать как минимум 1 ключ');
    }
}

/**
 * Копирует ключ
 * @param index - индекс копируемого ключа
 */
function copyKey(index){
    var new_index = getNextKeyIndex();
    $.post('/ajax/copyTaskKey', 'copy_key_index=' + index + '&' + 'new_index=' + new_index + '&'
        + $('#new_task_form').serialize(),
            function(data, textStatus, jqXHR){
                $('#key_container_' + index).parent().children(':last').after(data);
                initLoadedKey(new_index);
    });
}

function resetRadio(radio) {
    radio = $(radio);
    if (radio.hasClass('checked')) {
        radio.removeAttr('checked').removeClass('checked');
    } else {
        radio.addClass('checked');
        var other_id = radio.attr('name') + '_' + (radio.val() == '0' ? '1' : '0');
        $('#' + other_id).removeClass('checked');
    }
}

//----------------------------------------------------
// ------------------- HELPERS -----------------------
//----------------------------------------------------


Function.prototype.bind = function (scope) {
    var fn = this;
    return function () {
        return fn.apply(scope, arguments);
    };
};

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