function onChangeType(select, tag) {
   if ($(select).val() == 'choose') {
        $('#choose_' + tag).show()
   } else {
       $('#choose_' + tag).hide()
   }
}

function setNew(tag){
    $('#choose_' + tag + ' tr.new input').attr('onkeypress', '');
    $('#choose_' + tag + ' tr.new').removeClass('new');
    var values_count = $('#' + tag + '_values_count')
    values_count.val( parseInt(values_count.val()) + 1)
    addNew(tag)
}

function addNew(tag){
    $('#choose_' + tag + ' tbody').append('<tr class="new">'+
                                              '<td><input type="text" onkeypress="setNew(\'' + tag + '\')"></td>'+
                                              '<td><input type="text" onkeypress="setNew(\'' + tag + '\')"></td>'+
                                              '</tr>');
}