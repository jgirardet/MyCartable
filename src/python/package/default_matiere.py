from PySide2.QtGui import QColor


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
    {"nom": "Langues", "id": 5, "bgColor": (0, SATURATION_BASE, VALUE_BASE)},  # Rouge
    {
        "nom": "Sciences",
        "id": 6,
        "bgColor": (30, SATURATION_BASE, VALUE_BASE),
    },  # orange
    {"nom": "Arts", "id": 7, "bgColor": (270, SATURATION_BASE, VALUE_BASE)},  # violet
    {"nom": "Divers", "id": 1, "bgColor": (110, SATURATION_BASE, VALUE_BASE)},  # vert
]


def build_matiere_groupe():
    groups = []
    for g in MATIERE_GROUPE_BASE:
        cop = {k: v for k, v in g.items() if k != "bgColor"}
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


def build_grouped_color():
    return {group["id"]: get_color_by_group(group) for group in MATIERE_GROUPE_BASE}


def build_matiere():
    res = []
    matieres_groupe = build_grouped_color()
    for m in MATIERES_BASE:
        group_id = m["groupe"]
        if group_id in matieres_groupe:
            nom = m["nom"]
            if nom in matieres_groupe[group_id]:
                res.append(matieres_groupe[group_id][nom])
        else:
            res.append(m)
    return res


MATIERES = MATIERES_BASE
MATIERES = build_matiere()
