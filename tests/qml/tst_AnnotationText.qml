import QtQuick 2.15
import "qrc:/qml/annotations"

FocusScope {
    id: item

    property Item model
    property var _move: null
    property var section: testcase.ref

    function move(dx, dy) {
        _move = [dx, dy];
    }

    width: 200 // important pout les tests
    height: 200 //important pour les tests
    focus: true

    CasTest {
        id: testcase

        property var annot
        property var annotobj
        property var ref
        property var page

        function initPre() {
            let img = fk.f("imageSection");
            annot = fk.f("annotationText", {
                "section": img.id,
                "text": "bla",
                "style": {
                    "bgColor": "blue",
                    "fgColor": "#000000",
                    "underline": true
                }
            });
            page = th.getBridgeInstance(item, "Page", img.page);
            ref = page.model.data(page.model.index(0, 0), th.getRole("SectionRole")); // 257:PageRole
            annotobj = ref.model.data(ref.model.index(0, 0), th.getRole("AnnotationRole")); //258:AnnotationRole
            params = {
                "annot": annotobj,
                "referent": item
            };
            annotobj.index = 0;
        }

        function test_initY() {
            compare(tested.pointSizeStep, 1);
            compare(tested.moveStep, 5);
            compare(tested.height, tested.contentHeight);
            compare(tested.width, tested.contentWidth + 5);
        }

        function test_focus() {
            verify(tested.activeFocus); // focus at init empty text
            item.focus = false;
            verify(!tested.focus);
            item.focus = true;
            verify(tested.focus);
        }

        function test_init_from_annot() {
            // at init
            compare(tested.color, "#000000");
            compare(tested.font.underline, true);
            compare(tested.text, "bla");
            fuzzyCompare(tested.background.color, "#0000FF", 0);
        }

        function test_font_size() {
            compare(tested.fontSizeFactor, 15); // value uiManager.annotationCurrentTextSizeFactor
            compare(tested.font.pixelSize, 13); // 200/15
            let annot2 = fk.f("annotationText", {
                "section": ref.id,
                "x": 0.4,
                "y": 0.2,
                "style": {
                    "pointSize": 3
                },
                "text": ""
            });
            let aannoott2 = th.getBridgeInstance(ref, "AnnotationText", annot2.id);
            var tested2 = createObj(testedNom, {
                "annot": aannoott2,
                "referent": item
            }, item);
            compare(tested2.fontSizeFactor, 3);
            compare(tested2.font.pixelSize, 66); // 200/3
            tested2.destroy(); // avoid warningbla
        }

        function test_background() {
            // color teste plus haut dans test_init_from_annot
            var bg = tested.background;
            // border
            item.focus = false;
            verify(Qt.colorEqual(bg.border.color, "transparent"));
            item.focus = true;
            verify(Qt.colorEqual(bg.border.color, "#21be2b"));
            compare(bg.opacity, ref.annotationTextBGOpacity);
        }

        function test_focus_changed_cursor_at_end() {
            tested.text = "12345678";
            tested.cursorPosition = 2;
            tested.focus = false;
            tested.focus = true;
            compare(tested.cursorPosition, 8);
        }

        function test_add_new_line() {
            tested.text = "";
            mouseClick(tested);
            keyClick(Qt.Key_A);
            keyClick(Qt.Key_Return);
            keyClick(Qt.Key_B);
            compare(tested.text, "a\nb");
        }

        function test_taille_du_texte() {
            // pointSize empty donc default  = annotationCurrentTextSizeFactor
            compare(tested.fontSizeFactor, annotobj.annotationCurrentTextSizeFactor);
            compare(tested.fontSizeFactor, annotobj.annotationCurrentTextSizeFactor);
        }

        function test_taille_du_text_fonction_taille_image() {
            var old = (item.height / annotobj.annotationCurrentTextSizeFactor) | 0;
            compare(tested.font.pixelSize, old);
            item.height = item.height * 2;
            tryCompare(tested.font, "pixelSize", old * 2);
        }

        function test_grossi__text() {
            var size = tested.font.pixelSize;
            compare(tested.fontSizeFactor, 15);
            tested.focus = true;
            keyClick(Qt.Key_Plus, Qt.ControlModifier);
            compare(tested.fontSizeFactor, 14);
            let modif = fk.getItem("AnnotationText", annot.id);
            compare(modif.style.pointSize, 14);
            verify(tested.font.pixelSize > size);
        }

        function test_diminue__text() {
            var size = tested.font.pixelSize;
            tested.focus = true;
            compare(tested.fontSizeFactor, 15);
            keyClick(Qt.Key_Minus, Qt.ControlModifier);
            compare(tested.fontSizeFactor, 16);
            let modif = fk.getItem("AnnotationText", annot.id);
            compare(modif.style.pointSize, 16);
            verify(tested.font.pixelSize < size);
        }

        function test_move_data() {
            return [{
                "key": Qt.Key_Left,
                "movex": -5,
                "movey": 0
            }, {
                "key": Qt.Key_Right,
                "movex": 5,
                "movey": 0
            }, {
                "key": Qt.Key_Up,
                "movex": 0,
                "movey": -5
            }, {
                "key": Qt.Key_Down,
                "movex": 0,
                "movey": 5
            }];
        }

        function test_move(data) {
            keyClick(data.key, Qt.ControlModifier);
            compare(item._move, [data.movex, data.movey]);
        }

        function test_on_textChanged() {
            clickAndWrite(tested);
            compare(dtb.getDB("AnnotationText", annot.id).text, "bcd");
        }

        function test_checkPointIsNotDraw() {
            verify(!tested.checkPointIsNotDraw(4, 5));
        }

        function test_undo_redo() {
            tested.cursorPosition = 3;
            keyClick(Qt.Key_X);
            compare(tested.cursorPosition, 4);
            compare(tested.text, "blax");
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 3);
            compare(tested.text, "bla");
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 4);
            compare(tested.text, "blax");
            keyClick(Qt.Key_Backspace);
            compare(tested.cursorPosition, 3);
            compare(tested.text, "bla");
            keySequence("ctrl+z");
            compare(tested.cursorPosition, 4);
            compare(tested.text, "blax");
            keySequence("ctrl+shift+z");
            compare(tested.cursorPosition, 3);
            compare(tested.text, "bla");
        }

        name: "AnnotationText"
        testedNom: "qrc:/qml/annotations/AnnotationText.qml"
    }

}
