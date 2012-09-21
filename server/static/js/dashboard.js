function switchAll(cb){
    if (cb.checked)
        $('input.jobcb').attr('checked', 'checked')
    else
        $('input.jobcb').removeAttr('checked')
}

var alive_progress_data = {};
$(function(){
    alive_progress_spans = $('span.alive_progress');
    if (alive_progress_spans.length) {
        alive_progress_spans.each(function(index, span){
            span = $(span)
            alive_progress_data[span.data('workerid')] = span.data('appid');
        });
        getProgress();
        setInterval('getProgress()', 2000);
    }
});



function getProgress() {
    if (Object.keys(alive_progress_data).length){
        $.ajax('/ajax/getTasksProgress', {
            data: alive_progress_data,
            type: 'POST',
            success: function(data, textStatus, jqXHR){
                if (typeof data['appIdResult'] == 'object') {
                    var appId, workerId, processIndicator;
                    for (i in data['appIdResult']) {
                        var appIdResult = data['appIdResult'][i];
                        workerId = appIdResult[0];
                        appId = appIdResult[1];
                        $('#progress_' + workerId).data('appid', appId);
                        alive_progress_data[workerId] = appId;
                    }

                    for (i in data['progressResult']) {
                        var progressResult = data['progressResult'][i];

                        var progress = progressResult[1];
                        appId = progressResult[0];

                        workerId = false;
                        for (var key in alive_progress_data){
                            if (alive_progress_data[key] == appId) {
                                workerId = key;
                                break;
                            }
                        }

                        if (parseInt(progress) == 100) {
                            delete alive_progress_data[workerId];
                            processIndicator = $('#loader_' + workerId);
                            processIndicator.parent().addClass('SUCCESS').parent().addClass('success_recently');
                            $('#progress_' + workerId).remove();
                            processIndicator.remove();
                        } else {
                            $('#progress_' + workerId).html(progress + '%');
                        }
                    }

                    for (i in data['diedWorkers']) {
                        workerId = data['diedWorkers'][i];
                        delete alive_progress_data[workerId];
                        processIndicator = $('#loader_'+workerId);
                        processIndicator.parent().addClass('ERROR');
                        $('#progress_' + workerId).remove();
                        processIndicator.remove();
                    }
                }
            }
        });
    }
}