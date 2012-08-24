<?php
/**
 * User: pavlenko.roman
 * Email: pavlenko.roman.spb@gmail.com
 * Date: 22.08.12 13:08
 */
include_once dirname(__FILE__) . '/TFAnalyticsKeys.php';
include_once dirname(__FILE__) . '/TFAnalyticsParams.php';
include_once dirname(__FILE__) . '/TFAnalyticsSlices.php';

class TopFaceAnalyticsConfig {

    static $settings = array(

        'keys' => array(

            TFAnalyticsKeys::KEY_1 => array(
                'description' => 'Ключ 1',
                'mustHaveParams' => array(TFAnalyticsParams::PARAM_1, TFAnalyticsParams::PARAM_1),
                'canHaveParams' => array(TFAnalyticsParams::PARAM_1)
            ),

            TFAnalyticsKeys::KEY_2 => array(
                'description' => 'Ключ 2',
                'mustHaveSlices' => array(TFAnalyticsSlices::SLICE_1),
                'canHaveSlice' => array(TFAnalyticsSlices::SLICE_2)
            ),

        ),

        'params' => array(
            TFAnalyticsParams::PARAM_1 => array(
                'values' => array('vk', 'fb'),
            ),

            TFAnalyticsParams::PARAM_2 => array(
                'type' => 'string',
            ),

            TFAnalyticsParams::PARAM_3 => array(
                'type' => 'int',
            )
        ),

        'slices' => array(

            TFAnalyticsSlices::SLICE_1 => array(
                'params' => array(TFAnalyticsParams::PARAM_1, TFAnalyticsParams::PARAM_3)
            ),

            TFAnalyticsSlices::SLICE_2 => array(
                'params' => array(TFAnalyticsParams::PARAM_2, TFAnalyticsParams::PARAM_3)
            ),

        )
    );
}
