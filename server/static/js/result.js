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


$(function(){

    var data = chartdata['data']
    if (data === undefined) {
        return;
    }
    // разбираем данные серий

    var series = [];

    var multy = Object.size(chartdata['data']) > 1;

    for (var index in chartdata['data'])
    {

        var seriesGroupData = chartdata['data'][index];
        for (var seriesIndex  in seriesGroupData)
        {
            var xdata = [];
            var seriesData = seriesGroupData[seriesIndex];

            for (var i in seriesData['data']) {
                var row = seriesData['data'][i];
                xdata.push([i, row])
            }
            series.push({
                name: seriesData.name,
                data: xdata,
                opt: seriesData.opt
            })
        }
    }


        xAxis = {
            type: 'datetime',
            showEmpty: false,
                dateTimeLabelFormats: {
                month: '%e %b',
                year: '%b'
        }};


    var chartconf = {
        chart: {
            renderTo: 'chart_container',
            type: 'spline'
        },

        xAxis: xAxis,
        yAxis: {
            min: 0,
            minTickInterval: 1
        },
        tooltip: {
            formatter: function() {
                return '<b>'+ this.series.name + '</b><br/>' +
                    'Значение:' + this.y + '<br/>' +
                    'Дата:' + formatDate(this.x, this.series.options.opt.interval);

            }
        },

        series: series
    };

    $.extend(true, chartconf, chartdata['chartconf'])


    drawSplineChart(chartconf)
});

function drawSplineChart(chartconf) {
    chartconf['chart']['type'] = "spline";
    chart = new Highcharts.Chart(chartconf);
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

