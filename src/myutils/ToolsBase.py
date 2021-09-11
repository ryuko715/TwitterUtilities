# coding: cp932

import sys
import pathlib
import json
import signal

sys.path.append( str(pathlib.Path(__file__).resolve().parent.parent) )
from myutils.Logger import Logger

def sigterm_handler(signum, frame) -> None:
    sys.exit(1)

class ToolsBase(object):
    def __init__(self, conf_file) -> None:
        try:
            super().__init__()
            self.conf_file = conf_file

            self._init_conf()

            self.logger = Logger.get_logger(
                level=self.config["LOG"]["LEVEL"],
                file=self.config["LOG"]["FILE"],
                stdout=self.config["LOG"]["STDOUT"]
            )
        except Exception as ex:
            Logger.get_logger().critical(f"初期処理に失敗しました。{ex}")

    def main(self):
        signal.signal(signal.SIGTERM, sigterm_handler)
        try:
            self._init()
            self._main()
            self._term()
            return self
        except Exception as ex:
            self.logger.critical(f"致命的なエラーが発生しました。強制終了します。{ex}")
        finally:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self._cleanup()
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_DFL)

    def _init(self):
        return self

    def _main(self):
        return self

    def _term(self):
        return self

    def _init_conf(self):
        self.conf_file = pathlib.Path(self.conf_file).resolve()
        if not self.conf_file.is_file():
            Logger.get_logger().critical(f"設定ファイルが存在しません。{self.conf_file}")
        
        with self.conf_file.open(mode='r', encoding='shift_jis') as f:
            self.config = json.load(f)

        return self

    def _cleanup(self):
        Logger.delete_logger()
        return

if __name__ == "__main__":
    ToolsBase(sys.argv).main()
