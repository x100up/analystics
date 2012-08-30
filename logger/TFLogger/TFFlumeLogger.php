<?php
/**
 * User: pavlenko.roman
 * Email: pavlenko.roman.spb@gmail.com
 * Date: 16.08.12 10:51
 */

include_once dirname(__FILE__) . '/thrift-php/Thrift.php';
include_once dirname(__FILE__) . '/thrift-php/transport/TTransport.php';
include_once dirname(__FILE__) . '/thrift-php/transport/TTransport.php';
include_once dirname(__FILE__) . '/thrift-php/transport/TSocket.php';
include_once dirname(__FILE__) . '/thrift-php/protocol/TBinaryProtocol.php';
include_once dirname(__FILE__) . '/thrift-php/packages/flume/flume_types.php';
include_once dirname(__FILE__) . '/thrift-php/packages/flume/ThriftFlumeEventServer.php';


/**
 *
 */
abstract class TFFlumeLogger {

    /**
     * Хост Flum -a
     * @var string
     */
    //private $host = 'web345.verumnets.ru';
    private $host = 'localhost';

    /**
     * Устанавливает хост flume-a
     * @param $host string
     */
    public function setHost($host) {
        $this->host = $host;
    }

    /**
     * Порт Flum -a
     * @var int
     */
    private $port = 5140;

    /**
     * Устанавливает порт flume-a
     * @param $port int
     */
    public function setPort($port) {
        $this->port = $port;
    }

    /**
     * Название хоста сбора статистики.
     * По аналогии с SQL - база данных.
     * @var string
     */
    private $analyticHost = 'topface';

    /**
     * Устанавливает хост сбора статистики
     * @param string $analyticHost
     */
    public function setAnalyticHost($analyticHost) {
        $this->analyticHost = $analyticHost;
    }

    /**
     * Создает ThriftFlumeEvent для отправки во флум
     * @param $key
     * @param array $params
     */
    protected function createFlumeEvent($key, $params = array()) {

        $dateArray = getdate();
        $date = array(
            'year'      => $dateArray['year'],
            'month'     => $dateArray['mon'],
            'day'       => $dateArray['mday']
        );

        // поля события нужны для формирования пути
        // по которуму флум положит файлы в HDFS
        $fields = $date;
        $fields['key'] = $key;

        // поля тела записи - то, что запишется в файл
        $params =  array(
            $params,
            'ts' => $dateArray[0],
            'hours' => $dateArray['hours'],
            'minutes' => $dateArray['minutes'],
            'second' => $dateArray['seconds'],
        ) + $date;

        $body = $this->createBodyString($params);
        echo $body, '<br />';
        return new ThriftFlumeEvent(array(
            'host' => $this->analyticHost,
            'body' => $body,
            'priority' => Priority::INFO,
            'fields' => $fields
        ));
    }

    /**
     * Отправляет логи во флум
     * @param $events - массив ThriftFlumeEvent
     */
    protected function sendLogEvents($events) {
        $socket = new TSocket($this->host, $this->port);
        $protocol = new TBinaryProtocol($socket);
        $client = new ThriftFlumeEventServerClient($protocol);

        try{
            $socket->open();
            foreach ($events as $event) {
                $client->append($event);
            }
            $socket->close();
        } catch (TException $exception) {
            throw new TFAnalyticsException('Исключение при работе с трифтом', TFAnalyticsException::THRIFT_EXCEPTION, $exception);
        }
    }

    //
    // Константы ниже используются для постороения строк,
    // которые может разобрать hive. Если их изменить, то
    // старые данные будут, в лучшем случае, недоступны для чтения.
    //

    /**
     * разделитель полей
     */
    const BODY_FIELDS_TERMINATED = ',';

    /**
     * Разделитель элементов массива
     */
    const BODY_COLLECTION_ITEMS_TERMINATED = ';';

    /**
     * Разделитель ключа и значения массива
     */
    const BODY_MAP_KEYS_TERMINATED = '=';

    /**
     * Сериализует массив параметров в строку, годную для логирования и чтения через Hive.
     * Значения массива $params - скалярные или массив со скалярными значенями.
     * Остальные значения игнорируются.
     * @param array $params
     * @return string
     */
    private function createBodyString($params = array()) {
        $fields = array();

        foreach ($params as $param) {
            if (is_scalar($param)) {
                $fields[] = $param;
            } else if (is_array($param)) { // <- если массив то клеим
                $mapElements = array();

                foreach ($param as $key => $value) {
                    if (is_scalar($value)) {
                        if (is_bool($value)) {
                            $value = $value ? 'TRUE' : 'FALSE';
                        }
                    } else if(is_null($value)) {
                        $value = 'NULL';
                    } else {
                        throw new TFAnalyticsException('Недопустимый тип значения параметра');
                    }

                    $mapElements[] = $key . self::BODY_MAP_KEYS_TERMINATED . $value;
                }

                $fields[] = implode(self::BODY_COLLECTION_ITEMS_TERMINATED, $mapElements);
            }
        }

        return implode(self::BODY_FIELDS_TERMINATED, $fields);
    }


}