from collections import namedtuple

FamilleActivite = namedtuple("FamilleActivite", "index nom")

ACTIVITES = [
    FamilleActivite(0, "Leçons"),
    FamilleActivite(1, "Exercices"),
    FamilleActivite(2, "Evaluations"),
]

pageColumnWidthRatio = 2 / 3

preferredCentralWidth = 750
preferredSideWidth = preferredCentralWidth * pageColumnWidthRatio / 2
preferredHeaderHeight = 50
preferredActiviteHeight = 300

minimumSideWidth = preferredSideWidth / 2
minimumCentralWidth = minimumSideWidth * 3
minimumActiviteHeight = preferredActiviteHeight / 2

maximumSideWidth = preferredSideWidth


LAYOUT_SIZES = {
    "preferredCentralWidth": preferredCentralWidth,
    "preferredSideWidth": preferredSideWidth,
    "preferredHeaderHeight": preferredHeaderHeight,
    "preferredActiviteHeight": preferredActiviteHeight,
    "minimumSideWidth": minimumSideWidth,
    "minimumCentralWidth": minimumCentralWidth,
    "minimumActiviteHeight": minimumActiviteHeight,
    "maximumSideWidth": maximumSideWidth,
}


TITRE_TIMER_DELAY = 500

APPNAME = "MyCartable"
ORGNAME = "Cacahuete Coding"

BASE_FONT = "Verdana"
ANNOTATION_TEXT_BG_OPACITY = 0.5

MONOSPACED_FONTS = ["Liberation Mono", "Courier", "Courier New", "Noto Mono"]
