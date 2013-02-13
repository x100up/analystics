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
var minStartDate, maxEndDate, dateMode;
var currentChartData;


var intervalsSeconds = {
    'minute': 60000,
    '10minutes': 600000,
    'hour': 60 * 60000,
    'day': 60 * 60000 * 24,
    'week': 60 * 60000 * 24 * 7
};
/**
 * Запускается при загрузке новых результатов
 */
function onChartResultLoad() {
    chartconf = globalData.chartdata.chartconf;
    chartdata = globalData.chartdata;

    minStartDate = new Date(globalData.minStartDate * 1000);
    maxEndDate = new Date(globalData.maxEndDate * 1000);

    dateMode = false;
    if (minStartDate.getYear() == maxEndDate.getYear()) {
        dateMode = 'year';
        if (minStartDate.getMonth() == maxEndDate.getMonth()) {
            dateMode = 'month';
            if (minStartDate.getDate() == maxEndDate.getDate()) {
                dateMode = 'day';
            }
        }
    }

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

    // по умолчанию рисуем данные пришедшие с сервера
    currentChartData = chartdata['data'];

    switchToSpline();
    ChartManager.constructor(chart);

    for (i in globalData.tagCloudData){
        globalData.tagCloudData[i]['handlers'] = {
            click: ChartManager.onTagClick.bind(ChartManager)
        };
    }
}

/**
 * Показывает серии данных
 * @return {Array}
 */
