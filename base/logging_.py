from common.config_do import Config_do

import logging, os
from logging.handlers import RotatingFileHandler

from base.base import *

logger = logging.getLogger(__name__)
logger.setLevel(Config_do.get_self(Config_do.config, ["config", "log_level"], "INFO"))
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s"
)

_path = os.path.dirname(os.path.abspath(__name__))
# print(path)
# # FileHandler
# file_handler = logging.FileHandler(
#     Config_do.get_self(Config_do.config, ["config", "log_file"], "output.log"),
#     mode="w",
# )
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# StreamHandler
stream_handler = logging.StreamHandler()
# stream_handler.setLevel("DEBUG")  # 先由logger过滤
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# FileHandler,大小限制,日志记录流
fsize_handler = RotatingFileHandler(
    Config_do.get_self(Config_do.config, ["config", "log_file"], "static/output.log"),
    # _path + os.sep + "static" + os.sep + "log" + os.sep + "output.log",
    mode="w",  # 默认为a了
    maxBytes=1024 * 1024 * 10,
    encoding="utf-8",
)
fsize_handler.setFormatter(formatter)
logger.addHandler(fsize_handler)


# if __name__ == "__main__":
#     logger.info("This is a log info")
#     logger.debug("Debugging")
#     logger.warning("Warning exists")
#     logger.info("Finish")
