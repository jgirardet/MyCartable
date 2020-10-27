import os
import pathlib
import tempfile


class CustomNamedTemporaryFile:
    """
    This custom implementation is needed because of the following limitation of tempfile.NamedTemporaryFile:

    > Whether the name can be used to open the file a second time, while the named temporary file is still open,
    > varies across platforms (it can be so used on Unix; it cannot on Windows NT or later).
    from : https://stackoverflow.com/questions/23212435/permission-denied-to-write-to-my-temporary-file
    """

    def __init__(self, mode="wb", delete=True):
        self._mode = mode
        self._delete = delete
        # Generate a random temporary file name
        file_name = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        # Ensure the file is created
        open(file_name, "x").close()

    def __enter__(self):
        # Open the file in the given mode
        self._tempFile = open(file_name, self._mode)
        return self._tempFile

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tempFile.close()
        if self._delete:
            os.remove(self._tempFile.name)


class Path(type(pathlib.Path())):
    @classmethod
    def tempfile(cls):
        return Path(os.path.join(tempfile.gettempdir(), os.urandom(24).hex()))

    def __init__(self):