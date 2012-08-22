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
    public function __construct($settingFile) {
        $this->settings = json_decode(file_get_contents($settingFile), true);
        //var_dump(file_get_contents($settingFile));
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
     * Кеш TFAnalyticsKeys
     * @var ReflectionClass
     */
    //private $KeyReflection;

    /**
     * проверка ключа и сочетаемых срезов
     * @param $key
     * @param $rawSlices
     * @throws TFAnalyticsException
     * @return array
     */
    private function processSlices($key, $rawSlices) {

        //if (!$this->KeyReflection)
        //    $this->KeyReflection = new ReflectionClass(TFAnalyticsKeys::getClassName());

        // проверка ключа
        //if (!$this->KeyReflection->hasConstant($key)) {
        //    throw new TFAnalyticsException('Ключ отсутвует в списке известных ключей', TFAnalyticsException::WRONG_KEY);
        //}

        // проверка срезов
        if (!isset($this->settings['keys'][$key])) {
            throw new TFAnalyticsException('Ключ отсутствует в настройке приложения', TFAnalyticsException::WRONG_KEY);
        }

        $slices = array();

        $keySettings = $this->settings['keys'][$key];

        // срезы, которые должны быть
        if (isset($keySettings['mustHaveSlices'])) {
            foreach ($keySettings['mustHaveSlices'] as $sliceName) {
                if (!array_key_exists($sliceName, $rawSlices)) {
                    throw new TFAnalyticsException('Отсуствует необходимый срез для ключа',
                        TFAnalyticsException::NO_REQUIRED_SLICE_FOR_KEY);
                }

                $slices[$sliceName] = $rawSlices[$sliceName];
            }
        }

        // срезы, которые могут быть или не быть
        if (isset($keySettings['canHaveSlices'])) {
            foreach ($keySettings['canHaveSlices'] as $sliceName) {
                if (array_key_exists($sliceName, $rawSlices)) {
                    $slices[$sliceName] = $rawSlices[$sliceName];
                }
            }
        }

        unset($rawSlices);
        $sliceSettings = $this->settings['slices'];
        foreach ($slices as $sliceName => $value) {
            if (isset($sliceSettings[$sliceName])) {
                $sliceSetting = $sliceSettings[$sliceName];

                // проверка на вхождение в список допустимых значений
                if (isset($sliceSetting['values'])) {
                    if (!in_array($value, $sliceSetting['values'])) {
                        throw new TFAnalyticsException('Значение среза не входит в список доступных значений',
                            TFAnalyticsException::WRONG_SLICE_VALUE);
                    }
                }

            } else {
                throw new TFAnalyticsException('Срез отсутсвует в списке допустимых срезов', TFAnalyticsException::WRONG_SLICE);
            }
        }

        return $slices;
    }
}