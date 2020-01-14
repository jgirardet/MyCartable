from package.database_object import DatabaseObject
from package.database.factory import *

def create_matiere():
    f_matiere("un")
    f_matiere("deux")
    f_matiere("trois")
    f_matiere("quatre")

def test_init(ddb):
    a = DatabaseObject(ddb)
    assert a.db == ddb
    assert a._currentPage == {}
    assert a._currentMatiere == -1

def test_currentMatiere(database):
    create_matiere()
    a = DatabaseObject(database)
    assert a.currentMatiere == -1

    #from string
    a.setCurrentMatiereFromString('trois')
    assert a.currentMatiere == 3

    # from int
    a.currentMatiere = 2
    assert a.currentMatiere == 2
    a.currentMatiere = 2 #same
    assert a.currentMatiere == 2
    a.currentMatiere = "fez" #not in do nothing
    assert a.currentMatiere == 2

    #get index from id
    assert a.getMatiereIndexFromId(3) == 2

def test_matiereList(database):
    create_matiere()

    # listnom
    a = DatabaseObject(database)
    assert a.matieresListNom == ("un", "deux", "trois", "quatre")

    #refresh
    f_matiere("cinq")
    a.matieresListRefresh()
    assert a.matieresListNom == ("un", "deux", "trois", "quatre", "cinq")

def test_newPage(database):
    a = DatabaseObject(database)
    ac = f_activite()
    b = a.newPage(ac.id)
    assert b["activite"] == ac.id

def test_currentPage(database):
    a = f_page().to_dict()
    b = f_page().to_dict()
    c = DatabaseObject(database)
    assert c.currentPage == {}

    #setCurrentPage
    c.setCurrentPage(1)
    assert c.currentPage == a
    c.setCurrentPage(2)
    assert c.currentPage == b

    #
def test_getPagesByMatiereAndActivite(database):
    """à tester vi gui"""
    pass

