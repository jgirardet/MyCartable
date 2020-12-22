from mycartable.default_configuration import DEFAUT_CONFIGURATION
from mycartable.main import update_configuration
from pony.orm import db_session


def test_update_configuration(ddbr):
    with db_session:  # reset config
        for k in ddbr.Configuration.select():
            k.delete()

    update_configuration(ddbr)
    with db_session:
        assert ddbr.Configuration.all() == DEFAUT_CONFIGURATION
