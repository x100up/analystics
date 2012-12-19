function addEventGroup(){
    var iterator = $('#eventGroupIterator');
    var maxIndex = parseInt(iterator.val());
    maxIndex++;
    $('#eventGroupIterator').val(maxIndex);

    $('#all_event_groups').append('<div class="row-fluid" class="event-group-container" data-event-group-index="'+maxIndex+'">'+
        '<div class="oneEventGroup span2">'+
            '<input type="text" name="group_event_'+maxIndex+'" value="">'+
        '</div>'+
        '<div class="span10" id="group-tags-container-'+maxIndex+'">'+
            '<div class="label label-warning" onclick="editEventList(event, '+maxIndex+')"><i class="icon-plus-sign"></i></div>'+
        '</div>'+
    '</div>');
}

var commandBuffer, editableGroupIndex;

 function editEventList(event, groupIndex){
        commandBuffer = {add:{}, remove:{}};
        editableGroupIndex = groupIndex;
        $('.modal-checkboxes').removeAttr('checked');
        $('.event-label-' + groupIndex).each(function(index, item){
            var eventCode = $(item).data('event-code');
            $('#modal-event-' + eventCode).attr('checked', 'checked');
        });

        $('#eventListModal').modal({});
}


function checkEvent(checkbox, eventCode){
    if (checkboxIsChecked(checkbox)) {
        // добавляем
        if (commandBuffer.remove[eventCode]) {
            delete commandBuffer.remove[eventCode];
        } else {
            commandBuffer.add[eventCode] = true;
        }
    } else {
        if (commandBuffer.add[eventCode]) {
            delete commandBuffer.add[eventCode];
        } else {
            commandBuffer.remove[eventCode] = true;
        }
    }
}

function saveGroupEvents(){
    var name;
    for (var eventCode in commandBuffer.add) {
        name = $('#modal-event-' + eventCode).parent().text().trim();

        $('#group-tags-container-' + editableGroupIndex).prepend('<div class="label event-code-'+eventCode+' label-info event-label-' + editableGroupIndex + '"' +
            'data-event-code="' + eventCode + '">'+ name +'</div> '+
            '<input type="hidden" name="group_event_' + eventCode + '" value="' + editableGroupIndex + '"'+
                'id="input_' + editableGroupIndex + '_' + eventCode + '">'
        );
    }
    for (eventCode in commandBuffer.remove) {
        $('#group-tags-container-' + editableGroupIndex).find('.event-code-' + eventCode).remove();
        $('#input_' + editableGroupIndex + '_' + eventCode).remove()
    }

    $('#eventListModal').modal('hide')
}


function checkboxIsChecked(checkbox){
    return $(checkbox).attr('checked') != undefined
}