""" ssm.abcs.loggable
    (boilerplate for logger abstract base)
"""

from ssm import util


class Loggable:
    """
    a mixin that allows subclassers to call things like
    self.logger.debug(..) etc with no hassle
    """

    def __init__(self, name=None, **kwargs):
        if hasattr(self, "logger"):
            return
        logger_name = getattr(self, "logger_name", name or self.__class__.__name__)
        self.logger_name = logger_name
        self.logger = util.get_logger(self.logger_name)
