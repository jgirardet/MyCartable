from pathlib import Path

from pdf2image import convert_from_path
import tempfile


def test_pdf():
    with tempfile.TemporaryDirectory() as path:
        pdf = Path(__file__).parent / "resources" / "2pages.pdf"
        assert pdf.is_file()
        res = convert_from_path(pdf, output_folder=path)
        for x in res:
            assert Path(x.filename).is_file()
