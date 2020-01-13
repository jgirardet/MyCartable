from pony.orm import db_session


class MatieresDispatcher:
    def __init__(self, db):
        self.db = db
        with db_session:
            self.query = self.db.Matiere.select().order_by(self.db.Matiere.id)
            self.nom_id = self.build_nom_id()
            self.id_nom = self.build_id_nom()
            self.id_index = self.build_id_index()

    def build_nom_id(self):
        return {p.nom: p.id for p in self.query}

    def build_id_nom(self):
        return {p.id: p.nom for p in self.query}

    def build_id_index(self):
        return {p.id: index for index, p in enumerate(self.query)}
