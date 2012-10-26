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

function updateKey(index) {
    $('#key_' + index + '_h').text($('#key_' + index + '_name').val());
}

function deleteKey(index) {
    $('#key_' + index).remove();
    if (relation_cache[index] != undefined) {
        delete relation_cache[index];
    }
}

function updateKeyTags(button) {
    var keyList = {};
    $('input[name="key_index"]').each(function(index, tag){
        var index = $(tag).val();
        keyList[index] = $('#key_' + index + '_name').val();
    });

    var tagList = {};
    $('input[name="tag_index"]').each(function(index, tag){
        var index = $(tag).val();
        tagList[index] = $('#tag_' + index + '_code').val();
    });

    var html = '';
    for (var key_index in keyList) {
        var key_code = keyList[key_index];
        html += '<h3>' + key_code + '</h3>';

        var list = '';
        for (var tag_index in tagList) {
            var checked = (relation_cache[key_index] != undefined) && ($.inArray(tag_index, relation_cache[key_index]) != -1);
            list += '<li><input type="checkbox" name="have_key_tag_' + key_index + '" value="' + tag_index + '" '
                + (checked ? 'checked="checked"' : '')
                + ' onclick="changeRelationCache(this, ' + key_index + ', \'' +tag_index + '\')"'
                + '>' + tagList[tag_index] + '</li>';
        }

        html += '<ul>' + list + '</ul>';
    }

    $('#keytags').html(html);
}

function changeRelationCache(checkbox, key_index, tag_index) {
    if ($(checkbox).attr('checked') != undefined) {
        if (relation_cache[key_index] == undefined) {
            relation_cache[key_index] = [];
        }
        relation_cache[key_index].push(tag_index);
    } else {
        var op_index = jQuery.inArray(tag_index, relation_cache[key_index]);
        if (op_index != -1) {
            relation_cache[key_index].splice(op_index, 1);
        }
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