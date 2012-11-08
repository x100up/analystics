/**
 * @var currentPath
 */

$(function(){
    loadPath(currentPath);
});



function loadPath(path){
    console.log(path);
    $.ajax('/hdfs/ajax/getPath', {
        type:'POST',
        data: {path: path},
        success: function(data){
            $('#fileList').html(data.body);
            $('#navigator').html(data.navigator);
        }
    })
}
