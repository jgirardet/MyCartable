from PyQt5.QtCore import QModelIndex
from mycartable.commands import BaseCommand

from .sections import Section


class SectionBaseCommand(BaseCommand):
    def __init__(self, page, **kwargs):
        self.page = page
        self.nb: int = 0  # nombre de section ajoutées
        self.position: int = 0  # position où a été ajouté la section
        super().__init__(**kwargs)


class AddSectionCommand(SectionBaseCommand):

    formulations = {
        "TextSection": "Insérer un zone de texte",
        "EquationSection": "Insérer une zone d'équation",
        "AdditionSection": "Insérer une addition",
        "MultiplicationSection": "Insérer une multiplication",
        "SoustractionSection": "Insérer une soustraction",
        "DivisionSection": "Insérer une division",
        "TableauSection": "Insérer une tableau",
        "FriseSection": "Insérer une frise",
        "ImageSection": "Insérer une image",
    }

    def redo_command(self) -> None:

        position = self.params.get("position", None)
        if position is None:
            position = self.page.model.rowCount(QModelIndex())
        self.params["position"] = position

        self.undo_text = self.formulations.get(self.params["classtype"], "")

        new_secs = Section.new_sub(page=self.page.id, **self.params)
        new_secs = [new_secs] if not isinstance(new_secs, list) else new_secs
        new_secs = list(filter(lambda x: x is not None, new_secs))  # on enleve les None
        nb = len(new_secs) - 1
        if nb >= 0:
            self.nb = nb
            self.position = position
            self.page.model.insertRows(position, nb)

    def undo_command(self) -> None:
        self.page.model.removeRows(
            self.position, self.nb
        )  # removeRows enleve 1 de base déjà enlevé avant
