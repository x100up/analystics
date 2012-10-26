var shortMonths = ['янв', 'фев', 'март', 'апр', 'май', 'июнь', 'июль', 'авг', 'сент', 'окт' ,'ноя', 'дек'];

Highcharts.setOptions({
    lang: {
        months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
        shortMonths: shortMonths,
        loading: 'Загрузка',
        weekdays: ['Воскресение', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    }
});

var chart = null;
var isComapare = false;

function prepareDateSeries() {
    var series = [];
    for (var index in chartdata['data'])
    {
        var seriesGroupData = chartdata['data'][index];
        for (var seriesIndex  in seriesGroupData)
        {
            var xdata = [];
            var seriesData = seriesGroupData[seriesIndex];

            for (var i in seriesData['data']) {
                var row = seriesData['data'][i];
                xdata.push([row[0], row[1]])
            }
            series.push({
                            name: seriesData.name,
                            data: xdata,
                            opt: seriesData.opt
                        })
        }
    }
    return series;
}

var intervalsSeconds = {
    'minute': 60000,
    '10minutes': 600000,
    'hour': 60 * 60000,
    'day': 60 * 60000 * 24,
    'week': 60 * 60000 * 24 * 7
};

/**
 * Подготавливает данные для сравнения серий
 * @return {Array}
 */
function prepareCompareSeries() {

    var series = [];
    var delta = intervalsSeconds[interval];

    for (var index in chartdata['data'])
    {
        var seriesGroupData = chartdata['data'][index];
        var minValue = false;
        for (var seriesIndex in seriesGroupData)
        {
            var _v = seriesGroupData[seriesIndex]['data'][0][0];
            if (minValue === false || minValue > _v) {
                minValue = _v;
            }
        }

        for (seriesIndex in seriesGroupData)
        {
            var seriesData = [];
            var rowSeriesData = seriesGroupData[seriesIndex];

            var first = false;
            for (var i in rowSeriesData['data']) {
                var row = rowSeriesData['data'][i];
                var ts = (row[0] - minValue) / delta;
                seriesData.push([ts, row[1]]);
            }

            series.push({
                            name: rowSeriesData.name,
                            data: seriesData,
                            opt: rowSeriesData.opt
                        })
        }
    }
    return series;
}

$(function(){
    chartconf = chartdata['chartconf'];

    chartconf['tooltip'] = {
        formatter: function() {
            return '<b>'+ this.series.name + '</b><br/>' +
                'Значение:' + this.y + '<br/>' +
                'Дата:' + formatDate(this.x, this.series.options.opt.interval);

        }
    };
    drawChart();
});

/**
 * Рисует график
 */
function drawChart() {

    if (isComapare) {
        chartconf['chart']['type'] = "spline";
        chartconf['xAxis']['type'] = 'linear';
        chartconf['xAxis']['tickInterval'] = 1;
        chartconf['series'] = prepareCompareSeries();

    } else {
        chartconf['chart'] = {
                renderTo: 'chart_container',
                type: 'spline'
        };
        chartconf['series'] = prepareDateSeries();

        chartconf['xAxis'] = {
            type: 'datetime',
            showEmpty: false,
            dateTimeLabelFormats: {
                month: '%e %b',
                year: '%b'}
        };
    }

    chart = new Highcharts.Chart(chartconf);
}


/**
 * Переключает режим сравнения серий
 */
function switchCompare() {
    isComapare = !isComapare;
    if (isComapare) {
        $('#compare_button').addClass('on');
    } else {
        $('#compare_button').removeClass('on');
    }
    drawChart();
}

function drawColumnChart(chartconf) {
    chartconf['chart']['type'] = "column";
    chartconf['plotOptions'] = {
        column: {
            stacking: 'normal',
                dataLabels: {
                enabled: true,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
            }
        }
    };
    chart = new Highcharts.Chart(chartconf);
}

function drawAreaChart(chartconf){
    chartconf['chart']['type'] = "area";

    chartconf['plotOptions'] = {
        area: {
            stacking: 'normal',
                lineColor: '#666666',
                lineWidth: 2,
                marker: {
                    lineWidth: 1,
                    lineColor: '#666666'
                }
        }
    };

    chartconf['credits'] = {
        enabled: false
    };

    chart = new Highcharts.Chart(chartconf);
}





Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

/**
 *
 * @param timestamp
 * @param interval
 * @return {String}
 */
function formatDate(timestamp, interval) {
    var date = new Date(timestamp);
    var result =  date.getDate() + ' ' + shortMonths[date.getMonth()] + ' ' + date.getFullYear();
    switch (interval) {
        case '10minutes':
            result += ' ' + date.getHours() + ':' + date.getMinutes() + '+10 мин';
        break;

        case 'week':
            result += ' - ' + formatDate(timestamp + (60 * 60 * 24 * 7 * 1000) , 'day');
        break;

        case 'day':
            // result =  date.getDate() + ' ' + shortMonths[date.getMonth()] + ' ' + date.getFullYear();
        break;

        case 'hour':
            result += ' ' + date.getHours() + ' +1час';
        break;

        case 'minute':
            result += ' ' + date.getHours() + ':' +date.getMinutes();
        break;
    }
    return result;
}

