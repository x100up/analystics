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
var chartconf, chartdata, interval;


var intervalsSeconds = {
    'minute': 60000,
    '10minutes': 600000,
    'hour': 60 * 60000,
    'day': 60 * 60000 * 24,
    'week': 60 * 60000 * 24 * 7
};

function onChartResultLoad() {
    chartconf = globalData.chartdata.chartconf;
    chartdata = globalData.chartdata;
    interval = globalData.interval;
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

    $("#tagcloud").jQCloud(globalData.tagCloudData);
}

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


/*---------------------------------------------------
                TABLE MECHANISM
 --------------------------------------------------*/
function selectRow(td){
    var tr = $($(td).parent());
    if (tr.hasClass('selected')) {
        tr.removeClass('selected');
    } else {
        tr.addClass('selected');
    }
}

function selectColumn(th ,columnIndex) {
    th = $(th);
    if (!th.hasClass('selected')) {
        $('td.col_' + columnIndex).addClass('cSelected');
        th.addClass('selected')
    } else {
        th.removeClass('selected')
        $('td.col_' + columnIndex).removeClass('cSelected');
    }

}

/*---------------------------------------------------
            SORT TABLE MECHANISM
 --------------------------------------------------*/

/**
 *
 * @param field
 */
function sortResultTable(button, field) {
    button = $(button);
    var turn = button.data('sorted');
    if (turn == 'ask') {
        turn = 'desc';
        button.removeClass('up').addClass('down');
    } else {
        turn = 'ask';
        button.removeClass('down').addClass('up');
    }
    button.data('sorted', turn);


    var rows = $('table.data_table > tbody > tr');
    var values = [];
    var rowDict = {};
    rows.each(function(index, row){
        row = $(row);
        var val = parseFloat($(row).data(field));
        values.push(val);
        if (typeof rowDict[val] == 'undefined') {
            rowDict[val] = []
        }
        rowDict[val].push(row);
    });
    var body = $('table.data_table > tbody');
    rows.detach();
    if (turn == 'ask') {
        values = values.sort(function(a,b){return a > b});
    } else {
        values = values.sort(function(a,b){return a < b});
    }
    for (var i in values) {
        val = values[i];
        body.append(rowDict[val].pop());
    }
}

function getSectionInTabel() {
    var columns = $('table.data_table > thead th.selected');
    var rows = $('table.data_table > tbody tr.selected');

    var data = [];
    var rowData = [];

    // выделены только строки
    if (columns.length == 0) {
        rows.each(function(index, row){
            var rowData = [];
            $(row).children().each(function(i, child){
                rowData.push(child);
            });
            data.push(rowData)
        });
    }

    else if (rows.length == 0) {
        rowData = [$('#emptyData')[0]];
        columns.each(function(i, th){
            rowData.push(th);
        });
        data.push(rowData);

        $('table.data_table > tbody tr').each(function(index, row){
            var rowData = [];
            $(row).children('.cSelected').each(function(i, child){
                rowData.push(child);
            });
            data.push(rowData)
        });
    } else {
        rowData = [$('#emptyData')[0]];
        columns.each(function(i, th){
            rowData.push(th);
        });
        data.push(rowData);

        rows.each(function(index, row){
            row = $(row);
            var rowData = [
                row.children('th')[0]
            ];
            $(row).children('.cSelected').each(function(i, child){
                rowData.push(child);
            });
            data.push(rowData)
        });
    }

    return data;
}

function copyToBuffer() {
    var data = getSectionInTabel();

    window.getSelection().removeAllRanges();

    for (var rowIndex in data) {
        for (var columnIndex in data[rowIndex]) {
            var el = data[rowIndex][columnIndex];
            var rangeObj = document.createRange();
            rangeObj.selectNodeContents(el);
            window.getSelection().addRange(rangeObj);
        }
    }

}

function exportToExcel(){
    var data = getSectionInTabel();
    var textData = [];
    for (var rowIndex in data) {
        var rowData = [];
        for (var columnIndex in data[rowIndex]) {
            var el = $(data[rowIndex][columnIndex]);
            rowData.push(el.text().trim());
        }
        textData.push(rowData);
    }

    $.post('/ajax/downloadCSV', {'data': textData}, function(retData){
        $("body").append("<iframe src='/ajax/downloadCSV/?file=" + retData + "' style='display: none;' ></iframe>")
    });
}
