"""
Ici sont expliquées les migrations chaque changement dans la ddb.
"""
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Union, Callable, List

from loguru import logger
from package.database.base_db import Schema, init_database, init_models, db_session
from package.database.models import schema_version
from package.utils import Version
from pony.orm import Database


class Migrator:
    """
    db: Database à migrer
    version: version cible
    migrations: pool de migrations
    """

    def __init__(self, db: Database, version: Version, migrations: dict):
        self.db = db
        self.version = version
        self.migrations = migrations
        self.schema = Schema(self.db)

    def select_migrations(self) -> List[str]:
        """
        Les migrations sont choisies si > à la version de la db et  <= à la version cible
        :returns la liste de str de migrations à effectuer
        """
        selected = []
        schema_v = self.schema.version
        for ver, migs in self.migrations.items():
            version = Version(ver)
            if schema_v < version <= self.version:
                selected += migs
        return selected

    def process_one(self, line: str):
        with db_session(self.db) as db:
            db.execute(line)

    def process_migrations(self, mig_list: list):
        for mig in mig_list:
            self.process_one(mig)

    def apply_version(self):
        """
        Apply the targetted version
        :return:
        """
        self.schema.version = self.version

    def __call__(self):
        migrations = self.select_migrations()
        self.process_migrations(migrations)
        self.apply_version()


class MakeMigrations:
    def __init__(
        self,
        filename: Union[str, Path],  # chemin vers la ddb
        actual_version: Union[
            Version, str
        ] = None,  # version actuelle (dans les sources)
        migrations: dict = None,  # pool de migrations
    ):
        # migrations = migrations
        self.actual_version = (
            actual_version
            if isinstance(actual_version, Version)
            else Version(actual_version)
        )

        self.old_file = Path(filename)  # ddb à faire migrer

        # création d'une base temporaire pour effectuer les migrations
        # _, tmp = tempfile.mkstemp(suffix=".sqlite")
        tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        tmp.close()
        self.tmp_file = Path(tmp.name)
        shutil.copy(self.old_file, self.tmp_file)  # duplication de la DDB

        # outils pour migrations
        self.tmp_db = Database(provider="sqlite", filename=tmp.name)
        self.schema = Schema(file=self.tmp_db)
        self.migrator = Migrator(self.tmp_db, self.actual_version, migrations)
        logger.info(
            f"starting migrations from version {self.schema.version} to {self.actual_version}"
        )

    def make_migrations(self):
        self.migrator()

    def check_migrations(self, check_cb: Callable) -> bool:
        """
        Check migration with cb.
        Test are done on another Database
        :return: True if success
        """
        if not check_cb:
            return True
        logger.info("Checking migrations...")
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        shutil.copy(self.tmp_file, f.name)
        check_db = Database(provider="sqlite", filename=f.name)
        res = check_cb(check_db)
        check_db.disconnect()  # sinon unlink fail on windows
        os.unlink(f.name)
        return res

    def generate_new_mapping(self, generate_cb: Callable):
        """
        Generate new mapping using pony models, and apply some more migrations.
        On compte sur exceptions en cas d'erreur
        """
        if not generate_cb:
            return
        logger.info("Generating new mapping...")
        generate_cb(self.tmp_db)
        self.tmp_db.generate_mapping(create_tables=True)
        self.tmp_db.disconnect()

    def _backup_name(self):

        old_schema = Schema(file=self.old_file)
        backup_name = (
            f"mycartable_backup-from_{old_schema.version}"
            f"-to_{self.actual_version}-{datetime.now().isoformat().replace(':','_')}"
        )
        return backup_name

    def backup_old(self):
        backup_file = self.old_file.parent / self._backup_name()
        shutil.copy(self.old_file, backup_file)
        return backup_file

    def move_tmp_to_old(self):
        self.tmp_file.replace(self.old_file)

    def restore_backup(self, backup_file: Path):
        fail_name = backup_file.name.replace("backup", "failed_migrate")
        if self.old_file.is_file():
            self.old_file.replace(self.old_file.parent / fail_name)
        backup_file.replace(self.old_file)

    def __call__(self, check_cb: Callable = None, generate_cb: Callable = None) -> bool:
        """
        check_cb: voir check_migrations
        generate_db: voir generate_new_mapping
        - on fait la sauvegarde
        - réalisation les migrations sur la base temporaire
        - on vérifie que les données sont compatible avec les schema des sources
        - on remplace l'ancienne par la nouvelle

        :return: True sinon False
        """
        backup_file = self.backup_old()

        try:
            self.make_migrations()
            self.generate_new_mapping(generate_cb)
            self.check_migrations(check_cb)
            self.move_tmp_to_old()

        except Exception as err:
            logger.exception(err)
            self.restore_backup(backup_file)
            return False
        return True
