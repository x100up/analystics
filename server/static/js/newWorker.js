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
    $('div#key_1_tag_container').load('/ajax/key_configuration', {'key':keyName, 'app':appName})
}
