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
     * Неверный срез
     */
    const WRONG_SLICE = 2102;

    /**
     * Отсутствует необходимы параметр для ключа
     */
    const NO_REQUIRED_PARAM_FOR_KEY = 2103;

    /**
     * Неверный срез
     */
    const WRONG_PARAM = 2104;

    /**
     * Неверное значение среза
     */
    const WRONG_PARAM_VALUE = 2105;

    /**
     * Исключение
     */
    const THRIFT_EXCEPTION = 2106;

    /**
     * Неправильная конфигурация аналитики
     */
    const BAD_CONFIG = 2107;
}