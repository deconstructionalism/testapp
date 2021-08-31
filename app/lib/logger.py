from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from os import getenv
import logging

load_dotenv()

# define log level based on env var `DEBUG`
logging_level = logging.DEBUG if getenv("DEBUG") == "1" else logging.INFO

# define rotating file handler (max size 5 MB)
file_handler = RotatingFileHandler(
    "summarizer.log",
    mode='a',
    maxBytes=5*1024*1024
)

# define console stream handler
console_handler = logging.StreamHandler()

# set up basic logging config with handlers
logging.basicConfig(
    level=logging_level,
    format="%(asctime)s.%(msecs)03d |%(levelname)s|  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        file_handler,
        console_handler
    ]
)

# instantiate a logger
logger = logging.getLogger("summarizer")
