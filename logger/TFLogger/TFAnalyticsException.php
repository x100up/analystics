<?php
/**
 * User: pavlenko.roman
 * Email: pavlenko.roman.spb@gmail.com
 * Date: 21.08.12 16:31
 */

class TFAnalyticsException extends Exception {
    /**
     * Неверный ключ
     */
    const WRONG_KEY = 2101;

    /**
     * Отсутствует необходимы срез для ключа
     */
    const NO_REQUIRED_SLICE_FOR_KEY = 2102;

    /**
     * Неверный срез
     */
    const WRONG_SLICE = 2103;

    /**
     * Неверное значение среза
     */
    const WRONG_SLICE_VALUE = 2104;

    /**
     * Исключене
     */
    const THRIFT_EXCEPTION = 2105;
}