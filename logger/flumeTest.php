<?
include_once dirname(__FILE__) . '/TFLogger/TFLogger.php';
//include_once dirname(__FILE__) . '/TFLogger/TFAnalyticsKeys.php';

$flumeLogger = new TFLogger('topface_analytics.json');
$flumeLogger->log('KEY_1', array('slice_1' => 100500, 'slice_2' => 'fb'));
$flumeLogger->log('KEY_1', array('slice_1' => 100500, 'slice_2' => 'fb', 'slice_3' => 100,505));
$flumeLogger->log('KEY_2', array('slice_3' => null));
$flumeLogger->log('KEY_2', array('slice_3' => true));
$flumeLogger->log('KEY_2', array('slice_3' => false));

try {
    $flumeLogger->commit();
} catch (Exception $exception) {
    echo $exception->getMessage(), '<br/>';
    echo '<pre>', $exception->getTraceAsString(), '</pre>';
}
