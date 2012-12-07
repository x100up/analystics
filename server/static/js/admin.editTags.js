function onChangeType(select, index) {
    if ($(select).val() == 'choose') {
        $('#tag_choose_' + index).show()
    } else {
        $('#tag_choose_' + index).hide()
    }
}

/**
 *
 * @param tag_index
 */
function setNew(tag_index, value){
    if (typeof value =='undefined') value = '';
    var countTag = $('#tag_' + tag_index + '_values_count');
    var count = parseInt(countTag.val());
    $('input.new_tag_value_' + tag_index + '.key').val(value).addClass('tag_' + tag_index + '_values_key').removeClass('key');
    $('input.new_tag_value_' + tag_index).removeAttr('onkeypress').removeClass('new_tag_value_' + tag_index).parent().parent().removeClass('new');

    count = count + 1;
    $('#tag_choose_' + tag_index + ' tbody').append('<tr class="new">'
                                                        + '<td><input type="text" onkeypress="setNew(' + tag_index + ')" '
                                                        + 'name="tag_' + tag_index + '_values_key_' + count + '" class="new_tag_value_' + tag_index + ' key"></td>'
                                                        + '<td><input type="text" onkeypress="setNew(' + tag_index + ')" '
                                                        + 'name="tag_' + tag_index + '_values_value_' + count + '" class="new_tag_value_' + tag_index + '"></td>'+
                                                        '</tr>');

    countTag.val(count);
}


function addKey(button) {
    var next_i = 0;
    while($('#key_' + next_i).length) {
        next_i += 1;
    }

    $.ajax('/ajax/add_new_key', {
        data: {'index': next_i},
        type: 'POST',
        success: function(data){
            $(button).before(data);
        }
    });
}

function addTag(button) {
    var next_i = 0;
    while($('#tag_' + next_i).length) {
        next_i += 1;
    }

    $.ajax('/ajax/add_new_tag', {
        data: {'index': next_i},
        type: 'POST',
        success: function(data){
            $(button).before(data);
        }
    });
}

function addBunch(button) {
    var next_i = 0;
    while($('#bunch_' + next_i).length) {
        next_i += 1;
    }

    $.ajax('/ajax/add_new_bunch', {
        data: {'index': next_i, appCode:appCode },
        type: 'POST',
        success: function(data){
            $(button).before(data);
        }
    });
}


function checkboxIsChecked(checkbox){
    return $(checkbox).attr('checked') != undefined
}

function onBunchSwitch(checkbox, eventCode, tags) {
    var tagCheckboxes = [];
    $('input.event_' + eventCode).each(function(i, cb){
        cb = $(cb);
        if ($.inArray(cb.data('tag'), tags) != -1){
            tagCheckboxes.push(cb);
        }
    });

    var i;
    if (checkboxIsChecked(checkbox)) {
        for (i in tagCheckboxes){
            tagCheckboxes[i].attr('disabled', 'disabled').attr('checked', 'checked');
        }
    } else {
        for (i in tagCheckboxes){
            tagCheckboxes[i].removeAttr('disabled').removeAttr('checked');
        }
    }
}

function deleteKey(index) {
    $('#key_' + index).remove();
}

/**
 * Вовзращает значения для тега если он choose
 * @param tag_index
 */
function getTagValues(tag_index) {
    var values = [];
    if ($('#tag_' + tag_index + '_type').val() == 'choose'){
        $('input.tag_' + tag_index + '_values_key').each(function(i, input){
            var val = $(input).val();
            if (val){
                values.push($(input).val());
            }
        });
    }
    return values;
}

/**
 * Добавляет знаяение для тега
 */
function addTagValue(value, tag_index, button) {
    if ($('#tag_' + tag_index + '_type').val() == 'choose'){
        setNew(tag_index, value);
        button = $(button);
        button.parent().css('color','green');
        button.remove();
    } else {
        alert('Тип тега должен быть "Выбор"');
    }
}