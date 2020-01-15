from pony.orm import db_session


class MatieresDispatcher:
    def __init__(self, db):
        self.db = db
        with db_session:
            self.query = self.db.Matiere.select().order_by(self.db.Matiere.id)
            self.nom_id = self._build_nom_id()
            self.id_nom = self._build_id_nom()
            self.id_index = self._build_id_index()
        self.matieres_list_nom = self._build_matieres_list_nom()
        self.matieres_list_id = self._build_matieres_list_id()

    def _build_nom_id(self):
        return {p.nom: p.id for p in self.query}

    def _build_id_nom(self):
        return {p.id: p.nom for p in self.query}

    def _build_id_index(self):
        return {p.id: index for index, p in enumerate(self.query)}

    def _build_matieres_list_nom(self):
        return tuple(self.nom_id.keys())

    def _build_matieres_list_id(self):
        return tuple(self.nom_id.values())

