import logging
import logging.config
from pathlib import Path

import yaml


def get_config_file_path() -> Path:
    """
    Gets the path to a file with configurations for logging

    Returns
    -------
    Path
        Path to file with logging config options
    """

    return Path(__file__).with_name("logger_config.yaml")


def get_configured_logger(config_path: Path) -> logging.Logger:
    """
    Reads a config file and returs a customized logger

    Parameters
    ----------
    config_path : Path
        Path to file with logging config options

    Returns
    -------
        Return a customized parserLogger

    """
    with config_path.open("r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config=config)

    return logging.getLogger("parserLogger")


logger = get_configured_logger(get_config_file_path())
