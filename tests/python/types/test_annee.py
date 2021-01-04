from mycartable.types.annee import Annee


def test_init(qtbot):
    a = Annee.new(id=2345, niveau="aah")
    assert a.id == 2345
    assert a.niveau == "aah"
    with qtbot.waitSignal(a.niveauChanged):
        a.niveau = "EEE"
    assert a.niveau == "EEE"


def test_getMenuesAnnees(fk):
    for i in range(4):
        fk.f_annee(2016 - (i * i))
    a = Annee()
    assert a.getMenuAnnees() == [
        {"id": 2007, "niveau": "cm2007"},
        {"id": 2012, "niveau": "cm2012"},
        {"id": 2015, "niveau": "cm2015"},
        {"id": 2016, "niveau": "cm2016"},
    ]
