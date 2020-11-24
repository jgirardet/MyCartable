from PySide2.QtCore import Signal, Property, QObject
from mycartable.types.bridge import Bridge


class Section(Bridge):
    nullSignal = Signal()

    entity_name = "Section"

    @Property(str, notify=nullSignal)
    def classtype(self):
        return self._data["classtype"]
