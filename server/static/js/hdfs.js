/**
 * @var currentPath
 */

var hive = {
    'db': null,
    'table': null,
    'partition': null,
}

$(function(){
    loadPath(currentPath);
});



function loadPath(path){

    currentPath = path;
    createLoadingDiv($('#pathTable'));
    $.ajax('/hdfs/ajax/getPath', {
        type:'POST',
        data: {path: path},
        success: function(data){
            $('#fileList').html(data.body);
            $('#navigator').html(data.navigator);
            var requestHiveStat = false;

            $(['db', 'table', 'partition']).each(function(i, name){
                var label = $('#hive_' + name + ' > span.label');
                if (data.hive[name]) {
                    if (name == 'partition') {
                        label.html(data.hive[name].join('.'));
                    } else {
                        label.html(data.hive[name]);
                    }

                    hive[name] = data.hive[name];
                    requestHiveStat = true;
                } else {
                    label.html('-');
                }
            });

            if (requestHiveStat){
                getHiveStat();
            }

            removeLoadingDiv();
            loadPathStat(path);
        }
    })
}

function createLoadingDiv(el) {
    el = $(el);
    var  position = el.position();
    var loader = $('#loadingDiv');
    loader.height(el.height()).width(el.width()).css('display', 'block')
        .css('left', position.left + parseInt(el.css('margin-left'))).css('top', position.top + parseInt(el.css('margin-top')));

}

function removeLoadingDiv() {
    $('#loadingDiv').css('display', 'none');
}

function loadPathStat(path){
    var summary = $('#folderSummary');
    summary.html('');
    createLoadingDiv(summary);
    currentPath = path;
    $.ajax('/hdfs/ajax/getPathStat', {
        type:'POST',
        data: {path: path},
        success: function(data){
            summary.html(data.html);
            removeLoadingDiv();
        }
    })
}


function getHiveStat(){
    $.ajax('/hdfs/ajax/getHiveStat', {
        type:'POST',
        data: hive,
        success: function(data){
            $(['db', 'table', 'partition']).each(function(i, name){
                if (typeof data[name] != 'undefined'){
                    $('#hive_' + name).removeClass('exist').removeClass('not_exist')
                        .addClass(data[name]['exists'] ? 'exist' : 'not_exist');
                }
            });
        }
    })
}

function dropTable() {
    runHiveAction('dropTable', hive['table']);
}

function createTable() {
    runHiveAction('createTable', hive['table']);
}

function dropDatabase() {
    runHiveAction('dropDatabase', hive['db']);
}

function createDatabase() {
    runHiveAction('createDatabase', hive['db']);
}

function dropPartition() {
    runHiveAction('dropPartition', hive['partition']);
}

function createPartition() {
    runHiveAction('createPartition', hive['partition']);
}

function runHiveAction(action, data) {
    $.ajax('/hdfs/ajax/runHiveAction', {
        type:'POST',
        data: {'action':action, 'data':data},
        success: function(data){
            getHiveStat();
        }
    })
}



