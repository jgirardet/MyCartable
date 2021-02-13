import json
from typing import Union, Any

from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtQml import QJSValue
from loguru import logger
from pony.orm import Database, db_session, ObjectNotFound, count
from pony.orm.core import Query


class DTB(QObject):

    db: Database

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        if not getattr(self, "db", None):
            raise NotImplementedError(
                "attribute 'db' must be set before instance creation"
            )

    @db_session
    @pyqtSlot(str, "QVariantMap", result="QVariantMap")
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
                    logger.debug(f"addDB Entity {entity}: {item.to_dict()}")
                    return item.to_dict()
            except TypeError as err:
                logger.error(err)
        return {}

    @db_session
    @pyqtSlot(str, str, result=bool)
    @pyqtSlot(str, int, result=bool)
    def delDB(self, entity_name: str, item_id: str) -> bool:
        """
        Database delete call
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :return: True if delete, False if nothing or fail
        """
        if entity := getattr(self.db, entity_name, None):  # pragma: no branch
            if item := entity.get(id=item_id):  # pragma: no branch
                logger.debug(f"delDB item: {item.to_dict()}")
                item.delete()
                return True
            else:
                logger.error(f"Absence d'item {item_id} dans la table {entity_name}")
                return False
        else:
            logger.error(f"Absence de table {entity_name} dans la base de donnée")
            return False

    @db_session
    @pyqtSlot(str, str, result="QVariantMap")
    @pyqtSlot(str, int, result="QVariantMap")
    def getDB(self, entity_name: str, item_id: str) -> dict:
        """
        Get an Item un database
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :return: True if delete, False if nothing or fail
        """
        if entity := getattr(self.db, entity_name, None):  # pragma: no branch
            if item := entity.get(id=item_id):  # pragma: no branch
                # logger.debug(f"getDB item: {item.to_dict()}")
                return item.to_dict()
            else:
                logger.error(f"Absence d'item {item_id} dans la table {entity_name}")
                return {}
        else:
            logger.error(f"Absence de table {entity_name} dans la base de donnée")
            return {}

    @db_session
    @pyqtSlot(str, str, "QVariantMap", result="QVariantMap")
    @pyqtSlot(str, int, "QVariantMap", result="QVariantMap")
    @pyqtSlot(str, "QVariantList", "QVariantMap", result="QVariantMap")
    def setDB(self, entity: str, item_id: Union[str, int, list], params: dict) -> dict:
        """
        Modify a row in database.
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :param params: dict. paremeter to edit in  row.
        :return: True if ok, else False
        """
        if isinstance(item_id, list):
            item_id = tuple(item_id)
        if entity := getattr(self.db, entity, None):  # pragma: no branch
            try:
                item = entity[item_id]  # pragma: no branch
            except ObjectNotFound:
                logger.error(f"{entity}[{item_id}] n'existe pas")
                return {}
            try:
                item.set(**params)
                logger.debug(f"setDB item {item}: {params}")
                return item.to_dict()
            except TypeError as err:
                logger.error(err)
            except ValueError as err:
                logger.error(err)
        return {}

    @db_session
    @pyqtSlot(str, result="QVariant")
    def getConfig(self, key: str):
        res = self.db.Configuration.option(key)
        if isinstance(res, dict):  # compliqué de retourner des dict
            res = json.dumps(res)
        return res

    @db_session
    @pyqtSlot(str, "QVariant")
    def setConfig(self, key: str, value: Any):
        if isinstance(value, QJSValue):
            value = value.toVariant()
        self.db.Configuration.add(key, value)

    @db_session
    def execDB(
        self, entity: str, item_id: Union[str, int], func: str, *args, **kwargs
    ) -> Any:
        """
        Runs a method on a row in database.
        N EST PAS Un SLOT
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :param func: str.function name
        :param args: positionnal arguments
        :param kwargs: keyword arguments
        :return: Any
        """
        if entity := getattr(self.db, entity, None):  # pragma: no branch
            if item_id:
                if item := entity.get(id=item_id):  # pragma: no branch
                    try:
                        res = getattr(item, func)(*args, **kwargs)
                    except TypeError as err:
                        logger.exception(err)
                    else:
                        return res

            else:
                try:
                    res = getattr(entity, func)(*args, **kwargs)
                except TypeError as err:
                    logger.exception(err)
                else:
                    return res

    @db_session
    def count(self, query: Union[Query]):
        return count(query)
