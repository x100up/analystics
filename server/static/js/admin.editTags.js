function onChangeType(select, index) {
   if ($(select).val() == 'choose') {
        $('#tag_choose_' + index).show()
   } else {
       $('#tag_choose_' + index).hide()
   }
}

function setNew(tag_index){
    var countTag = $('#tag_' + tag_index + '_values_count');
    var count = parseInt(countTag.val());
    $('input.new_tag_value_' + tag_index).removeAttr('onkeypress').parent().parent().removeClass('new');
    count = count + 1;
    $('#tag_choose_' + tag_index + ' tbody').append('<tr class="new">'
        + '<td><input type="text" onkeypress="setNew(' + tag_index + ')" '
        + 'name="tag_' + tag_index + '_values_key_' + count + '" class="new_tag_value_' + tag_index + '"></td>'
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
        data: {'index': next_i},
        type: 'POST',
        success: function(data){
            $(button).before(data);
        }
    });
}

function updateKey(index) {
    $('#key_' + index + '_h').text($('#key_' + index + '_name').val());
}

function deleteKey(index) {
    $('#key_' + index).remove();
    if (relation_cache[index] != undefined) {
        delete relation_cache[index];
    }
}

function saveForm(){
    updateKeyTags();
    $('#tag_form').submit();
}

function updateKeyTags(button) {
    var index = 0, bunch = null, tag_index = null, bunchesForTag = null;
    var checked = false;
    // keys list
    var keyList = {};
    $('input[name="key_index"]').each(function(index, tag){
        index = $(tag).val();
        keyList[index] = {'name': $('#key_' + index + '_name').val(), 'desc': $('#key_' + index + '_desc').val()};
    });

    // tags list
    var tagList = {};
    $('input[name="tag_index"]').each(function(index, tag){
        index = $(tag).val();
        tagList[index] = $('#tag_' + index + '_code').val();
    });

    // list of bunches
    var bunchList = {};
    $('input[name="bunch_index"]').each(function(index, tag){
        index = $(tag).val();
        bunchList[index] = {'code': $('#bunch_code_' + index).val(), 'name': $('#bunch_name_' + index).val()};
    });

    var html = '';
    for (var key_index in keyList) {
        var key_values = keyList[key_index];
        html += '<h3>' + (key_values['desc'] ? key_values['desc'] : key_values['name']) + '</h3>';

        var list = '';
        for (tag_index in tagList) {
            tag_index = parseInt(tag_index);
            checked = (relation_cache['tag'][key_index] != undefined) && ($.inArray(tag_index, relation_cache['tag'][key_index]) != -1);

            classes = '';
            var bunches_indexes = getBunchesForTag(tag_index);
            for (bunch_index in bunches_indexes){
                bunch_index = bunches_indexes[bunch_index];
                if ($.inArray(bunch_index, relation_cache['bunch'][key_index]) > -1) {
                    classes = ' b_' + bunch_index;
                }
            }

            list += '<li><input type="checkbox" name="key_tag_' + key_index + '" value="' + tag_index + '" '
                + (checked || classes ? 'checked="checked"' : '')
                + (classes ? 'disabled="disabled"' : '')
                + ' class="k_' + key_index + ' t_' + tag_index + classes + '" onclick="changeRelationCache(this, ' + key_index + ', ' +tag_index + ')"'
                + '>' + tagList[tag_index] + '</li>';
        }

        html += '<div class="grid_3 alpha"><h4>Теги:</h4><ul>' + list + '</ul></div>';

        list = '';
        for (var bunch_index in bunchList) {
            bunch_index = parseInt(bunch_index);
            bunch = bunchList[bunch_index];
            var label = bunch['name'] ? bunch['name'] : bunch['code'];
            checked = (relation_cache['bunch'][key_index] != undefined) && ($.inArray(bunch_index, relation_cache['bunch'][key_index]) != -1);
            list += '<li><input type="checkbox" name="key_bunch_' + key_index + '" value="' + bunch_index + '" '
                + (checked ? 'checked="checked"' : '')
                + ' onclick="changeBunchRelationCache(this, ' + key_index + ', ' + bunch_index + ')"'
                + '>' + label + '</li>';
        }

        html += '<div class="grid_3 omega"><h4>Группы:</h4><ul>' + list + '</ul></div>';

        html += '<div class="clearfix"></div>'

        html = '<div class="grid_6 alpha">' + html + '</div>'
    }

    var bunch_html = '';
    for (bunch_index in bunchList) {

        bunch = bunchList[bunch_index];
        label = bunch['name'] ? bunch['name'] : bunch['code'];
        bunch_html += '<h3>' + label + '</h3>';
        list = '';
        for (tag_index in tagList) {
            tag_index = parseInt(tag_index)
            checked = bunch_cache;
            checked = (bunch_cache[bunch_index] != undefined) && ($.inArray(tag_index, bunch_cache[bunch_index]) != -1);
            list += '<li><input type="checkbox" name="bunch_tag_' + bunch_index + '" value="' + tag_index + '"'
            + (checked ? 'checked="checked"' : '')
            + ' onclick="changeBunchTagCache(this,' + bunch_index + ', ' + tag_index + ')"'
            + '>' + tagList[tag_index] + '</li>'
        }

        bunch_html += '<ul>'  + list + '</ul>';
    }
    html += '<div class="grid_6 omega">' + bunch_html + '</div>'


    $('#keytags').html(html);
}

