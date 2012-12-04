function addGroup(name){
    var iField = $('#' + name + 'GroupIterator');
    var iterator = parseInt(iField.val());
    iterator = iterator + 1;

    $('#' + name + 'Table > thead > tr').append('<th>' +
         '<input type="text" name="group_' + name + '_' + iterator + '" value="">' +
         '</th>');

    $('#' + name + 'Table > tbody > tr').each(function(i, row){
            row = $(row);
            $(row).append('<td>' +
                    '<input type="checkbox" name="group_' + name + '_' + row.data('code') + '" value="' + iterator + '">' +
                    '</td>');
    });
    iField.val(iterator);
}