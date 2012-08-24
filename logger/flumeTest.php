<?
include_once dirname(__FILE__) . '/TFLogger/TFLogger.php';
include_once dirname(__FILE__) . '/TFLogger/TFAnalyticsConfig.php';

$flumeLogger = new TFLogger(TopFaceAnalyticsConfig::$settings);
$flumeLogger->log('KEY_1', array('param_1' => 'fb', 'param_2' => 'my_string'));
$flumeLogger->log('KEY_1', array('param_1' => 'vk', 'param_2' => 'my_string_2', 'param_3' => 100));
$flumeLogger->log('KEY_2', array('param_1' => 'vk', 'param_3' => 100));
$flumeLogger->log('KEY_2', array('param_1' => 'vk', 'param_3' => 105));
$flumeLogger->log('KEY_2', array('param_1' => 'vk', 'param_3' => 108));

try {
    $flumeLogger->commit();
} catch (Exception $exception) {
    echo $exception->getMessage(), '<br/>';
    echo '<pre>', $exception->getTraceAsString(), '</pre>';
}
