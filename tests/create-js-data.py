import sys
from pathlib import Path
import json
import inspect

root = Path(__file__).parents[1]
sys.path.append(str(root / "src" / "main" / "python"))
sys.path.append(str(Path(__file__).parent))

import package.database
package.database.db = package.database.init_database()


# def init():
    # modify python path
    # root = Path(__file__).parents[1]
    # sys.path.append(str(root / "src" / "main" / "python"))
    # sys.path.append(str(Path(__file__).parent))

    # Init database
    # import package.database
    #
    # package.database.db = package.database.init_database()

    # run qrc update
    # orig = root / "src" / "main" / "resources" / "qml.qrc"
    # dest = root / "src" / "main" / "python" / "qrc.py"
    # command = f"pyside2-rcc {orig.absolute()} -o {dest.absolute()}"
    # subprocess.run(command, cwd=root, shell=True)



    # return  package.database.db


def populate():
    from package.database.factory import populate_database

    populate_database()

def write_fixtures():
    # init
    from package.database_object import DatabaseObject
    dao = DatabaseObject(package.database.db)
    samples = {}

    # create samples
    for x in [page, matiere, activite]:
        samples.update(x(dao))


    # write
    a = Path('qml_tests/echantillon.js')
    with a.open("wt") as f:
        json.dump(samples, f, indent=2)
        f.seek(0)
        f.write("var sample =")
    # a.write_text(json.dumps(samples))

def page(dao):
    new = {}

    new["currentPage"] = []
    new["currentTitre"] = []
    for i in range(1, 10):
        setattr(dao, "currentPage", i)
        new["currentPage"].append(getattr(dao, 'currentPage'))
        new["currentTitre"].append(getattr(dao, 'currentTitre'))

    return new

def activite(dao):
    new = {}

    dao.currentMatiere = 1
    new["lessonsList"] = dao.lessonsList
    # new["currentTitre"] = []
    # for i in range(1, len(dao.matieresListNom) + 1):
    #     setattr(dao, "currentMatiere", i)))

    return new

def matiere( dao):
    new ={}

    new["getMatiereIndexFromId"] = {
        k: getattr(dao,"getMatiereIndexFromId")(k) for k in range(1,4)
    }

    new["currentMatiere"] = []
    for i in range(1, len(dao.matieresListNom)+1):
        setattr(dao,"currentMatiere", i)
        new["currentMatiere"].append(getattr(dao, 'currentMatiere'))

    new["matieresListNom"] = getattr(dao,'matieresListNom')

    return new

def run():
    # ddb = init()
    populate()
    write_fixtures()

if __name__ == '__main__':

    run()