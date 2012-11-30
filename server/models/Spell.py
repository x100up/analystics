# coding=utf-8

class Spell():

    #Название события в легенде
    EVENT_KEY_LEGEND_NAME = 'event_key_legend_name'

    #Название при подсчете количества тега
    EVENT_TAG_COUNT_NAME = 'event_tag_count_name'

    #Название при подсчете среднего значения тега
    EVENT_TAG_AVG_NAME = 'event_tag_avg_name'

    #Название при подсчете суммы тега
    EVENT_TAG_SUM_NAME = 'event_tag_sum_name'

    #Название при группировке значений тега
    EVENT_TAG_GROUP_NAME = 'event_tag_group_name'

    def __init__(self):
        self.keyFields = {
            self.EVENT_KEY_LEGEND_NAME: u'Название события в легенде',
        }

        self.tagFields = {
            self.EVENT_TAG_AVG_NAME: u'Среднее значение тега',
            self.EVENT_TAG_COUNT_NAME: u'Количество значений тега',
            self.EVENT_TAG_SUM_NAME: u'Сумма значении тега',
        }
