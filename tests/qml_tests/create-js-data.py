import sys
import time
from datetime import datetime
from operator import itemgetter
from pathlib import Path
import json

from PySide2.QtCore import QUrl
from pony.orm import db_session

MAT = ["Math", "Français", "Histoire", "Anglais"]


class CreateJs:
    def __init__(self):
        self.new = {}
        from package.database_object import DatabaseObject

        self.dao = DatabaseObject(package.database.db)
        self.populate()

    def populate(self):
        from package.database.factory import (
            f_annee,
            f_matiere,
            f_page,
            f_section,
            f_imageSection,
            f_stabylo,
            f_textSection,
            f_annotationText,
        )

        self.annee = f_annee(id="2019")
        self.matieres = [f_matiere(x, self.annee.id,) for x in MAT]
        self.dao.setup_settings(annee=2019)
        self.dao.init_matieres()
        math = self.matieres[0]
        with db_session:
            self.activites = math.activites.select()[:]
        self.pages = []

        for i in range(4):
            for p in self.activites:
                self.pages.append(
                    f_page(
                        activite=p.id,
                        titre=f"letitre {p.famille} {i}",
                        created=datetime.utcnow(),
                    )
                )
                time.sleep(1 / 1000)  # le temps passe moins vite sur windows

        self.la_page = self.pages[0]
        self.image_sections = [f_imageSection(page=self.la_page.id) for i in range(4)]
        self.la_image_section = self.image_sections[0]
        self.la_annotationText = f_annotationText(
            0.1, 0.2, "un annotation", section=self.la_image_section.id
        )
        self.le_stabylo = f_stabylo(
            0.5, 0.6, 0.1, 0.2, section=self.la_image_section.id, color="green"
        )  # green = 4278222848, '#008000'
        self.la_annotationText2 = f_annotationText(
            0.1,
            0.4,
            "un annotation",
            section=self.la_image_section.id,
            color="green",
            underline=True,
        )

    # def matiere(self):
    #
    #     self.new["getMatiereIndexFromId"] = {
    #         "id" + str(k): getattr(self.dao, "getMatiereIndexFromId")(k)
    #         for k in range(1, len(MAT))
    #     }
    #
    #     self.new["currentMatiere"] = []
    #     for i in range(1, len(self.dao.matieresListNom) + 1):
    #         setattr(self.dao, "currentMatiere", i)
    #         self.new["currentMatiere"].append(getattr(self.dao, "currentMatiere"))
    #
    #     self.new["matieresListNom"] = getattr(self.dao, "matieresListNom")
    #     self.dao.currentMatiere = 1
    #     self.new["pagesParSection"] = self.dao.pagesParSection

    def activite(self):

        self.dao.currentMatiere = 1

    def page(self):

        self.new["currentPage"] = []
        self.new["currentTitre"] = []
        for i in self.pages:
            setattr(self.dao, "currentPage", i.id)
            self.new["currentPage"].append(getattr(self.dao, "currentPage"))
            self.new["currentTitre"].append(getattr(self.dao, "currentTitre"))

    def image_section(self):

        self.new["loadAnnotations"] = sorted(
            self.dao.loadAnnotations(self.la_image_section.id), key=itemgetter("id")
        )
        # shunt le problème de QColor non serialisable
        for x in self.new["loadAnnotations"]:
            if x["color"]:
                x["color"] = "#008000"

        # doit retourner 4,5,6 si seulement 2 fabriquées dans populate
        self.new["addAnnotation"] = {
            x["classtype"]: self.dao.addAnnotation(x)
            for x in [
                {
                    "classtype": "AnnotationText",
                    "section": 1.0,
                    "relativeX": 0.3,
                    "relativeY": 0.4,
                    "text": "",
                },
                {
                    "classtype": "Stabylo",
                    "section": 1.0,
                    "relativeX": 0.3,
                    "relativeY": 0.4,
                    "relativeWidth": 0.5,
                    "relativeHeight": 0.6,
                },
                {
                    "classtype": "Stabylo",
                    "section": 1.0,
                    "relativeX": 0.3,
                    "relativeY": 0.4,
                    "relativeWidth": 0.5,
                    "relativeHeight": 0.6,
                },
            ]
        }

    def section(self):
        self.new["loadSection"] = self.dao.loadSection(self.la_image_section.id)
        self.new["addSection"] = self.dao.addSection(
            self.la_page.id, {"path": __file__, "classtype": "ImageSection"}
        )

    def recents(self):
        self.new["recentsModel"] = self.dao.recentsModel

    def check_fixtures(self):

        assert (
            len(self.new["currentPage"]) == 12
        ), f"{len(self.new['currentPage'])} != {12}"
        assert (
            len(self.new["currentTitre"]) == 12
        ), f"{len(self.new['currentTitre'])} != {12}"
        assert (
            len(self.new["loadAnnotations"]) == 3
        ), f"{len(self.new['loadAnnotations'])} != { 3}"
        assert (
            len(self.new["addAnnotation"]) == 2
        ), f"{len(self.new['addAnnotation'])} != { 2}"
        assert (
            len(self.new["loadSection"]["annotations"]) == 3
        ), f"{len(self.new['loadSection']['annotations'])} != { 3}"
        assert self.new["loadAnnotations"] == [
            {
                "id": 1,
                "relativeX": 0.1,
                "relativeY": 0.2,
                "section": 1,
                "color": None,
                "classtype": "AnnotationText",
                "text": "un annotation",
                "underline": False,
            },
            {
                "id": 2,
                "relativeX": 0.5,
                "relativeY": 0.6,
                "section": 1,
                # "color": 4278222848,
                "color": "#008000",  # on triche pour le problème de serialisation de QColor
                "classtype": "Stabylo",
                "relativeWidth": 0.1,
                "relativeHeight": 0.2,
            },
            {
                "id": 3,
                "relativeX": 0.1,
                "relativeY": 0.4,
                "section": 1,
                "color": "#008000",  # on triche pour le problème de serialisation de QColor
                "classtype": "AnnotationText",
                "text": "un annotation",
                "underline": True,
            },
        ], self.new["loadAnnotations"]
        assert (
            len(self.new["recentsModel"]) == 12
        ), f"{len(self.new['recentsModel'])} != {12}"
        assert self.new["addSection"] == 5, self.new["addSection"]



    def write_fixtures(self):
        # init

        samples = {}

        # create samples
        for x in [
            self.activite,
            self.page,
            self.section,
            self.image_section,
            self.recents,
        ]:
            x()

        self.check_fixtures()

        def default_json(obj):
            if isinstance(obj, QUrl):
                return obj.toLocalFile()

        # write
        a = root / Path("tests/qml_tests/echantillon.js")
        a.write_text("var samples = ")
        with a.open("at") as f:
            json.dump(self.new, f, indent=2, default=default_json)


if __name__ == "__main__":
    root = Path(__file__).absolute().parents[2]
    sys.path.append(str(root / "src" / "main" / "python"))
    sys.path.append(str(Path(__file__).parent))
    import package.database

    package.database.db = package.database.init_database()

    a = CreateJs()
    a.write_fixtures()