/**
 * Изменяет привязку ключа и банча
 * @param checkbox
 * @param key_index
 * @param bunch_index
 */
function changeBunchRelationCache(checkbox, key_index, bunch_index){
    if (typeof relation_cache['bunch'][key_index] == 'undefined') relation_cache['bunch'][key_index] = [];
    if (checkboxIsChecked(checkbox)) {
        relation_cache['bunch'][key_index].push(bunch_index);
        getKeysForBunch(bunch_index);


        $('input.k_' + key_index).each(function(index, input) {
            if ($.inArray(index, bunch_cache[bunch_index]) > -1) {
                $(input).addClass('b_' + bunch_index).attr('disabled', 'disabled').attr('checked', 'checked');
            }
        });
    } else {
        removeFromArray(bunch_index, relation_cache['bunch'][key_index]);
        $('input.k_' + key_index + '.b_' + bunch_index).removeAttr('disabled').removeAttr('checked').removeClass('b_'+bunch_index);
    }
}

/**
 * Добавить или удалить тег из банча
 * @param checkbox
 * @param bunch_index
 * @param tag_index
 */
function changeBunchTagCache(checkbox, bunch_index, tag_index) {
    if (typeof bunch_cache[bunch_index] == 'undefined') bunch_cache[bunch_index] = [];
    var keyIndexes = getKeysForBunch(bunch_index);
    if (checkboxIsChecked(checkbox)) {
        bunch_cache[bunch_index].push(tag_index);
        $(keyIndexes).each(function(i, keyIndex){
            $('input.t_' + tag_index + '.k_' + keyIndex).addClass('b_' + bunch_index).attr('disabled', 'disabled').attr('checked', 'checked');
        });
    } else {
        removeFromArray(tag_index, bunch_cache[bunch_index]);
        var bunchIndexes = getBunchesForTag(tag_index);
        $(keyIndexes).each(function(i, keyIndex){
            var remove = true;
            var input = $('input.t_' + tag_index + '.k_' + keyIndex);
            for (var i in bunchIndexes){
                if (input.hasClass('b_' + bunchIndexes[i])) {
                    remove = false;
                    break;
                }
            }
            if (remove) {
                input.removeClass('b_' + bunch_index).removeAttr('disabled').removeAttr('checked');
            }
        });
    }
}

/**
 * Возвращает индексы банчей для тега
 * @param tag_index
 * @return {Array}
 */
function getBunchesForTag(tag_index){
    var result = [];
    for (var bunch_index in bunch_cache) {
        if ($.inArray(tag_index, bunch_cache[bunch_index]) > -1) {
            result.push(parseInt(bunch_index));
        }
    }
    return result;
}

function getKeysForBunch(bunchIndex) {
    var result = [];
    for (var key_index in relation_cache['bunch']) {
        if ($.inArray(bunchIndex, relation_cache['bunch'][key_index]) > -1) {
            result.push(key_index);
        }
    }
    return result;
}

function changeRelationCache(checkbox, key_index, tag_index) {
    if (relation_cache['tag'][key_index] == undefined) relation_cache['tag'][key_index] = [];
    if (checkboxIsChecked(checkbox)) {
        relation_cache['tag'][key_index].push(tag_index);
    } else {
        removeFromArray(tag_index, relation_cache['tag'][key_index]);
    }
}

function checkboxIsChecked(checkbox){
    return $(checkbox).attr('checked') != undefined
}

function removeFromArray(val, arr) {
    var index = jQuery.inArray(val, arr);
    if (index != -1) {
        arr.splice(index, 1);
    }
}


function showTab(li) {
    var activeLi = $('#tab_ul > li.active').removeClass('active');
    var active_name = activeLi.data('tab');
    $('#tab_' + active_name).removeClass('active');
    var newTab = $(li).addClass('active').data('tab');
    $('#tab_' + newTab).addClass('active');
    if (newTab == 'relation') {
        updateKeyTags();
    }
}

function showTagValues(tag_index) {
    keys = [];

    var bunchesForTag = getBunchesForTag(tag_index);

    for (key_index in relation_cache['tag']) {
        var tags = relation_cache['tag'][key_index];
        var index = jQuery.inArray(tag_index, tags);
        if (index != -1) {
            keys.push($('#key_' + key_index + '_name').val())
        }
    }

    for (key_index in relation_cache['bunch']) {
        for (var i in relation_cache['bunch'][key_index]) {
            bunchIndex = relation_cache['bunch'][key_index][i];
            if (jQuery.inArray(bunchIndex, bunchesForTag) != -1) {
                keys.push($('#key_' + key_index + '_name').val())
            }
        }
    }

    if (keys.length == 0) {
        alert('Нет привязанных ключей для этого тега.');
    } else {
        var data = {
            tagCode: $('#tag_' + tag_index + '_code').val(),
            keys: keys,
            app: appCode
        };

        $.ajax('/ajax/getTagUniqueValues/',{
            type: 'POST',
            data: data,
            success: function(data){
                if (data.values != undefined){
                    var list = '';
                    for (var i in data.values){
                        var value = data.values[i];
                        list += '<li>' + value + '</li>';
                    }
                    list = '<ul>' + list + '</ul>';
                    $('#tag_distinct_' + tag_index).append(list)
                }
            }
        });
    }

    return false;
}