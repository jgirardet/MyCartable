from PySide2.QtGui import QColor

"""
    Toute matiere appartient à un groupe, ce n'est pas négociable
"""

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

SATURATION_BASE = 40
VALUE_BASE = 220

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
    {"nom": "Langues", "id": 5, "bgColor": (0, SATURATION_BASE, VALUE_BASE),},  # Rouge
    {
        "nom": "Sciences",
        "id": 6,
        "bgColor": (30, SATURATION_BASE, VALUE_BASE),
    },  # orange
    {"nom": "Arts", "id": 7, "bgColor": (270, SATURATION_BASE, VALUE_BASE),},  # violet
    {"nom": "Divers", "id": 1, "bgColor": (110, SATURATION_BASE, VALUE_BASE),},  # vert
]


def build_matiere_groupe():
    groups = []
    for g in MATIERE_GROUPE_BASE:
        cop = {k: v for k, v in g.items()}  # if k != "bgColor"}
        cop["bgColor"] = QColor.fromHsv(*cop["bgColor"])
        groups.append(cop)

    return groups


MATIERE_GROUPE = build_matiere_groupe()


def get_color_by_group(groupe):
    matieres = {x["nom"]: x for x in MATIERES_BASE if x["groupe"] == groupe["id"]}
    bgColor = QColor.fromHsv(*groupe["bgColor"])
    ajout = (255 - bgColor.saturation()) / len(matieres)
    for v in matieres.values():
        v["bgColor"] = bgColor.toHsv()
        bgColor.setHsv(bgColor.hue(), bgColor.saturation() + ajout, bgColor.value())
    return matieres


def build_grouped_color(matiere_groupe_base):
    return {group["id"]: get_color_by_group(group) for group in matiere_groupe_base}


def build_matiere(matieres_base, matiere_groupe_base):
    res = []
    matieres_groupe = build_grouped_color(matiere_groupe_base)
    for m in matieres_base:
        group_id = m["groupe"]
        nom = m["nom"]
        res.append(matieres_groupe[group_id][nom])
    return res


MATIERES = build_matiere(MATIERES_BASE, MATIERE_GROUPE_BASE)
