<?php
/**
 * User: pavlenko.roman
 * Email: pavlenko.roman.spb@gmail.com
 * Date: 21.08.12 15:49
 */

$GLOBALS['THRIFT_ROOT'] = dirname(__FILE__) . '/thrift-php/';

include_once dirname(__FILE__) . '/TFFlumeLogger.php';
include_once dirname(__FILE__) . '/TFAnalyticsException.php';



/**
 * Класс логгера.
 * Проверяет правильность ключей и сочетания ключа и среза.
 * Отправляет логи через флум.
 */
class TFLogger extends TFFlumeLogger {

    private $settings;

    private $consistSlices = array();

    /**
     * @param $settingFile - путь к файлу настроек ключей и срезов
     */
    public function __construct(&$settings) {
        $this->settings = $settings;
    }

    /**
     * Установить срез и значение, которые будут добавляться ко всем ключам,
     * добавленным после вызова этой функции
     * @param $key string
     * @param $value string|int|float
     */
    public function setConsistSlice($key, $value) {
        $this->consistSlices[$key] = $value;
    }

    /**
     * Массив логов для сохранения
     * @var array
     */
    private $eventStack = array();

    /**
     * @param $key
     * @param array $slices
     * @param bool $sendNow - отправить немедленно
     */
    public function log($key, $slices = array(), $sendNow = false) {

        $slices = $this->processSlices($key, $slices);

        $event = $this->createFlumeEvent($key, $slices);

        if ($sendNow) {
            $this->sendLogEvents(array($event));
        } else {
            $this->eventStack[] = $event;
        }
    }

    /**
     * Отправляет несохраненные логи в флум
     */
    public function commit() {
        if ($this->eventStack) {
            $this->sendLogEvents($this->eventStack);
        }
    }

    /**
     * проверка ключа и сочетаемых срезов
     * @param $key
     * @param $rawParams
     * @throws TFAnalyticsException
     * @return array
     */
    private function processSlices($key, $rawParams) {
        // проверка - есть ли ключ в настройках приложения
        if (!isset($this->settings['keys'][$key])) {
            throw new TFAnalyticsException('Ключ отсутствует в конфигурации аналитики', TFAnalyticsException::WRONG_KEY);
        }

        $params = array();

        $keySettings = $this->settings['keys'][$key];
        $slicesSettings = $this->settings['slices'];

        // параметры, которые должны быть
        $mustHaveParams = array();
        if (isset($keySettings['mustHaveParams'])) {
            $mustHaveParams = $keySettings['mustHaveParams'];
        }

        if (isset($keySettings['mustHaveSlices'])) {
            foreach ($keySettings['mustHaveSlices'] as $sliceName) {
                if (isset($slicesSettings[$sliceName])) {

                    if (isset($slicesSettings[$sliceName]['params'])) {
                        $mustHaveParams += $slicesSettings[$sliceName]['params'];
                    } else {
                        throw new TFAnalyticsException('Ошибка в конфигурации: у настроек среза отсутствует список параметров',
                            TFAnalyticsException::BAD_CONFIG
                        );
                    }

                } else {
                    throw new TFAnalyticsException('Срез отсутствует в конфигурации аналитики',
                        TFAnalyticsException::WRONG_SLICE);
                }
            }
        }

        // проверка
        foreach ($mustHaveParams as $paramName) {
            if (!array_key_exists($paramName, $rawParams)) {
                    throw new TFAnalyticsException('Отсуствует необходимый параметр ' . $paramName . ' для ключа ' . $key,
                        TFAnalyticsException::NO_REQUIRED_PARAM_FOR_KEY);
            }

            $params[$paramName] = $rawParams[$paramName];
        }


        // параметры, которые могут быть или не быть

        $canHaveParams = array();
        if (isset($keySettings['canHaveParams'])) {
            $canHaveParams = $keySettings['canHaveParams'];
        }

        if (isset($keySettings['canHaveSlices'])) {
            foreach ($keySettings['canHaveSlices'] as $sliceName) {
                if (isset($slicesSettings[$sliceName])) {

                    if (isset($slicesSettings[$sliceName]['params'])) {
                        $canHaveParams += $slicesSettings[$sliceName]['params'];
                    } else {
                        throw new TFAnalyticsException('Ошибка в конфигурации: у настроек среза отсутствует список параметров',
                            TFAnalyticsException::BAD_CONFIG
                        );
                    }

                } else {
                    throw new TFAnalyticsException('Срез отсутствует в конфигурации аналитики',
                        TFAnalyticsException::WRONG_SLICE);
                }
            }
        }

        // копируем возможные параметры
        foreach ($canHaveParams as $paramName) {
            $params[$paramName] = $rawParams[$paramName];
        }

        // TODO возможно нужно сделать проверку на лишние параметры

        unset($rawParams);

        $paramSettings = &$this->settings['params'];

        foreach ($params as $paramName => &$value) {
            if (isset($paramSettings[$paramName])) {
                $paramSetting = $paramSettings[$paramName];

                // проверка типа значения параметра
                if (isset($paramSetting['type'])) {
                    switch ($paramSetting['type']) {

                        case 'string':
                            if (is_scalar($value) && !is_bool($value)) {
                                $value = (string)$value;
                            } else {
                                throw new TFAnalyticsException('Тип значения параметра ' . $paramName . ' должен быть ' . $paramSetting['type'],
                                    TFAnalyticsException::WRONG_PARAM_VALUE);
                            }
                        break;

                        case 'int':
                            if (is_numeric($value) && (int)$value == $value) {
                                $value = (int)$value;
                            } else {
                                throw new TFAnalyticsException('Тип значения параметра ' . $paramName . ' должен быть ' . $paramSetting['type'],
                                    TFAnalyticsException::WRONG_PARAM_VALUE);
                            }
                        break;

                        case 'float':
                            if (is_numeric($value) && (float)$value == $value) {
                                $value = (float)$value;
                            } else {
                                throw new TFAnalyticsException('Тип значения параметра ' . $paramName . ' должен быть ' . $paramSetting['type'],
                                    TFAnalyticsException::WRONG_PARAM_VALUE);
                            }
                        break;

                        default:
                            throw new TFAnalyticsException('Неверный тип значения параметра ' . $paramName,
                                TFAnalyticsException::BAD_CONFIG);
                    }
                }


                // проверка на вхождение в список допустимых значений
                if (isset($paramSetting['values'])) {
                    if (!in_array($value, $paramSetting['values'])) {
                        throw new TFAnalyticsException('Значение параметр ' . $paramName . ' не входит в список доступных значений',
                            TFAnalyticsException::WRONG_PARAM_VALUE);
                    }
                }

            } else {
                throw new TFAnalyticsException('Параметр ' . $paramName . ' отсутсвует в конфигурации аналитики',
                    TFAnalyticsException::WRONG_PARAM);
            }
        }

        return $params;
    }
}