"""
Provides a standardized, color-coded logger for the application.
"""
import logging
import sys


class ColoredFormatter(logging.Formatter):
    """
    A custom log formatter that adds color to log levels.
    """

    # ANSI escape codes for colors
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    # The format string for the log message
    log_format = (
        "%(asctime)s | %(name)s | %(levelname)-8s: %(message)s"
    )

    # A dictionary to map log levels to color formats
    FORMATS = {
        logging.DEBUG: GREY + log_format + RESET,
        logging.INFO: GREEN + log_format + RESET,
        logging.WARNING: YELLOW + log_format + RESET,
        logging.ERROR: RED + log_format + RESET,
        logging.CRITICAL: BOLD_RED + log_format + RESET,
    }

    def format(self, record):
        """
        Overrides the default format method to apply color.
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Creates and configures a logger.

    Args:
        name: The name of the logger, typically __name__.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger

    handler = logging.StreamHandler(sys.stdout)
    
    # Use our new ColoredFormatter
    handler.setFormatter(ColoredFormatter())

    logger.addHandler(handler)

    return logger



