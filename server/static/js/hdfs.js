/**
 * @var currentPath
 */

$(function(){
    loadPath(currentPath);
});



function loadPath(path){
    loadPathStat(path);
    currentPath = path;
    $.ajax('/hdfs/ajax/getPath', {
        type:'POST',
        data: {path: path},
        success: function(data){
            $('#fileList').html(data.body);
            $('#navigator').html(data.navigator);
        }
    })
}

function loadPathStat(path){
    currentPath = path;
    $.ajax('/hdfs/ajax/getPathStat', {
        type:'POST',
        data: {path: path},
        success: function(data){
            $('#folderSummary').html(data.html);
        }
    })
}

