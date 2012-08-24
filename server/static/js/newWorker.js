var appName = 'topface';
var months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
var dayNamesMin = [ 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

$(function(){
    var ka = $('input.key_autocomplete').autocomplete({ serviceUrl:'/ajax/key_autocomplete?app=' + appName , onSelect: onSelectKey});

    $.datepicker.setDefaults( {'monthNames':months, 'dayNamesMin':dayNamesMin, 'firstDay':1, 'maxDate': Date.now()} );

    console.log($.datepicker.regional[ "ru" ])
    $( "input.datepicker" ).datetimepicker({timeFormat: 'hh:mm'});
});

function onSelectKey(keyName) {
    // загружаем конфигурацию
    $.getJSON('/ajax/key_configuration', {'key':keyName, 'app':appName}, function(data){
        $('ul#tag_container_1').children().remove();
        if (data.mustHaveTags){
            for (i in data.mustHaveTags) {
                grawTag(i, data.mustHaveTags[i], true)
            }
        }

        if (data.canHaveTags){
            for (i in data.canHaveTags) {
                grawTag(i, data.canHaveTags[i], false)
            }
        }
    })
}


function grawTag(name, conf, mustHave){

    $('ul#tag_container_1').append('<li><label class="' + (mustHave ? 'must' : 'can') + '" title="' + conf.description + '">' + name + '</label>' +
        '<input type="text" name="key_tag[]" value="' + name + '">' +
        '</li>')
}

