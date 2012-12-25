
$(function () {
    clusterState = $('#clusterState');
    window.setTimeout(collectData, 1000);
    initChart();
});

function collectData() {
    clusterState.load('/ajax/admin/getClusterState', {success:function(){
        window.setTimeout(collectData, 1000);
    }});
}

function addPoint(currentTs, totalUsed){
    var series = clusterChart.series[0];
    var shift = series.data.length > 50;
    series.addPoint([ currentTs , totalUsed], true, shift);
}

function initChart() {
    Highcharts.setOptions({
                              global:{
                                  useUTC:false
                              }
                          });

    clusterChart = new Highcharts.Chart({
                                     chart:{
                                         renderTo:'chart',
                                         type:'spline',
                                         marginRight:10,
                                         events:{
                                             load:function () {}
                                         }
                                     },
                                     title:{
                                         text:'Нагрузка на кластер'
                                     },
                                     xAxis:{
                                         type:'datetime',
                                         tickPixelInterval:150
                                     },
                                     yAxis:{
                                         title:{
                                             text:'Value'
                                         },
                                         plotLines:[
                                             {
                                                 value:0,
                                                 width:1,
                                                 color:'#808080'
                                             }
                                         ],
                                         min: 0
                                     },
                                     tooltip:{
                                         formatter:function () {
                                             return '<b>' + this.series.name + '</b><br/>' +
                                                 Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                                                 Highcharts.numberFormat(this.y, 2);
                                         }
                                     },
                                     legend:{
                                         enabled:false
                                     },
                                     exporting:{
                                         enabled:false
                                     },
                                     series:[
                                         {
                                             name:'Random data',
                                             data:(function () {
                                                 // generate an array of random data
                                                 var data = [],
                                                     time = (new Date()).getTime(),
                                                     i;

                                                 data.push({x:time, y:0});
                                                 return [];
                                             })()
                                         }
                                     ]
                                 });
}