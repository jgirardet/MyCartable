from PyQt5.QtGui import QColor

# uniquement ajouté dans la DDB si n'existe pas déjà
DEFAUT_CONFIGURATION = {
    "preferredHeaderHeight": 50,
    "colorFond": QColor(130, 134, 138).name(),
    "fontMain": "Verdana",
    "lexiqueColumnWidth": 300,
}

# systématiquement remis à jours au démarrage
KEEP_UPDATED_CONFIGURATION = {
    "layouts": {
        "vide": {
            "splittype": "vide",
            "splittext": "",
            "splitindex": 0,
            "spliturl": "qrc:/qml/layouts/VideLayout.qml",
        },
        "classeur": {
            "splittype": "classeur",
            "splittext": "Classeur",
            "splitindex": 1,
            "spliturl": "qrc:/qml/layouts/ClasseurLayout.qml",
        },
        "lexique": {
            "splittype": "lexique",
            "splittext": "Lexique",
            "splitindex": 2,
            "spliturl": "qrc:/qml/lexique/LexiqueLayout.qml",
        },
    },
    "annotationDessinCurrentLineWidth": 3,
    "annotationDessinCurrentStrokeStyle": QColor("black").name(),
    "annotationDessinCurrentTool": "fillrect",
    "annotationCurrentTool": "text",
    "annotationCurrentTextSizeFactor": 15,
}
