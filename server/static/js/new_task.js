var months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
var monthNamesShort = ['янв', 'фев', 'март', 'апр', 'май', 'июнь', 'июль', 'авг', 'сен', 'окт', 'ноя', 'дек'];
var dayNamesMin = [ 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
var isLockDate = false;
var synchronizedTags = [];
var maxIndex = 0;

function initNewTask() {
    $.datepicker.setDefaults( {'monthNames':months, 'dayNamesMin':dayNamesMin, 'firstDay':1, 'maxDate': Date.now(),
                                  dateFormat:'dd M yy', monthNamesShort:monthNamesShort} );

    attachDateTimePicker($( "input.datepicker" ));
    maxIndex = globalData['eventLoaded'];

    for (var i = 0; i < maxIndex; i++){
        initLoadedKey(i);
    }
}

function attachDateTimePicker(obj){
    obj.datetimepicker({timeFormat: 'hh:mm' /*, onSelect: onDateSelect*/});
}

/**
 * Возвращает следующий ключ
 * @return {*}
 */
function getNextKeyIndex(){
    var next_index = $('div.key_form_item').length
    do {
        next_index ++;
    } while ($('#key_' + next_index).length);
    return next_index
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

/**
 * Парсит дату
 * @param str_val
 * @return {*}
 */
function parseDate(str_val) {
    if (typeof str_val == 'undefined') return;
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
    if (typeof date == 'undefined') return;
    var d = date.getDate();
    var h = date.getHours();
    var m = date.getMinutes();
    return (d < 10 ? '0' + d : d) + ' ' + monthNamesShort[date.getMonth()] + ' ' + date.getFullYear() + ' '
        + (h < 10 ? '0' + h : h) + ':' + (m < 10 ? '0' + m : m);
}


/**
 * Включает уникальность
 * @param index
 * @param button
 */
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
//function lockDate(index) {
//    var buttons = $('.button.lock')
//    if (buttons.hasClass('unlock')) {
//        // lock
//        isLockDate = [$('input#start_' + index).val(), $('input#end_' + index).val()];
//        $('input.start').val(isLockDate[0]);
//        $('input.end').val(isLockDate[1]);
//        buttons.removeClass('unlock')
//    } else {
//        // unlock
//        isLockDate = false;
//        buttons.addClass('unlock')
//    }
//}

var currentCalendarSelector = {};

function dateToSend(date){
    return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + '-' + date.getHours() + '-' + date.getMinutes();
}

function getDateSelector(index, startWith){
    var data = {
        app: app,
        start:(parseDate($('#start_' + index).val())),
        end: (parseDate($('#end_' + index).val())),
        eventName: $('#key_' + index).val(),
        index: index,
        startWith: startWith
    };

    if (typeof startWith == 'undefined') {

        currentCalendarSelector = {
            start: data.start,
            end: data.end,
            oneDay: true
        };
    } else {
        data.start = currentCalendarSelector.start;
        data.end = currentCalendarSelector.end;
    }

    data.start = dateToSend(data.start);
    data.end = dateToSend(data.end);

    console.log(currentCalendarSelector);

    $.ajax({
        url: '/ajax/getDateSelector/',
        data: data,
        success: function(data){
            while (true) {
                var container = $('#top-key-menu-date-' + index + ' div.popover-content');
                if (container.length) {
                    container.html(data);

                    // setup graphic EQ
                    $( '#top-key-menu-date-' + index + ' span.timepicker' ).each(function() {
                        var sp = $(this);
                        var max = 59;
                        var isHour = sp.hasClass('hour');
                        var isStart = sp.hasClass('start');
                        if (isHour){ max = 23; }
                        var value = parseInt(sp.text(), 10);
                        console.log(value);
                        $( this ).empty().slider({
                            value: value,
                            min: 0,
                            max: max,
                            range: "min",
                            animate: true,
                            orientation: "horizontal",
                            slide: function( event, ui ) {
                                var d;
                                var value = parseInt(ui.value);
                                if (isStart) {
                                    d = currentCalendarSelector.start;
                                } else {
                                    d = currentCalendarSelector.end;
                                }

                                if (isHour) {
                                    d.setHours(value);
                                } else {
                                    d.setMinutes(value);
                                }

                                if (!isStart && value < 2){
                                    updateCalendarSelection();
                                }

                                $('#dateSelector-result').html(toDateString(currentCalendarSelector.start) + ' - ' + toDateString(currentCalendarSelector.end));
                            }
                        });
                    });
                    return;
                }
            }
        }
    });
    return 'Загрузка'
}

function setCalendarDate(day, month, year){
    var newDate = new Date();
    newDate.setHours(0, 0, 0, 0);
    newDate.setFullYear(year, month - 1, day);

    var td_end = $('table.calendar-table td.start');
    var td_start = $('table.calendar-table td.end');
    if (currentCalendarSelector.oneDay) {
        var currentTd = $('td.c-' + day + '-' + month + '-' + year);
        if (newDate < currentCalendarSelector.start) {
            console.log('set start');
            currentCalendarSelector.start = newDate;
            td_end.removeClass('start');
            currentTd.addClass('start');
        } else {
            console.log('set end');
            currentCalendarSelector.end = new Date(newDate.getTime() + 24 * 60 * 60 * 1000);
            td_start.removeClass('end');
            currentTd.addClass('end');
        }
        currentCalendarSelector.oneDay = false;
    } else {
        currentCalendarSelector.oneDay = true;
        currentCalendarSelector.start = newDate;
        currentCalendarSelector.end = new Date(newDate.getTime() + 24 * 60 * 60 * 1000);
        td_end.removeClass('start');
        td_start.removeClass('end');
        $('td.c-' + newDate.getDate() + '-' + (newDate.getMonth() + 1) + '-' + newDate.getFullYear()).addClass('start').addClass('end');
    }

    updateCalendarSelection();
    $('#dateSelector-result').html(toDateString(currentCalendarSelector.start) + ' - ' + toDateString(currentCalendarSelector.end));
}

function updateCalendarSelection(){
    var start = currentCalendarSelector.start.getTime() / 1000;
    var end = currentCalendarSelector.end.getTime() / 1000;
    $('table.calendar-table td.selected').removeClass('selected');
    while (start < end){
        var d = new Date(start * 1000);
        $('td.c-' + d.getDate() + '-' + (d.getMonth() + 1) + '-' + d.getFullYear()).addClass('selected');
        start += 24 * 60 * 60;
    }
}

function setDateInDateSelector(index){
    $('#start_' + index).val(toDateString(currentCalendarSelector.start));
    $('#end_' + index).val(toDateString(currentCalendarSelector.end));
    $('#dateSelector' + index)
        .html(toDateString(currentCalendarSelector.start) + ' - ' + toDateString(currentCalendarSelector.end))
        .popover('hide');
}

/**
 * Инициализирует загруженную форму ключа
 * @param index
 */
function initLoadedKey(index) {
    $('#dateSelector' + index).popover(
        {
            placement:'bottom',
            content: function(){return getDateSelector(index)},
            title: 'Выберите период',
            html: true
        }
    );

    attachDateTimePicker($( ".datepicker" + index ));

    $('.tag-type-help-' + index).popover({
                                             trigger:'hover',
                                             placement:'left',
                                             html:true,
                                             title:function () {
                                                 return getToolTipForTagType($(this).data('type'), 'title');
                                             },
                                             content:function () {
                                                 return getToolTipForTagType($(this).data('type'), 'content');
                                             }

                                         });

    $('.op-control-' + index + ' > span.label-op').popover({
                                             trigger:'hover',
                                             placement:'left',
                                             html:true,
                                             title:function () {
                                                 return getToolTipForTagOperation($(this).data('type'), 'title');
                                             },
                                             content:function () {
                                                 return getToolTipForTagOperation($(this).data('type'), 'content');
                                             }

                                         });

//    if (isLockDate) {
//        $("#start_" + index).val(isLockDate[0]);
//        $("#end_" + index).val(isLockDate[1]);
//        $('.button.lock').removeClass('unlock');
//    }
    $('#key_header_' + index).addClass('key_loaded');

    // синхронизация значени тегов
    for (var i in synchronizedTags) {
        var tag_name = synchronizedTags[i];
        $('.sync_' + tag_name).addClass('selected');
    }
}

/**
 * Удаляет ключ
 * @param eventIndex
 */
function deleteEvent(eventIndex) {
    $('#key_container_'+eventIndex).remove();
    globalData['eventLoaded']--;
    if (globalData['eventLoaded'] < 1) {
        $('#formSaveBlock').hide();
    }
}

/**
 * Переключалка интервалов
 * @param button
 */
function switchInterval(button){
    $(button).parent().children().removeClass('btn-info');
    $('#group_interval').val($(button).addClass('btn-info').data('value'));
    return false;
}


/**
 *
 * @param index - key index
 * @param tag - tag name
 * @param operation - operation (sum, group, avg)
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
        $(html_node).removeClass('label-warning');
    } else {
        // убираем
        operations.push(operation);
        $(html_node).addClass('label-warning');
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
 * @param index
 * @param tag_name
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

/**
 * Отправляет форму
 */
function sendForm() {
    if (globalData['eventLoaded']){
        $('#new_task_form').submit()
    } else {
        alert('Вы должны выбрать как минимум 1 ключ');
    }

}

/**
 * Сохраняет шаблон
 */
function saveTemplate(){
    if (globalData['eventLoaded']){
        var form = $('#new_task_form');
        form.attr('action', form.attr('action') + '?saveAsTemplate=1').submit();
    } else {
        alert('Вы должны выбрать как минимум 1 ключ');
    }
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
 * Выбор события
 * @param eventCode
 */
function selectAppEvent(eventCode) {
    // create event index
    var newEventIndex = getNextKeyIndex();
    var container = getNewContainerForEvent(newEventIndex);

    container.load(
        '/ajax/key_configuration',
        {eventCode: eventCode, appCode: app, index: maxIndex},
        function (responseText, textStatus, XMLHttpRequest) {
            initLoadedKey(maxIndex);
            $('#formSaveBlock').show();
            maxIndex = maxIndex + 1;
        });
    globalData['eventLoaded']++;
}

/**
 * Копирует ключ
 * @param index - индекс копируемого ключа
 */
function copyKey(index){
    var newEventIndex = getNextKeyIndex();
    var container = getNewContainerForEvent(newEventIndex);

    $.post('/ajax/copyTaskKey', 'copy_key_index=' + index + '&' + 'new_index=' + newEventIndex + '&'
        + $('#new_task_form').serialize(),
            function(data, textStatus, jqXHR){
                container.append(data);
                initLoadedKey(newEventIndex);
                globalData['eventLoaded']++;
    });
}

/**
 * Создает и возвращает контейнер для загрузки формы событий
 * @param index
 * @return {*}
 */
function getNewContainerForEvent(index){
    $('#formContainer').append('<div id="key_' + index + '_tag_container"></div>');
    return $('div#key_' + index + '_tag_container')
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


function getToolTipForTagType(tagType, type){
    if (type == 'title'){
        return $('#tag-tooltip-' + tagType + ' > .title').html();
    } else {
        return $('#tag-tooltip-' + tagType + ' > .content').html();
    }
}

/**
 *
 * @param opType
 * @param type
 * @return {*}
 */
function getToolTipForTagOperation(opType, type){
    if (type == 'title'){
        return $('#tag-op-tooltip-' + opType + ' > .title').html();
    } else {
        return $('#tag-op-tooltip-' + opType + ' > .content').html();
    }
}