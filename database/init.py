"""
:author: vic on 2021-03-13
"""
from database.schema import Base, Engine

import logging.config
import os


def run():
    logger = logging.getLogger("library")
    logger.info("Setting up database schema for application operation")
    logger.info("Checking if database file exists...")
    if os.path.exists("./database/library.db"):
        logger.info("Library database file exists")
    else:
        logger.warning("Library database file does not exist. Creating...")
        if not os.path.exists("./database"):
            os.makedirs("./database")
        with open("./database/library.db", "w+"):
            pass
        logger.info("Library database created")
    logger.info("Creating db metadata...")
    Base.metadata.create_all(Engine)
    logger.info("Metadata created")
