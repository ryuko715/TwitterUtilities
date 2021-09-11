# coding: cp932

import os
import sys
import re
import pathlib
import logging
import logging.config
import inspect
import datetime
import traceback
import copy
import coloredlogs

sys.path.append( str(pathlib.Path(__file__).resolve().parent.parent) )

# ログフォーマット
FORMAT = "%(levelname)-8s %(asctime)s %(message)s"
LOGGER_DICT_CONF = {
    'version': 1,
    'disable_existing_loggers': False,
    # ロガーの対象一覧
    'root': {
        'level': 'INFO',
        'handlers': [
            'consoleHandler',
            'logFileHandler'
        ]
    },
    # ハンドラの設定
    'handlers': {
        'consoleHandler':{
            'class': 'logging.StreamHandler',
            "formatter": "consoleFormatter",
            "stream": "ext://sys.stdout"
        },
        'logFileHandler': {
            'class': 'logging.FileHandler',
            'formatter': 'logFileFormatter',
            'filename': './log/ToolsBase.log',
            'mode': 'w',
            # 'encoding': 'utf-8'
            'encoding': 'cp932'
        }
    },
    # フォーマットの設定
    'formatters': {
        'consoleFormatter': {
            'format': FORMAT
        },
        'logFileFormatter': {
            'format': FORMAT
        }
    }
}

coloredlogs.CAN_USE_BOLD_FONT = True
coloredlogs.DEFAULT_FIELD_STYLES = {
    'asctime': {'color': 'black', 'bold': True},
    'hostname': {'color': 'magenta'},
    'levelname': {'color': 'black', 'bold': True},
    'name': {'color': 'blue'},
    'programname': {'color': 'cyan'}
}

coloredlogs.DEFAULT_LEVEL_STYLES = {
    'critical': {'color': 'red', 'bold': True, 'bright': True},
    'error': {'color': 'red', 'bold': True},
    'warning': {'color': 'yellow', 'bold': True},
    'notice': {'color': 'magenta'},
    'info': {'color': 'green', 'bright': True},
    'debug': {'color': 'black', 'bold': True},
    'spam': {'color': 'green', 'faint': True},
    'success': {'color': 'green', 'bold': True},
    'verbose': {'color': 'blue'}
}

