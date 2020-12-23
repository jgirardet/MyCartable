from typing import Union, Optional, Any, List

from PySide2.QtCore import Slot
from PySide2.QtQml import QJSValue
from loguru import logger
from pony.orm import Database, db_session, ObjectNotFound
from pytestqml.qt import QObject


class DTB(QObject):

    db: Database

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        if not getattr(self, "db", None):
            raise NotImplementedError(
                "attribute 'db' must be set before instance creation"
            )

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
                logger.error(err)
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
    def getDB(self, entity_name: str, item_id: str) -> dict:
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
    def setDB(self, entity: str, item_id: Union[str, int, tuple], params: dict) -> dict:
        """
        Modify a row in database.
        :param entity: str. Entity Name
        :param item_id: str. Id (pk) of item
        :param params: dict. paremeter to edit in  row.
        :return: True if ok, else False
        """
        if entity := getattr(self.db, entity, None):  # pragma: no branch
            try:
                item = entity[item_id]  # pragma: no branch
            except ObjectNotFound:
                logger.error(f"{entity}[{item_id}] n'existe pas")
                return {}
            try:
                item.set(**params)
                return item.to_dict()
            except TypeError as err:
                logger.error(err)
            except ValueError as err:
                logger.error(err)
        return {}

    @db_session
    @Slot(str, result="QVariant")
    def getConfig(self, key: str):
        return self.db.Configuration.option(key)

    @db_session
    @Slot(str, "QVariant")
    def setConfig(self, key: str, value: Any):
        if isinstance(value, QJSValue):
            value = value.toVariant()
        self.db.Configuration.add(key, value)

    # @Slot(str, str, str, result="QVariantMap")
    # @Slot(str, int, str, result="QVariantMap")
    # @Slot(str, int, str, "QVariantList", "QVariantMap", result="QVariantList")
    # @Slot(str, int, str, "QVariantList", "QVariantMap", result="QVariantList")
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