function prepareDataSeries() {
    var series = [];
    var chartData = getChartData();
    for (var index in chartData)
    {
        var seriesGroupData = chartData[index];
        for (var seriesIndex  in seriesGroupData)
        {
            var xdata = [];
            var seriesData = seriesGroupData[seriesIndex];
            for (var i in seriesData['data']) {
                var row = seriesData['data'][i];
                xdata.push({
                    x: row[0],
                    y: row[1]
            })
            }
            series.push({
                            name: seriesData.name,
                            data: xdata,
                            opt: seriesData.opt,
                            _id: seriesData.id,
                            stack: seriesData.params.op + '_' + index,
                            color: seriesData.params.color,
                            visible: seriesData.params.visible
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

function getChartData() {
    return currentChartData;
}

/**
 * Сбрасывает данные на данные сервера
 */
function resetChartToDefault(){
    currentChartData = chartdata['data'];
    switchToSpline();
}

/**
 * Рисуем данные, которые выбрали в таблице
 */
function createChartWithSelectedData(){
    var selectionMatrix = getSectionInTabel();
    var timestamps = [];
    var chartSeries = [];
    var item;
    for (var rowIndex in selectionMatrix) {
        var row = selectionMatrix[rowIndex];
        if (rowIndex == 0) {
            // заголовки таблица - узнаем, по каким датам будем строить
            for (var columnIndex in row){
                item = $(row[columnIndex]);
                if (item.hasClass('date')) {
                    timestamps.push(parseInt(item.data('timestamp')));
                }
            }
        } else {
            item = $(row[0]);
            // если нет - пошли данные
            chartSeries.push(item.data('chartindex') + '::' +  item.data('seriesindex'));
        }
    }

    // фильтруем данные
    var newData = clone(chartdata['data']);
    for (var index in newData){
        for (var chartIndex in newData[index]){
            var d = newData[index][chartIndex];
            var key = d['seriesIndex'] + '::' + d['taskItemIndex'];
            if ($.inArray(key, chartSeries) == -1){
                delete newData[index][chartIndex];
            } else {
                // фильтруем по дате
                if (timestamps.length){
                    for (var dataIndex in d['data']) {
                        if ($.inArray(d['data'][dataIndex][0], timestamps) == -1) {
                            delete newData[index][chartIndex]['data'][dataIndex];
                        }
                    }
                }
            }
        }
    }

    currentChartData = newData;
    switchToSpline();
}

function clone(obj) {
    // Handle the 3 simple types, and null or undefined
    if (null == obj || "object" != typeof obj) return obj;

    // Handle Date
    if (obj instanceof Date) {
        var copy = new Date();
        copy.setTime(obj.getTime());
        return copy;
    }

    // Handle Array
    if (obj instanceof Array) {
        var copy = [];
        for (var i = 0, len = obj.length; i < len; i++) {
            copy[i] = clone(obj[i]);
        }
        return copy;
    }

    // Handle Object
    if (obj instanceof Object) {
        var copy = {};
        for (var attr in obj) {
            if (obj.hasOwnProperty(attr)) copy[attr] = clone(obj[attr]);
        }
        return copy;
    }

    throw new Error("Unable to copy obj! Its type isn't supported.");
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
            //tickInterval: getTickInterval(),
            pointInterval: getPointInterval(),
            dateTimeLabelFormats: {
                month: '%e %b',
                year: '%b'},
            labels: {
                formatter: function() {
                    return formatDateLabel(this.value, interval);
                }
            }
        };
    }
    if (chart) {
        chart.destroy();
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
 * Генерирует метку времени для тултипа
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

/**
 * Генерирует метку даты по таймштампу основываясь на периоде выборки и интервале
 * @param timestamp
 * @param interval
 * @return {String}
 */
function formatDateLabel(timestamp, interval){

    var date = new Date(timestamp);
    var result = '';
    switch (dateMode) {
        case 'year':
            result = date.getDate() + ' ' + date.getMonth();
            break;

        case 'month':
            result = date.getDate();
            break;

        case 'day':
            result = date.getDate();
            break;

        default :
            result =  date.getDate() + ' ' +  date.getYear() + ' ' + date.getMonth();
    }

    switch (interval){
        case 'minute':
        case '10minutes':
            result += ' ' + date.getHours() + ':' + date.getMinutes();
            break;
        case 'hour':
            result += ' ' + date.getHours() + ':00';
            break;
        case 'day':
            break;
        case 'week':
            break;
    }

    return result;
}

/**
 * Возвращает интервал между лейблами
 * для datetime - это количестов микросекунд
 * @return {Number}
 */
function getPointInterval(){
    switch (interval){
        case 'minute':
            return 60000;
            break;
        case '10minutes':
            return 600000;
            break;
        case 'hour':
            return 60 * 60000;
            break;
        case 'day':
            return 24 * 60 * 60000;
            break;
        case 'week':
            return 7 * 24 * 60 * 60000;
            break;
    }
    return 1;
}


var ChartManager = {

    chart: null,

    constructor: function(chart){
        this.chart = chart
    },

    switchDisplaySeries: function(seriesIds, forceShow, removeOther){
        if (typeof seriesIds == 'number') {
            seriesIds = [seriesIds];
        }
        _series = {};
        for (var i in this.chart.series) {
            var series = this.chart.series[i];
            var seriesId = series.options._id;
            if ($.inArray(seriesId, seriesIds) != -1) {
                var button = $('#switchSeriesButton_' + seriesId);

                if (forceShow || button.hasClass('hidden')) {
                    if (!series.visible){
                        series.show();
                    }

                    button.removeClass('hidden');
                } else {
                    if (series.visible){
                        series.hide();
                    }
                    button.addClass('hidden');
                }
            } else {
                if (removeOther) {
                    series.hide();
                    $('#switchSeriesButton_' + seriesId).addClass('hidden');
                }
            }
        }
    },

    switchVisibleChartGroup:function (button, groupId, append) {
        if (append == undefined) {
            append = false;
        }
        button = $(button);
        var parent = button.parent().parent().parent();

        var seriesIds = [];
        parent.children('tr.series').each(function (i, li) {
            seriesIds.push($(li).data('seriesid'))
        });

        if (button.hasClass('hidden')) {
            button.removeClass('hidden');
            this.switchDisplaySeries(seriesIds, true, append);
        } else {
            button.addClass('hidden');
            this.switchDisplaySeries(seriesIds, false, append);
        }
    },


    onTagClick: function(e){
        var span = $(e.target);
        var tag = span.data('tag').toLowerCase();
        var value = span.data('value');
        $('div#tagcloud span').removeClass('selected');
        span.addClass('selected');
        var seriesId = [];
        $('#series_container .series').each(function(i, element){
            element = $(element);
            if (element.data(tag) && element.data(tag) == value){
                seriesId.push(parseInt(element.data('seriesid')));
            }
        });
        this.switchDisplaySeries(seriesId, true, true);
    }

};




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
function sortResultTable(event, button, field) {
    event.stopPropagation();
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

/**
 * Возвращает сатрицу выделенных элементов
 * @return {Array}
 */
function getSectionInTabel() {
    var columns = $('table.data_table > thead th.selected');
    var rows = $('table.data_table > tbody tr.selected');

    var data = [];
    var rowData = [];

    // выделены только строки
    if (columns.length == 0) {
        data.push($('table.data_table > thead > tr > th.m').toArray());
        rows.each(function(index, row){
            var rowData = [];
            $(row).children().each(function(i, child){
                rowData.push(child);
            });
            data.push(rowData)
        });
    }
    // выделены только столбцы
    else if (rows.length == 0) {
        rowData = [$('#emptyData')[0]];
        columns.each(function(i, th){
            rowData.push(th);
        });
        data.push(rowData);

        $('table.data_table > tbody tr').each(function(index, row){
            row = $(row);
            var rowData = [$(row).children()[0]];
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

/**
 * по факту выделяет выбранные столбцы и строки
 */
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

    $.post('/ajax/downloadCSV', {data: textData}, function(retData){
        $("body").append("<iframe src='/ajax/downloadCSV/?file=" + retData + "' style='display: none;' ></iframe>")
    });
}


var table2loaded = false;
var showingTable = 1;

/**
 * перевернуть таблицу
 */
function switchTable(){
    $('#tableResult' + showingTable).hide();
    if (!table2loaded) {
        $('#tableBox').append('<table class="data_table" id="tableResult2"></table>');
        $('#tableResult2').load('/dashboard/app/' + app + '/result/table/' + globalData['taskId'], function(){
            table2loaded = true;
            showingTable = 2;
        });
    } else {
        if (showingTable == 1){
            $('#tableResult2').show();
            showingTable = 2;
        } else {
            $('#tableResult1').show();
            showingTable = 1;
        }
    }
}

