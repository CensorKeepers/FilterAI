import pathlib
import json
import logging


class Logger():
    __terminalLogger: logging.Logger = None
    __isTerminalLoggerEnabled: bool = None
    __fileLogger: logging.Logger = None
    __isFileLoggerEnabled: bool = None
    __fileLoggerPath: str = None

    def __init__(self) -> 'Logger':
        self.__path: pathlib.Path = pathlib.Path(
            str(pathlib.Path(__file__).parent.parent) + '/config/LoggerConfig.json')
        self.__config: dict = None
        self.__readConfigFile()
        self.__configureLogger()

    def __readConfigFile(self) -> None:
        file = open(self.__path, mode='r', encoding='utf-8')
        self.__config = json.load(file)
        file.close()

    def __configureLogger(self) -> None:
        level: int = logging.WARNING
        if self.__config['level'] == 'debug':
            level = logging.DEBUG
        elif self.__config['level'] == 'info':
            level = logging.INFO
        elif self.__config['level'] == 'error':
            level = logging.ERROR
        elif self.__config['level'] == 'warning':
            level = logging.WARNING
        elif self.__config['level'] == 'critical':
            level = logging.CRITICAL
        elif self.__config['level'] == 'fatal':
            level = logging.FATAL
        else:
            raise ValueError(
                f'Invalid log level "{self.__config["level"]}". Options are {{debug|info|error|warning|critical|fatal}}')

        logging.basicConfig(
            format=self.__config['format'], level=level)
        Logger.__terminalLogger = logging.getLogger('terminal')
        Logger.__isTerminalLoggerEnabled = self.__config['terminal']
        Logger.__fileLogger = logging.getLogger('file')
        Logger.__isFileLoggerEnabled = self.__config['file']
        Logger.__fileLoggerPath = self.__config['filePath']

    @staticmethod
    def warn(message: str) -> None:
        if Logger.__isTerminalLoggerEnabled:
            Logger.__terminalLogger.warn(message)
        if Logger.__isFileLoggerEnabled:
            Logger.__fileLogger.warn(message)

    @staticmethod
    def debug(message: str) -> None:
        if Logger.__isTerminalLoggerEnabled:
            Logger.__terminalLogger.debug(message)
        if Logger.__isFileLoggerEnabled:
            Logger.__fileLogger.debug(message)

    @staticmethod
    def info(message: str) -> None:
        if Logger.__isTerminalLoggerEnabled:
            Logger.__terminalLogger.info(message)
        if Logger.__isFileLoggerEnabled:
            Logger.__fileLogger.info(message)

    @staticmethod
    def error(message: str) -> None:
        if Logger.__isTerminalLoggerEnabled:
            Logger.__terminalLogger.error(message)
        if Logger.__isFileLoggerEnabled:
            Logger.__fileLogger.error(message)

    @staticmethod
    def critical(message: str) -> None:
        if Logger.__isTerminalLoggerEnabled:
            Logger.__terminalLogger.critical(message)
        if Logger.__isFileLoggerEnabled:
            Logger.__fileLogger.critical(message)

    @staticmethod
    def fatal(message: str) -> None:
        if Logger.__isTerminalLoggerEnabled:
            Logger.__terminalLogger.fatal(message)
        if Logger.__isFileLoggerEnabled:
            Logger.__fileLogger.fatal(message)