class Logger(object):
    """
    logging ラッパークラス
    """
    __Logger = None

    __Level = {
        "DEBUG": 1,
        "INFO": 2,
        "WARNING": 3,
        "ERROR": 4,
        "CRITICAL": 5,
    }

    __LevelForColoredLogs = {
        "1": "debug",
        "2": "info",
        "3": "warning",
        "4": "error",
        "5": "critical",
    }

    @classmethod
    def get_logger(cls, level="DEBUG", file="", stdout="ON"):
        if cls.__Logger is None:
            cls.__Logger = Logger(level=level, file=file, stdout=stdout)
        
        return cls.__Logger

    @classmethod
    def delete_logger(cls):
        if cls.__Logger is None:
            return
        
        if "consoleHandler" not in cls.__Logger.config["root"]["handlers"]:
            cls.__Logger.config["root"]["handlers"].append("consoleHandler")
            logging.config.dictConfig(cls.__Logger.config)
        
        cls.__Logger.end = datetime.datetime.now()
        cls.__Logger.elapsed = cls.__Logger.end - cls.__Logger.start
        msg = f"end logging! critical={cls.__Logger.critical_count} error={cls.__Logger.error_count} warning={cls.__Logger.warning_count} elapsed={cls.__Logger.elapsed}"
        cls.__Logger.info(msg)

        cls.__Logger = None

    def __init__(self, level="DEBUG", file="", stdout="ON"):
        self.start = datetime.datetime.now()

        logfile = file if file != "" else LOGGER_DICT_CONF["handlers"]["logFileHandler"]["filename"]
        if "%DATE%" in logfile:
            logfile = logfile.replace("%DATE%", self.start.strftime('%Y%m%d%H%M%S%f'))

        self.level = level
        self.file = pathlib.Path(logfile).resolve()
        self.stdout = stdout
        self.critical_count = 0
        self.error_count = 0
        self.warning_count = 0

        self.config = copy.deepcopy(LOGGER_DICT_CONF)
        if level in Logger.__Level:
            self.config["root"]["level"] = level
        else:
            self.level = "DEBUG"
        
        if self.file.is_file():
            self.file.rename(f"{self.file}.{self.start.strftime('%Y%m%d%H%M%S%f')}")

        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.config["handlers"]["logFileHandler"]["filename"] = self.file

        logging.config.dictConfig(self.config)
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level=level, logger=self.logger, fmt=FORMAT)

        self.info(f"started logging logfile={logfile}")
        # self.config["root"]["handlers"] = [h for h in self.config["root"]["handlers"] if h != "consoleHandler"]
        # logging.config.dictConfig(self.config)

    def critical(self, msg):
        self.critical_count += 1
        if Logger.__Level["CRITICAL"] < Logger.__Level[self.level]:
            return self
        
        formatted = self.__format_msg(msg, inspect.stack())
        trace = traceback.format_exc()
        try:
            self.logger.critical(formatted)
            if not trace.startswith("NoneType: None"):
                self.logger.critical(trace)
        except Exception:
            self.__console("CRITICAL", formatted)
            if not trace.startswith("NoneType: None"):
                self.__console("CRITICAL", trace)
            
            self.__console("CRITICAL", traceback.format_exc())
        finally:
            Logger.delete_logger()
            sys.exit(8)
        
        return self

    def error(self, msg):
        self.error_count += 1
        if Logger.__Level["ERROR"] < Logger.__Level[self.level]:
            return self
        
        formatted = self.__format_msg(msg, inspect.stack())
        try:
            self.logger.error(formatted)
        except Exception:
            self.__console("ERROR", formatted)
            self.__console("ERROR", traceback.format_exc())
        
        return self

    def warning(self, msg):
        self.warning_count += 1
        if Logger.__Level["WARNING"] < Logger.__Level[self.level]:
            return self
        
        formatted = self.__format_msg(msg, inspect.stack())
        try:
            self.logger.warning(formatted)
        except Exception:
            self.__console("WARNING", formatted)
            self.__console("WARNING", traceback.format_exc())
        
        return self

    def info(self, msg):
        if Logger.__Level["INFO"] < Logger.__Level[self.level]:
            return self
        
        formatted = self.__format_msg(msg, inspect.stack())
        try:
            self.logger.info(formatted)
        except Exception:
            self.__console("INFO", formatted)
            self.__console("INFO", traceback.format_exc())
        
        return self


    def debug(self, msg):
        if Logger.__Level["DEBUG"] < Logger.__Level[self.level]:
            return self
        
        formatted = self.__format_msg(msg, inspect.stack())
        try:
            self.logger.debug(formatted)
        except Exception:
            self.__console("DEBUG", formatted)
            self.__console("DEBUG", traceback.format_exc())
        
        return self

    def  __format_msg(self, msg, inspect_stack):
        str_msg = str(msg)
        pgm = pathlib.Path(inspect_stack[1].filename).stem
        func = inspect_stack[1].function
        line = inspect_stack[1].lineno
        return f"{str_msg} at {pgm}#{func}() lineno={line}"
    
    def __console(self, level, msg, edit_micro_sec=True):
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minitue = now.minute
        second = now.second
        micro_sec = str(now.microsecond)
        if edit_micro_sec:
            micro_sec = re.sub(r'^(?P<enable>\d{3}).*$', r'\g<enabel>', str(micro_sec))

        asctime = f"{year}-{month:0=2}-{day:0=2} {hour:0=2}:{minitue:0=2}:{second:0=2}.{micro_sec}"
        print(f"{level:<8} {asctime} {msg}")

        return self

if __name__ == "__main__":
    print("start")
    __logger = Logger.get_logger()
    __logger.debug("debug")
    __logger.info("info")
    __logger.warning("warning")
    __logger.error("error")
    __logger.critical("critical")
    __logger.debug("debug")
