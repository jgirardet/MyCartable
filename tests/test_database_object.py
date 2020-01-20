# from fixtures import compare
# from package.database_object import DatabaseObject
# from package.database.factory import *
#
# def create_matiere():
#     f_matiere("un")
#     f_matiere("deux")
#     f_matiere("trois")
#     f_matiere("quatre")
#
# def test_init(ddb):
#     a = DatabaseObject(ddb)
#     assert a.db == ddb
#     assert a._currentPage == {}
#     assert a._currentMatiere == -1
#
# def test_currentMatiere(ddbr):
#     create_matiere()
#     a = DatabaseObject(ddbr)
#     assert a.currentMatiere == -1
#
#     #from string
#     a.setCurrentMatiereFromString('trois')
#     assert a.currentMatiere == 3
#
#     # from int
#     a.currentMatiere = 2
#     assert a.currentMatiere == 2
#     a.currentMatiere = 2 #same
#     assert a.currentMatiere == 2
#     a.currentMatiere = "fez" #not in do nothing
#     assert a.currentMatiere == 2
#
#     #get index from id
#     assert a.getMatiereIndexFromId(3) == 2
#
# def test_matiereList(ddbr):
#     create_matiere()
#
#     # listnom
#     a = DatabaseObject(ddbr)
#     assert a.matieresListNom == ("un", "deux", "trois", "quatre")
#
#     #refresh
#     f_matiere("cinq")
#     a.matieresListRefresh()
#     assert a.matieresListNom == ("un", "deux", "trois", "quatre", "cinq")
#
# def test_newPage(ddbr):
#     a = DatabaseObject(ddbr)
#     ac = f_activite()
#     b = a.newPage(ac.id)
#     assert b["activite"] == ac.id
#
# def test_currentPage(ddbr):
#     a = f_page().to_dict()
#     b = f_page().to_dict()
#     c = DatabaseObject(ddbr)
#     assert c.currentPage == {}
#
#     #setCurrentPage
#     c.setCurrentPage(1)
#     assert c.currentPage == a
#     c.setCurrentPage(2)
#     assert c.currentPage == b
#
#     #
# def test_getPagesByMatiereAndActivite(ddbr):
#     """à tester vi gui"""
#     a = f_matiere()
#     with db_session:
#         act = [f_activite(matiere=a.id).to_dict() for p in range(2)]
#         pages = [f_page(activite=act[0]['id']).to_dict() for p in range(5) ]
#     c = DatabaseObject(ddbr)
#     #standard use case
#     assert compare(c.getPagesByMatiereAndActivite(a.nom, act[0]['famille']), pages)
#
#
