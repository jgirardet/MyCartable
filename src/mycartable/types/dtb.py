from typing import Union

from PySide2.QtCore import Slot
from loguru import logger
from pony.orm import Database, db_session
from pytestqml.qt import QObject


class DTB(QObject):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

    @db_session
    @Slot(str, "QVariantMap", result="QVariantMap")
    def addDB(self, entity: str, params: dict) -> dict:
        """
        Add a row in database.
        :param entity: str. Entity Name
        :param params: dict. paremeter to create row.
        :return: dict.
        """
        if entity := getattr(self.db, entity, None):  # pragma: no branch
            try:
                if item := entity(**params):  # pragma: no branch
                    return item.to_dict()
            except TypeError as err:
                logger.exception(err)
        return {}

    @db_session
    @Slot(str, str, result=bool)
    @Slot(str, int, result=bool)
    def delDB(self, entity_name: str, item_id: str) -> bool:
        """
        Database delete call
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :return: True if delete, False if nothing or fail
        """
        if entity := getattr(self.db, entity_name, None):  # pragma: no branch
            if item := entity.get(id=item_id):  # pragma: no branch
                item.delete()
                return True
            else:
                logger.error(f"Absence d'item {item_id} dans la table {entity_name}")
                return False
        else:
            logger.error(f"Absence de table {entity_name} dans la base de donnée")
            return False

    @db_session
    @Slot(str, str, result="QVariantMap")
    @Slot(str, int, result="QVariantMap")
    def getDB(self, entity_name: str, item_id: str) -> bool:
        """
        Get an Item un database
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :return: True if delete, False if nothing or fail
        """
        if entity := getattr(self.db, entity_name, None):  # pragma: no branch
            if item := entity.get(id=item_id):  # pragma: no branch
                return item.to_dict()
            else:
                logger.error(f"Absence d'item {item_id} dans la table {entity_name}")
                return {}
        else:
            logger.error(f"Absence de table {entity_name} dans la base de donnée")
            return {}

    @db_session
    @Slot(str, str, "QVariantMap", result="QVariantMap")
    @Slot(str, int, "QVariantMap", result="QVariantMap")
    def setDB(self, entity: str, item_id: Union[str, int], params: dict) -> dict:
        """
        Modify a row in database.
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :param params: dict. paremeter to edit in  row.
        :return: True if ok, else False
        """
        if entity := getattr(self.db, entity, None):  # pragma: no branch
            if item := entity.get(id=item_id):  # pragma: no branch
                try:
                    item.set(**params)
                    return item.to_dict()
                except TypeError as err:
                    logger.exception(err)
        return {}
