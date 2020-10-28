from pony.orm import Database, db_session

migrations_history = {"1.3.0": ['ALTER TABLE Annotation ADD "points" TEXT']}


def check_1_3_0(db: Database):
    with db_session:
        db.execute("select points from Annotation")
