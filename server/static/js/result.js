$(function(){

    var data = chartdata['data']
    if (data === undefined) {
        return;
    }
    // разбираем данные серий

    var series = new Array()

    var multy = Object.size(chartdata['data']) > 1

    for (var index in chartdata['data'])
    {

        var seriaGroupData = chartdata['data'][index];
        for (var seriaIndex  in seriaGroupData)
        {
            var xdata = new Array();
            var seriaData = seriaGroupData[seriaIndex];

            for (var i in seriaData['data']) {
                var row = seriaData['data'][i];

                if (multy){
                    xdata.push([parseInt(row[0]), parseInt(row[1])])
                } else {
                    var date = new Date();
                    var ts = Date.parse(row[0] + ' GMT');
                    date.setTime(ts);
                    xdata.push([ts, parseFloat(row[1])])
                }
            }
            series.push({
                name: seriaData.name,
                data: xdata,
                options:{
                    tagValues: seriaData.tagValues
                }
            })
        }
    }

    if (multy) {
        xAxis = {
            allowDecimals: false,
            labels: {
                formatter: function() {
                    return this.value;
                }
            }}
    } else {
        xAxis = {
            type: 'datetime',
            showEmpty: false,
                dateTimeLabelFormats: {
                month: '%e. %b',
                year: '%b'
        }}
    }

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
                console.log(this.series);
                return '<b>'+ this.series.name +'</b><br/>'+
                    + this.series.options.tagValues +
                    Highcharts.dateFormat('%e. %b', this.x) +'<br /> Значение:'+ this.y +' ';
            }
        },
        series: series
    }

    $.extend(true, chartconf, chartdata['chartconf'])


    drawColumnChart(chartconf)
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

