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
                        //processIndicator
                        $('#worker_row_' + workerId).removeClass('job_ALIVE').addClass('job_' + state);
                    }
                }
            }
        });
    }
}

var currentWorkerId = null;

function editName(button, workerId) {
    currentWorkerId = workerId;
    $(button).parent().hide();
    $('#taskName').show().focus();

    return '';
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

}

function keyDownHandlerTaskName(event){
    if (event.keyCode == 13) {
        event.stopPropagation();
        saveTaskName();
    }
}

function saveTaskName() {
    var editor = $('#taskName');
    var name = editor.val();
    editor.hide();
    $('#taskNameLabel').html(name).parent().show();
    if (currentWorkerId != undefined) {
        $.ajax('/ajax/saveWorkerName', {
            type: 'POST',
            data: {'name':name, 'workerId':currentWorkerId},
            success: function(data, textStatus, jqXHR){

            }
        });
    }
}

function loadResult(workerId) {
    loadDashboardContent('result?jobId=' + workerId);
    $('div.job').removeClass('selected');
    $('#worker_row_' + workerId).addClass('selected');
}

function startNewTask(x){
    var l = 'new';
    if (x != undefined){
        l += '?baseOn=' + x;
    }
    loadDashboardContent(l);
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
            if (data.redirect != undefined){
                loadDashboardContent(data.redirect);
                return;
            }
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
    alive_progress_spans = $('div.job_ALIVE');
    if (alive_progress_spans.length) {
        alive_progress_spans.each(function(index, obj){
            obj = $(obj);
            aliveWorkerIds[obj.data('workerid')] = 1;
        });
        getProgress();
        setInterval('getProgress()', 2000);
    }

    contentContainer = $('#dashboard_container');
    loadDashboardContent(location.hash.substr(1));

});



