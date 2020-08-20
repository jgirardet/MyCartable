import PySide2
from package.default_matiere import build_matiere
from package.default_matiere import SATURATION_BASE, VALUE_BASE


def test_MATIERES():
    """test pas terrible, simple veille sanitaire pour le moment"""
    assert build_matiere(MATIERES_BASE, MATIERE_GROUPE_BASE) == res


# def test_get_degrade():


MATIERE_GROUPE_BASE = [
    {
        "nom": "Mathématiques",
        "id": 2,
        "bgColor": (300, SATURATION_BASE, VALUE_BASE),
    },  # fushia
    {
        "nom": "Français",
        "id": 3,
        "bgColor": (190, SATURATION_BASE, VALUE_BASE),
    },  # bleu foncé
    {
        "nom": "Histoire-Géo",
        "id": 4,
        "bgColor": (60, SATURATION_BASE, VALUE_BASE),
    },  # jaune
    {"nom": "Langues", "id": 5, "bgColor": (0, SATURATION_BASE, VALUE_BASE)},  # Rouge
    {
        "nom": "Sciences",
        "id": 6,
        "bgColor": (30, SATURATION_BASE, VALUE_BASE),
    },  # orange
    {"nom": "Arts", "id": 7, "bgColor": (270, SATURATION_BASE, VALUE_BASE)},  # violet
    {"nom": "Divers", "id": 1, "bgColor": (110, SATURATION_BASE, VALUE_BASE)},  # vert
]

MATIERES_BASE = [
    {"nom": "Orthographe", "groupe": 3},
    {"nom": "Grammaire", "groupe": 3},
    {"nom": "Conjugaison", "groupe": 3},
    {"nom": "Vocabulaire", "groupe": 3},
    {"nom": "Rédaction", "groupe": 3},
    {"nom": "Lecture", "groupe": 3},
    {"nom": "Mathématiques", "groupe": 2},
    {"nom": "Géométrie", "groupe": 2},
    {"nom": "Histoire", "groupe": 4},
    {"nom": "Géographie", "groupe": 4},
    {"nom": "Education civique", "groupe": 4},
    {"nom": "Anglais", "groupe": 5},
    {"nom": "Allemand", "groupe": 5},
    {"nom": "Espagnol", "groupe": 5},
    {"nom": "Physique", "groupe": 6},
    {"nom": "Chimie", "groupe": 6},
    {"nom": "Technologie", "groupe": 6},
    {"nom": "SVT", "groupe": 6},
    {"nom": "Musique", "groupe": 7},
    {"nom": "Poesie", "groupe": 7},
    {"nom": "Arts Plastiques", "groupe": 7},
    {"nom": "Divers", "groupe": 1},
]

res = [
    {
        "nom": "Orthographe",
        "groupe": 3,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.527778, 0.156863, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Grammaire",
        "groupe": 3,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.527778, 0.294118, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Conjugaison",
        "groupe": 3,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.527778, 0.431373, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Vocabulaire",
        "groupe": 3,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.527778, 0.568627, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Rédaction",
        "groupe": 3,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.527778, 0.705882, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Lecture",
        "groupe": 3,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.527778, 0.843137, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Mathématiques",
        "groupe": 2,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.833333, 0.156863, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Géométrie",
        "groupe": 2,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.833333, 0.576471, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Histoire",
        "groupe": 4,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.166667, 0.156863, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Géographie",
        "groupe": 4,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.166667, 0.435294, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Education civique",
        "groupe": 4,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.166667, 0.713725, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Anglais",
        "groupe": 5,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.000000, 0.156863, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Allemand",
        "groupe": 5,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.000000, 0.435294, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Espagnol",
        "groupe": 5,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.000000, 0.713725, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Physique",
        "groupe": 6,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.083333, 0.156863, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Chimie",
        "groupe": 6,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.083333, 0.364706, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Technologie",
        "groupe": 6,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.083333, 0.572549, 0.862745, 1.000000
        ),
    },
    {
        "nom": "SVT",
        "groupe": 6,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.083333, 0.780392, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Musique",
        "groupe": 7,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.750000, 0.156863, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Poesie",
        "groupe": 7,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.750000, 0.435294, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Arts Plastiques",
        "groupe": 7,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.750000, 0.713725, 0.862745, 1.000000
        ),
    },
    {
        "nom": "Divers",
        "groupe": 1,
        "bgColor": PySide2.QtGui.QColor.fromHsvF(
            0.305556, 0.156863, 0.862745, 1.000000
        ),
    },
]
