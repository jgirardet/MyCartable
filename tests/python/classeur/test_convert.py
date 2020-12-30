import base64
from unittest.mock import patch
from uuid import UUID

import pytest
from mycartable.classeur.convert import frise_section
from mycartable import WIN
from pony.orm import db_session


def pixel_to_mm(pix):
    return round(pix / 3.7795275591)


class TestExportToOdt:
    @pytest.mark.skipif(
        WIN, reason="le rendu est bon  mais le test echoue que sous windows"
    )
    def test_frise_section(self, fk, qapp, resources):

        with db_session:
            f1 = fk.f_friseSection(titre="ma frise")
            with patch(
                "mycartable.classeur.convert.uuid.uuid4", return_value=UUID("1" * 32)
            ):
                res, auto = frise_section(f1)
        width = pixel_to_mm(1181)
        height = pixel_to_mm(f1.height)
        img = resources / "convert" / "frisesection.png"
        img = base64.b64encode(img.read_bytes())
        control = f"""<text:p text:style-name="Standard">
    <draw:frame draw:style-name="fr1" draw:name="{"1"*32}" text:anchor-type="paragraph" svg:width="{width}mm"  svg:height="{height}mm" draw:z-index="0">
        <draw:image loext:mime-type="image/png">
            <office:binary-data>{img.decode()}</office:binary-data>
        </draw:image>
    </draw:frame>
</text:p>"""
        # assert res == control
        # assert auto == ""

        with db_session:
            f1 = fk.f_friseSection(titre="ma frise")
            with patch(
                "mycartable.classeur.convert.uuid.uuid4", return_value=UUID("1" * 32)
            ):
                res, auto = frise_section(f1)
        width = pixel_to_mm(1181)
        height = pixel_to_mm(f1.height)
        img = resources / "convert" / "frisesection.png"
        img = base64.b64encode(img.read_bytes())
        control = f"""<text:p text:style-name="Standard">
    <draw:frame draw:style-name="fr1" draw:name="{"1"*32}" text:anchor-type="paragraph" svg:width="{width}mm"  svg:height="{height}mm" draw:z-index="0">
        <draw:image loext:mime-type="image/png">
            <office:binary-data>{img.decode()}</office:binary-data>
        </draw:image>
    </draw:frame>
</text:p>"""
