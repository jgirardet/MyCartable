from odf.opendocument import OpenDocumentText, load
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import P, H

doc = OpenDocumentText()

p_style = Style(name="p_style", family="paragraph")
p_text_prop = TextProperties(
    attributes={
        "fontname": "Verdana",
        "fontfamily": "Verdana",
        "fontstylename": "Normal",
        "fontpitch": "variable",
        "fontsize": "20pt",
    }
)
p_style.addElement(p_text_prop)
doc.styles.addElement(p_style)

# h1_style = Style(name="h1_style", family="paragraph")
h1_style = Style(
    name="h1_style",
    family="paragraph",
    parentstylename=p_style,
    defaultoutlinelevel="1",
)
h1_text_prop = TextProperties(
    attributes={
        # "fontname": "Verdana",
        # "fontfamily": "Verdana",
        # "fontstylename": "Normal",
        # "fontpitch": "variable",
        "fontsize": "36pt",
    }
)
h1_style.addElement(h1_text_prop)
doc.styles.addElement(h1_style)

intro = P(stylename=p_style)
intro.addText("coucou blabla")
doc.text.addElement(intro)

titre1 = H(stylename=h1_style, outlinelevel="1")
titre1.addText("titre 1")
doc.text.addElement(titre1)


doc.save("/home/jimmy/bla.odt")
