class AnalyticsException(BaseException):

    def __init__(self, message = '', previouse = None):
        super(AnalyticsException, self).__init__()
        self.message = message
        self.previouse = previouse