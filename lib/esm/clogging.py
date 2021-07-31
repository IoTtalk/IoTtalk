
"""
Usage:
    Same as logging.basicConfig().
    Call clogging.basicConfig() will change the default Formatter
    of all root handlers.

Example:

    import clogging
    import logging

    clogging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info('something')

Compatibility:
    This module is compatible with python2 and python3.
"""

import logging

#DEFAULT_FORMAT = '%(levelname)-8s %(asctime)s %(name)s:%(lineno)3d| %(message)s'
DEFAULT_FORMAT = '%(asctime)s %(name)s:%(lineno)d| %(message)s'
DEFAULT_DT_FORMAT = '%H:%M'

class ColorfulFormatter(logging.Formatter):
    color = {
        'D': '\033[0;30m', 'LD': '\033[1;30m',
        'R': '\033[0;31m', 'LR': '\033[1;31m',  # CRITICAL
        'G': '\033[0;32m', 'LG': '\033[1;32m',  # INFO
        'Y': '\033[0;33m', 'LY': '\033[1;33m',  # WARNING
        'B': '\033[0;34m', 'LB': '\033[1;34m',
        'M': '\033[0;35m', 'LM': '\033[1;35m',  # ERROR
        'C': '\033[0;36m', 'LC': '\033[1;36m',
        'W': '\033[0;37m', 'LW': '\033[1;37m',  # DEBUG
        'E': '\033[m',
    }
    level_color = {
        'CRITICAL': color['R'],
        'ERROR':    color['M'],
        'WARNING':  color['Y'],
        'INFO':     color['G'],
        'DEBUG':    color['W'],
    }

    def format(self, record):
        if isinstance(record.msg, str):
            record.msg = record.msg.format(**self.color)
        s = super().format(record)
        if record.levelname in self.level_color:
            s = (
                self.level_color[record.levelname] +
                record.levelname[0] + ' ' + s +
                self.color['E']
            )

        return s


def get_default_formatter():
    return ColorfulFormatter(DEFAULT_FORMAT, DEFAULT_DT_FORMAT)


def basicConfig(**kwargs):
    if 'format' not in kwargs:
        kwargs['format'] = DEFAULT_FORMAT

    logging.basicConfig(**kwargs)

    colorful_formatter = ColorfulFormatter(fmt=kwargs['format'])
    root_logger = logging.getLogger()
    for hdlr in root_logger.handlers:
        hdlr.setFormatter(colorful_formatter)
