var globalData = {};
var contentContainer ;



function switchAll(cb){
    if (cb.checked)
        $('input.jobcb').attr('checked', 'checked')
    else
        $('input.jobcb').removeAttr('checked')
}

var aliveWorkerIds = {};


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

function editName(workerId) {
    var a = $('#link_' + workerId);
    var editor = $('<input/>').val(a.text()).width(a.width());
    a.after(editor).remove();
    editor.focus();

    var callback = function () {
        if (!editor.val().trim()) {
            editor.after(a).remove();
            return;
        }
        editor.attr('disabled', 'disabled');
        $.ajax('/ajax/saveWorkerName', {
            type: 'POST',
            data: {'name':editor.val(), 'workerId':workerId},
            success: function(data, textStatus, jqXHR){
                editor.after(a.text(editor.val())).remove()
            }
        });
    };

    editor.blur(callback);
    editor.keydown(function(event){
        if (event.keyCode == 13) {
            event.stopPropagation();
            callback();
        }
    })
}

function loadResult(workerId) {
    loadDashboardContent('result?jobId=' + workerId);
    $('tr.job').removeClass('selected');
    $('#worker_row_' + workerId).addClass('selected');
}

function startNewTask(){
    loadDashboardContent('new');
}

function loadDashboardContent(page) {
    var callback = null;
    if (typeof page == "undefined") {
        page = 'first'
    } else {
        location.hash = page;
        if (page.indexOf('result?') == 0){
            callback = onChartResultLoad
        }

        if (page.indexOf('new') == 0){
            callback = initNewTask;
        }
    }


    $.ajax('/dashboard/app/' + app + '/' + page,{
        success: function(data){
            contentContainer.html(data.html);
            if (typeof data.vars != 'undefined'){
                for (var key in data.vars){
                    globalData[key] = data.vars[key];
                }
            }

            if (callback) {
                callback();
            }
        }
    });
}


$(function(){
    alive_progress_spans = $('span.alive_progress');
    if (alive_progress_spans.length) {
        alive_progress_spans.each(function(index, span){
            span = $(span);
            aliveWorkerIds[span.data('workerid')] = span.data('stage_count');
        });
        getProgress();
        setInterval('getProgress()', 2000);
    }

    contentContainer = $('#dashboard_container');
    loadDashboardContent(location.hash.substr(1));

});



