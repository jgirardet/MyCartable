from collections import namedtuple
from PySide2.QtCore import QStandardPaths
from pathlib import Path

FamilleActivite = namedtuple("FamilleActivite", "index nom")

ACTIVITES = [
    FamilleActivite(0, "Lessons"),
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

ROOT_DATA = (
    Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / APPNAME
)
if not ROOT_DATA.is_dir():
    ROOT_DATA.mkdir(parents=True)

FILES = ROOT_DATA  / "files"
if not FILES.is_dir():
    FILES.mkdir(parents=True)