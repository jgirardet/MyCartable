import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 800
    height: 600

    CasTest {
        // le dragY est disabled
        //collé contre l'autre qui s'est replacé
        // collé après les autres
        //        function test_xx_right_border_drag() {
        //            wait(10000);
        //        }
        //        function test_wheldown() {
        //            let s = un.separator;
        //            compare(s.y, 0);
        //            compare(s.height, corps.height + s.rab);
        //            compare(s.legende.y, s.height + 10);
        //        }
        //            wait(10000);
        //            s.state = "up";
        //            wait(30000);

        property var corps
        property QtObject zero
        property QtObject un
        property QtObject deux
        property var z1
        property var z0

        function initPre() {
            fk.resetDB();
        }

        function initPreCreate() {
            let fr = fk.f("friseSection", {
                "height": 424,
                "titre": "ma frise"
            });
            z0 = fk.f("zoneFrise", {
                "frise": fr.id,
                "texte": "zone1",
                "ratio": 0.1,
                "separatorText": "-10 av JC",
                "style": {
                    "bgColor": "red"
                }
            });
            // on l'utilise en property pour le réutiliser
            z1 = fk.f("zoneFrise", {
                "frise": fr.id,
                "texte": "zone2",
                "ratio": 0.2,
                "style": {
                    "bgColor": "blue",
                    "strikeout": true
                }
            });
            let z2 = fk.f("zoneFrise", {
                "frise": fr.id,
                "texte": "zone3",
                "ratio": 0.3,
                "style": {
                    "bgColor": "green"
                }
            });
            params = {
                "sectionId": fr.id
            };
        }

        function initPost() {
            corps = tested.corps;
            zero = corps.itemAtIndex(0);
            un = corps.itemAtIndex(1);
            deux = corps.itemAtIndex(2);
            corps.displaced.animations = [];
        }

        //should pass without failing
        function test_init() {
            compare(tested.width, item.width);
            compare(tested.height, 424);
            compare(tested.titre.text, "ma frise");
        }

        function test_corps_init() {
            compare(corps.count, 3);
            compare(un.zone.texte.text, "zone2");
        }

        function test_add_zone() {
            mouseClick(corps, corps.width - 5, undefined);
            compare(corps.count, 4);
            compare(corps.itemAtIndex(3).zone.texte.text, "new");
            fuzzyCompare(corps.itemAtIndex(3).zone.color, "lightgoldenrodyellow", 0);
        }

        function test_move_zone_une_case() {
            mouseDrag(zero, zero.width / 2, zero.height - 10, zero.width, 15, Qt.LeftButton, Qt.NoModifier, 50);
            compare(zero.x, un.width); //collé contre l'autre qui s'est replacé
            compare(zero.y, 0); // dragY désactivé
        }

        function test_move_zone_a_fond() {
            mouseDrag(zero, zero.width / 2, zero.height - 10, zero.parent.width, 0, Qt.LeftButton, Qt.NoModifier, 50);
            compare(zero.x, un.width + deux.width); // collé après les autres
        }

        function test_editzone_text() {
            let t = un.zone.texte;
            mouseClick(t);
            keyClick(Qt.Key_End);
            keySequence(" ,a,b,c");
            compare(fk.getItem("ZoneFrise", z1.id).texte, "zone2 abc");
        }

        function test_remove_zone() {
            mousePress(un, undefined, undefined, Qt.MiddleButton, undefined);
            compare(corps.count, 2);
            tryCompare(deux, "x", zero.width);
        }

        function test_move_separator_change_ratio() {
            let prevWidth = zero.width;
            mouseDrag(zero.separator, 1, 1, 40, 0, Qt.LeftButton, Qt.NoModifier, 50);
            fuzzyCompare(zero.width, prevWidth + 40, 10);
            let ratio = zero.width / corps.width;
            fuzzyCompare(fk.getItem("ZoneFrise", z0.id).ratio, ratio, 0.001);
        }

        function test_separator_legende_up_down() {
            let s = zero.separator;
            compare(s.y, 0);
            compare(s.height, corps.height + s.rab);
            compare(s.legende.y, s.height + 10);
            mouseWheel(s, 1, 1, 0, 1);
            compare(s.y, -20);
            compare(s.legende.y, -10 - s.legende.height);
            compare(fk.getItem("ZoneFrise", z0.id).style.strikeout, true);
        }

        function test_color_dialog() {
            mouseClick(un.zone, 1, 1, Qt.RightButton);
            let cp = findChild(un, "colordialog");
            cp.contentItem.picked("purple");
            fuzzyCompare(un.zone.color, "purple", 0);
            fuzzyCompare(fk.getItem("ZoneFrise", z1.id).style.bgColor, "purple", 0);
        }

        function test_separator_position_text_modif() {
            let s = zero.separator;
            compare(s.legende.text, "-10 av JC");
            s.legende.text = "mais après Francis";
            compare(fk.getItem("ZoneFrise", z0.id).separatorText, "mais après Francis");
        }

        function test_se() {
        }

        params: {
        }
        testedNom: "qrc:/qml/sections/FriseSection.qml"
        name: "FriseSection"
    }

}
