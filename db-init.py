"""
:author: vic on 2021-03-13
"""
from dbschema import Base, Engine


def init():
    import logging.config
    import os

    if os.path.exists("logging.conf"):
        logging.config.fileConfig("logging.conf")
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)-7s - %(message)s',
                            datefmt='%Y-%m-%dT%H:%M:%S')

    logging.info("Setting up database schema for application operation")
    logging.info("Checking if database file exists...")
    if os.path.exists("./database/library.db"):
        logging.info("Library database file exists")
    else:
        logging.warning("Library database file does not exist. Creating...")
        if not os.path.exists("./database"):
            os.makedirs("./database")
        with open("./database/library.db", "w+"):
            pass
        logging.info("Library database created")
    logging.info("Creating db metadata...")
    Base.metadata.create_all(Engine)
    logging.info("Metadata created")


if __name__ == '__main__':
    init()
