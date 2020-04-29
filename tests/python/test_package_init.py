# def test_get_binary_root(tmp_path):
#     if sys.platform == "linux":
#         assert get_binary_root() == Path(__file__).parents[1] / "binary" / "linux"
#     elif sys.platform == "win32":
#         assert get_binary_root() == Path(__file__).parents[1] / "binary" / "windows"
#
#     sys._MEIPASS = str(tmp_path)
#     sys.frozen = True
#     if sys.platform == "linux":
#         assert get_binary_root() == tmp_path / "binary" / "linux"
#     elif sys.platform == "win32":
#         assert get_binary_root() == tmp_path / "binary" / "windows"
#
#     del sys._MEIPASS
#     del sys.frozen
