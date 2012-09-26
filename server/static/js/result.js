var shortMonths = ['янв', 'фев', 'март', 'апр', 'май', 'июнь', 'июль', 'авг', 'сент', 'окт'];

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

                //if (multy){
                //    xdata.push([parseInt(row[0]), parseInt(row[1])])
                //} else {
                    xdata.push([row[0], parseFloat(row[1])])
                //}
            }
            series.push({
                name: seriesData.name,
                data: xdata,
                tagValues: seriesData.tagValues
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
                    'Дата:' + formatDate(this.x);

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

function formatDate(timestamp) {
    console.log(timestamp);
    var date = new Date(timestamp);
    return date.getDate() + ' ' + shortMonths[date.getMonth()] + ' ' + date.getFullYear() + ' ' + date.getHours() + ':' +
        date.getMinutes();
}

