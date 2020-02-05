import sys
from datetime import datetime
from pathlib import Path
import json

from pony.orm import db_session

MAT = ["Math", "Français", "Histoire", "Anglais"]


class CreateJs:
    def __init__(self):
        self.new = {}
        self.populate()
        from package.database_object import DatabaseObject

        self.dao = DatabaseObject(package.database.db)

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

        self.annee = f_annee(niveau="ce1")
        self.matieres = [f_matiere(x, self.annee.id) for x in MAT]
        math = self.matieres[0]
        with db_session:
            self.activites = math.activites.select()[:]
        self.pages = [
            f_page(
                activite=p.id,
                titre=f"letitre {p.famille} {i}",
                created=datetime.utcnow(),
            )
            for i in range(4)
            for p in self.activites
        ]

        self.la_page = self.pages[0]
        self.image_sections = [f_imageSection(page=self.la_page.id) for i in range(4)]
        self.la_image_section = self.image_sections[0]
        self.la_annotationText = f_annotationText(
            0.1, 0.2, "un annotation", section=self.la_image_section.id
        )
        self.le_stabylo = f_stabylo(
            0.1, 0.2, 0.3, 0.4, section=self.la_image_section.id
        )

    def matiere(self):

        self.new["getMatiereIndexFromId"] = {
            "id" + str(k): getattr(self.dao, "getMatiereIndexFromId")(k)
            for k in range(1, len(MAT))
        }

        self.new["currentMatiere"] = []
        for i in range(1, len(self.dao.matieresListNom) + 1):
            setattr(self.dao, "currentMatiere", i)
            self.new["currentMatiere"].append(getattr(self.dao, "currentMatiere"))

        self.new["matieresListNom"] = getattr(self.dao, "matieresListNom")

    def activite(self):

        self.dao.currentMatiere = 1
        self.new["lessonsList"] = self.dao.lessonsList
        self.new["exercicesList"] = self.dao.exercicesList
        self.new["evaluationsList"] = self.dao.evaluationsList
        # self.new["currentTitre"] = []
        # for i in range(1, len(self.dao.matieresListNom) + 1):
        #     setattr(self.dao, "currentMatiere", i)))

    def page(self):

        self.new["currentPage"] = []
        self.new["currentTitre"] = []
        for i in self.pages:
            setattr(self.dao, "currentPage", i.id)
            self.new["currentPage"].append(getattr(self.dao, "currentPage"))
            self.new["currentTitre"].append(getattr(self.dao, "currentTitre"))

    def image_section(self):

        self.new["loadAnnotations"] = self.dao.loadAnnotations(self.la_image_section.id)

        # doit retourner 3 et 4 si seulement 2 fabriquées dans populate
        self.new["addAnnotation"] = {
            x["classtype"]: self.dao.addAnnotation(x)
            for x in [
                {
                    "classtype": "Stabylo",
                    "section": 1.0,
                    "relativeX": 0.3,
                    "relativeY": 0.4,
                    "relativeWidth": 0.5,
                    "relativeHeight": 0.6,
                },
                {
                    "classtype": "AnnotationText",
                    "section": 1.0,
                    "relativeX": 0.3,
                    "relativeY": 0.4,
                    "text": "",
                },
            ]
        }

    def section(self):
        self.new["loadSection"] = self.dao.loadSection(self.la_image_section.id)

    def recents(self):
        self.new["recentsModel"] = self.dao.recentsModel

    def check_fixtures(self):
        assert (
            len(self.new["getMatiereIndexFromId"]) == 3
        ), f"{len(self.new['getMatiereIndexFromId'])} != { 3}"
        assert (
            len(self.new["currentMatiere"]) == 4
        ), f"{len(self.new['currentMatiere'])} != { 4}"
        assert (
            len(self.new["matieresListNom"]) == 4
        ), f"{len(self.new['matieresListNom'])} != { 4}"
        assert (
            len(self.new["lessonsList"]) == 4
        ), f"{len(self.new['lessonsList'])} != { 4}"
        assert (
            len(self.new["exercicesList"]) == 4
        ), f"{len(self.new['exercicesList'])} != { 4}"
        assert (
            len(self.new["evaluationsList"]) == 4
        ), f"{len(self.new['evaluationsList'])} != { 4}"
        assert (
            len(self.new["currentPage"]) == 12
        ), f"{len(self.new['currentPage'])} != {12}"
        assert (
            len(self.new["currentTitre"]) == 12
        ), f"{len(self.new['currentTitre'])} != {12}"
        assert (
            len(self.new["loadAnnotations"]) == 2
        ), f"{len(self.new['loadAnnotations'])} != { 2}"
        assert (
            len(self.new["addAnnotation"]) == 2
        ), f"{len(self.new['addAnnotation'])} != { 2}"
        assert (
            len(self.new["loadSection"]["annotations"]) == 2
        ), f"{len(self.new['loadSection']['annotations'])} != { 2}"
        assert self.new["loadAnnotations"] == [
            {
                "id": 1,
                "relativeX": 0.1,
                "relativeY": 0.2,
                "section": 1,
                "classtype": "AnnotationText",
                "text": "un annotation",
            },
            {
                "id": 2,
                "relativeX": 0.1,
                "relativeY": 0.2,
                "section": 1,
                "classtype": "Stabylo",
                "relativeWidth": 0.3,
                "relativeHeight": 0.4,
            },
        ]
        assert (
            len(self.new["recentsModel"]) == 12
        ), f"{len(self.new['recentsModel'])} != {12}"

    def write_fixtures(self):
        # init

        samples = {}

        # create samples
        for x in [
            self.matiere,
            self.activite,
            self.page,
            self.section,
            self.image_section,
            self.recents,
        ]:
            x()

        self.check_fixtures()

        # write
        a = root / Path("tests/qml_tests/echantillon.js")
        a.write_text("var samples = ")
        with a.open("at") as f:
            json.dump(self.new, f, indent=2)


if __name__ == "__main__":
    root = Path(__file__).absolute().parents[2]
    sys.path.append(str(root / "src" / "main" / "python"))
    sys.path.append(str(Path(__file__).parent))
    import package.database

    package.database.db = package.database.init_database()

    a = CreateJs()
    a.write_fixtures()
