import pytest
from fixtures import check_args
from mycartable.classeur.matiere import Matiere, MatieresDispatcher


class TestMatiere:
    def test_properties(self, fk):
        f = fk.f_matiere(td=True)
        m = Matiere(f)
        assert m.id == f["id"]
        assert m.nom == f["nom"]
        assert m.bgColor == f["bgColor"]
        assert m.fgColor == f["fgColor"]


class TestMatiereDispatcher:
    def test_check_args(self):
        md = MatieresDispatcher
        check_args(MatieresDispatcher.indexFromId, str, int)
        check_args(MatieresDispatcher.idFromIndex, int, int)
        check_args(MatieresDispatcher.getDeplacePageModel, None, list)

    def test_indexFromId(self, some_init_matiere):

        assert self.md.indexFromId(self.f0["id"]) == 0
        assert self.md.indexFromId(self.f1["id"]) == 1
        assert self.md.indexFromId(self.f2["id"]) == 2

    def test_IdfromIndex(self, some_init_matiere):
        # print(self.md.matieres_list_id)
        assert self.md.idFromIndex(0) == self.f0["id"]
        assert self.md.idFromIndex(1) == self.f1["id"]
        assert self.md.idFromIndex(2) == self.f2["id"]

    def test_matieresList(self, some_init_matiere):
        assert self.md.matieresList == [self.f0, self.f1, self.f2]

    def test_getDeplacePageModel(self, some_init_matiere, fk):
        a0 = fk.f_activite(matiere=self.f0["id"])
        a1 = fk.f_activite(matiere=self.f0["id"])
        assert self.md.getDeplacePageModel() == [
            {
                "activites": [
                    {"id": str(a0.id), "nom": a0.nom},
                    {"id": str(a1.id), "nom": a1.nom},
                ],
                "bgColor": self.f0["bgColor"],
                "nom": self.f0["nom"],
            },
            {
                "activites": [],
                "bgColor": self.f1["bgColor"],
                "nom": self.f1["nom"],
            },
            {
                "activites": [],
                "bgColor": self.f2["bgColor"],
                "nom": self.f2["nom"],
            },
        ]

    @pytest.fixture()
    def some_init_matiere(self, fk):
        self.g = fk.f_groupeMatiere(annee=2300)
        self.f0 = fk.f_matiere(td=True, groupe=self.g.id)
        self.f1 = fk.f_matiere(td=True, groupe=self.g.id)
        self.f2 = fk.f_matiere(td=True, groupe=self.g.id)
        self.md = MatieresDispatcher(fk.db, 2300)
