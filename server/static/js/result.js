$(function(){
    var xdata = new Array()
    var data = chartdata['data']
    if (data === undefined){

        return;
    }

    for (i in chartdata['data']) {
        var row = data[i]
        var date = Date.UTC(parseInt(row[3]), parseInt(row[2]) - 1, parseInt(row[4]), parseInt(row[1]), parseInt(row[5]))
        xdata.push([date, parseInt(row[0])])
    }

    var chartconf = {
        chart: {
            renderTo: 'chart_container',
            type: 'spline'
        },

        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            }
        },
        yAxis: {
            min: 1,
            minTickInterval: 1
        },
        tooltip: {
            formatter: function() {
                return '<b>'+ this.series.name +'</b><br/>'+
                    Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y +' m';
            }
        },
        series: [{
            name: 'KEY',
            data: xdata
        }]
    }

    $.extend(true, chartconf, chartdata['chartconf'])


    chart1 = new Highcharts.Chart(chartconf);
});