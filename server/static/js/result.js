var shortMonths = ['янв', 'фев', 'март', 'апр', 'май', 'июнь', 'июль', 'авг', 'сент', 'окт' ,'ноя', 'дек'];

Highcharts.setOptions({
    lang: {
        months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
        shortMonths: shortMonths,
        loading: 'Загрузка',
        weekdays: ['Воскресение', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    },
    legend:{
        enabled: false
    }
});

var chart = null;
var isComapare = false;

var intervalsSeconds = {
    'minute': 60000,
    '10minutes': 600000,
    'hour': 60 * 60000,
    'day': 60 * 60000 * 24,
    'week': 60 * 60000 * 24 * 7
};

function prepareDataSeries() {
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
                            opt: seriesData.opt,
                            _id: seriesData.id,
                            stack: seriesData.params.op + '_' + index
                        })
        }
    }



    return series;
}


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
                            opt: rowSeriesData.opt,
                            stack: rowSeriesData.params.op + '_' + index
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
                'Дата:' + formatDate(this.x, interval, true);

        }
    };
    chartconf['chart'] = {
        renderTo: 'chart_container',
        type: 'spline'
    };
    switchToSpline();
    ChartManager.constructor(chart);
});


/**
 * Рисует график
 * @param chartconf
 */
function renderChart(chartconf) {

    if (isComapare) {
        chartconf['series'] = prepareCompareSeries();
        chartconf['xAxis']['type'] = 'linear';
        chartconf['xAxis']['tickInterval'] = 1;
    } else {
        chartconf['series'] = prepareDataSeries();
        chartconf['xAxis'] = {
            type: 'datetime',
            showEmpty: false,
            dateTimeLabelFormats: {
                month: '%e %b',
                year: '%b'},
            labels: {
                formatter: function() {
                    return formatDate(this.value, interval, false);
                }
            }
        };
    }

    chart = new Highcharts.Chart(chartconf);
}


//------------------------------------------------------------
// Разные виды графиков
//------------------------------------------------------------

/**
 * Переключает режим сравнения серий
 */
function switchToCompare() {
    isComapare = !isComapare;
    if (isComapare) {
        $('#compare_button').addClass('on');
    } else {
        $('#compare_button').removeClass('on');
    }
    renderChart(chartconf);
}

/**
 * Переключает в режим базовых столбцов
 */
function switchToBasicColumn(button){
    switchChartButtons(button);
    switchToColumn(null);
}

/**
 * Переключает в режим базовых столбцов
 */
function switchToStackingColumn(button){
    switchChartButtons(button);
    switchToColumn('normal');
}

/**
 * Переключает в режим базовых столбцов
 */
function switchToPercentColumn(button){
    switchChartButtons(button);
    switchToColumn('percent');
}

function switchToColumn(stacking){
    chartconf['chart']['type'] = "column";
    chartconf['plotOptions'] = {};
    chartconf['plotOptions']['column'] = {
        stacking: stacking,
        dataLabels: {
            enabled: true,
            color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
        }
    };
    renderChart(chartconf);
}


/**
 * Переключает на обычные линейные графики
 */
function switchToSpline(button) {
    switchChartButtons(button);
    chartconf['chart']['type'] = "spline";
    renderChart(chartconf);
}

/**
 *
 */
function switchToArea() {
    alert('coming soon');
}

function switchChartButtons(button){
    if (button) {
        $('span.button.chart.on').removeClass('on');
        $(button).addClass('on');
    }
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
function formatDate(timestamp, interval, extra) {
    var date = new Date(timestamp);
    var result = date.getDate() + ' ' + shortMonths[date.getMonth()] + ' ' + date.getFullYear();
    var minutes = date.getMinutes();
    var hours = date.getHours();
    if (minutes < 10) minutes = '0' + minutes;
    if (hours < 10) hours = '0' + hours;
    switch (interval) {
        case '10minutes':
            if (!extra) {
                result = '';
            }
            result += ' ' + hours + ':' + minutes + (extra ? ' +10 мин' : '');
        break;

        case 'week':
            result += ' - ' + formatDate(timestamp + (60 * 60 * 24 * 7 * 1000) , 'day');
        break;

        case 'day':
            // result =  date.getDate() + ' ' + shortMonths[date.getMonth()] + ' ' + date.getFullYear();
        break;

        case 'hour':
            result += ' ' + hours +  (extra ? ' +1 час' : '');
        break;

        case 'minute':
            if (!extra) {
                result = '';
            }
            result += ' ' + hours + ':' + minutes;
        break;
    }
    return result;
}


var ChartManager = {

    chart: null,

    constructor: function(chart){
        this.chart = chart
    },

    switchDisplaySeries: function(checkbox, seriesId){
        for (var i in this.chart.series) {
            var series = this.chart.series[i];
            if (series.options._id == seriesId){
                if (checkboxIsChecked(checkbox)) {
                    series.show();
                } else {
                    series.hide();
                }
            }
        }
    }

};


function checkboxIsChecked(checkbox){
    return $(checkbox).attr('checked') != undefined
}



