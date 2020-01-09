from datetime import datetime

from package.database.factory import*
import pytest

pytestmark = pytest.mark.usefixtures("reset_db")

@db_session
def test_creation_all():
    an = f_annee()
    a= f_matiere(annee=an)
    f_section()




class TestSection:
    @db_session
    def test_modified(self, ddb):
        # insert
        avant = datetime.now()
        s= f_section(created=datetime.now())
        s.to_dict() #flush
        apres = datetime.now()
        assert avant <s.created <apres

        # update
        avant = datetime.now()
        s.content = "mkplkù lù pl"
        mod = s.to_dict()['modified']
        apres = datetime.now()

        assert   s.created < avant < mod< apres



class TestMatiere:
    @db_session
    def test_noms(self, ddb):
        assert ddb.Matiere.select()[:] ==[]
        f_matiere(nom="a")
        f_matiere(nom="b")
        f_matiere(nom="c")
        f_matiere(nom="d")
        f_matiere(nom="e")
        assert ddb.Matiere.noms() ==[{'id': 1, 'nom': 'a'}, {'id':2, 'nom': 'b'}, {'id': 3, 'nom': 'c'}, {'id': 4, 'nom': 'd'}, {'id': 5, 'nom': 'e'}]
