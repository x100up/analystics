function switchAll(cb){
    if (cb.checked)
        $('input.jobcb').attr('checked', 'checked')
    else
        $('input.jobcb').removeAttr('checked')
}

var aliveWorkerIds = {};
$(function(){
    alive_progress_spans = $('span.alive_progress');
    if (alive_progress_spans.length) {
        alive_progress_spans.each(function(index, span){
            span = $(span)
            aliveWorkerIds[span.data('workerid')] = span.data('stage_count');
        });
        getProgress();
        setInterval('getProgress()', 2000);
    }
    console.log(aliveWorkerIds);
});

function getProgress() {
    if (Object.keys(aliveWorkerIds).length){
        $.ajax('/ajax/getTasksProgress', {
            data: aliveWorkerIds,
            type: 'POST',
            success: function(data, textStatus, jqXHR){

                var workerStates = data['workerStates'];
                for (i in workerStates) {
                    var workerId = workerStates[i][0];
                    var state = workerStates[i][1];

                    if (state != 'ALIVE') {
                        delete aliveWorkerIds[workerId];
                        processIndicator = $('#loader_' + workerId);
                        processIndicator.parent().removeClass('ALIVE').addClass(state);
                        $('#progress_' + workerId).remove();
                        processIndicator.remove();
                    }
                }
            }
        });
    }
}