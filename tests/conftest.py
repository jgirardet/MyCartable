import io
import re
import sys
import time
from pathlib import Path

import pytest
from loguru import logger
from mimesis import Generic

root = Path(__file__).parents[1]
python_dir = root / "src"
sys.path.append(str(python_dir))

from mycartable.main import register_new_qml_type
from tests.common import setup_session

#
def pytest_sessionstart():
    setup_session()

    register_new_qml_type()


"""
Fixtures
"""

generic_mimesis = Generic("fr")

"""
Meta test
"""


@pytest.fixture(autouse=False)
def duree_test():
    debut = time.time()
    yield
    print(f"d={int((time.time()-debut)*1000)} ms")


"""
Fakers factory
"""


@pytest.fixture(scope="function")
def gen(request):
    """utilisation de generic mimesis"""
    return generic_mimesis


@pytest.fixture()
def png_annot(resources):
    return resources / "tst_AnnotableImage.png"


@pytest.fixture(scope="session")
def resources():
    """acces en lecture"""
    return Path(__file__).parent / "resources"


@pytest.fixture()
def new_res(tmp_path, resources):
    """pour acces en écriture"""

    def factory(name):
        file = name if isinstance(name, Path) else resources / name
        new_file = tmp_path / file.name
        new_file.write_bytes(file.read_bytes())
        return new_file

    return factory


@pytest.fixture(scope="function")
def tmpfile(request, tmp_path, gen):
    """tempfile which exists"""
    file = tmp_path / gen.file.file_name()
    file.touch()
    return file


@pytest.fixture(scope="function")
def tmpfilename(request, tmp_path, gen):
    """tempfile which does not exists"""
    return tmp_path / gen.file.file_name()


"""
Qt fixtures
"""


"""
Logging fixtures
"""


@pytest.fixture()
def caplogger():
    from loguru import logger

    class Ios(io.StringIO):
        def read(self, *args, **kwargs):
            self.seek(0)
            return super().read(*args, **kwargs)

        @property
        def records(self):
            res = []
            self.seek(0)
            for line in self.readlines():
                res.append(re.search(r"(.+)\|(.+)\|(.+$)", line).groups())
            return res

    log = Ios()
    logger.remove()
    lid = logger.add(log, level="DEBUG")

    yield log
    logger.remove(lid)
    logger.add(sys.stdout, level="WARNING")


@pytest.fixture(autouse=True, scope="session")
def loglevel_base():
    logger.remove()
    logger.add(sys.stdout, level="WARNING")
    yield


@pytest.fixture(scope="function")
def loglevel_debug():
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    yield
    logger.add(sys.stdout, level="WARNING")
