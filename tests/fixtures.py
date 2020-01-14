from PySide2.QtCore import QObject
from PySide2.QtQml import QQmlProperty


def r(object, property):
    """read a qml property"""
    return QQmlProperty.read(object, property)

def s(object, property, value):
    """set a qml property"""
    QObject.setProperty(object, property, value)