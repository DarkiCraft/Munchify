import logging
import random

import numpy as np
import torch


def setup_logger(name="rs_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handlers
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    c_format = logging.Formatter(format_str)
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(c_handler)

    return logger


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
