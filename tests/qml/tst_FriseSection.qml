import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 800
    height: 600

    CasTest {
        property var friseSection
        property var sec
        property var corps
        property QtObject zero
        property QtObject un
        property QtObject deux
        property var z1
        property var z0
        property var l0
        property var l1
        property Item zone0
        property Item zone1
        property Item zone2
        property Item leg0
        property Item leg1

        function initPre() {
            friseSection = fk.f("friseSection", {
                "height": 424,
                "titre": "ma frise"
            });
            z0 = fk.f("zoneFrise", {
                "frise": friseSection.id,
                "texte": "zone1",
                "ratio": 0.1,
                "separatorText": "-10 av JC",
                "style": {
                    "bgColor": "red"
                }
            });
            // on l'utilise en property pour le réutiliser
            z1 = fk.f("zoneFrise", {
                "frise": friseSection.id,
                "texte": "zone2",
                "ratio": 0.2,
                "style": {
                    "bgColor": "blue",
                    "strikeout": true
                }
            });
            let z2 = fk.f("zoneFrise", {
                "frise": friseSection.id,
                "texte": "zone3",
                "ratio": 0.3,
                "style": {
                    "bgColor": "green"
                }
            });
            // Création des légendes
            l0 = fk.f("friseLegende", {
                "zone": z2.id,
                "texte": "legende 0 gauche bas",
                "relativeX": 0.3,
                "side": false
            });
            l1 = fk.f("friseLegende", {
                "zone": z2.id,
                "texte": "legende 1 au droit haut",
                "relativeX": 0.7,
                "side": true
            });
            sec = th.getBridgeInstance(item, "FriseSection", friseSection.id);
            params = {
                "section": sec,
                "sectionItem": item
            };
        }

        function initPost() {
            corps = tested.corps;
            zero = corps.itemAtIndex(0);
            un = corps.itemAtIndex(1);
            deux = corps.itemAtIndex(2);
            corps.displaced.animations = [];
            zone0 = zero.zone;
            zone1 = un.zone;
            zone2 = deux.zone;
            if (zone2.legendeItems.get(0).legendeId === l0.id) {
                leg0 = zone2.legendeItems.get(0);
                leg1 = zone2.legendeItems.get(1);
            } else {
                leg0 = zone2.legendeItems.get(1);
                leg1 = zone2.legendeItems.get(0);
            }
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
            let new3 = corps.itemAtIndex(3);
            compare(new3.zone.texte.text, "new");
            fuzzyCompare(new3.zone.color, "lightgoldenrodyellow", 0);
            compare(new3.zone.legendeItems.get(0).x, new3.zone.width); // auto new legende created
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

        function test_color_dialog() {
            mouseClick(un.zone, 1, 1, Qt.RightButton);
            let cp = findChild(un, "colordialog");
            cp.contentItem.picked("purple");
            fuzzyCompare(un.zone.color, "purple", 0);
            fuzzyCompare(fk.getItem("ZoneFrise", z1.id).style.bgColor, "purple", 0);
        }

        function test_legende_init() {
            compare(leg1.state, "up");
            compare(leg1.y + leg1.languette.y, -10);
            compare(leg1.legende.text, "legende 1 au droit haut");
            compare(leg1.x, 147.7);
        }

        function test_legende_update() {
            // va en bas
            mouseWheel(leg0.legende, 1, 1, 0, -1);
            compare(leg0.y, leg0.parent.height);
            compare(leg0.legende.y, 10);
            compare(fk.getItem("FriseLegende", l0.id).side, false);
            // Va en haut
            mouseClick(leg0.legende);
            mouseWheel(leg0.legende, 1, 1, 0, 1);
            compare(leg0.y, 0);
            compare(leg0.languette.y, -10);
            compare(leg0.legende.y + leg0.legende.height, leg0.languette.y);
            compare(fk.getItem("FriseLegende", l0.id).side, true);
            //Text
            clickAndWrite(leg0.legende);
            compare(fk.getItem("FriseLegende", l0.id).texte, "bcd");
            // relative X
            mouseDrag(leg1.languette, 1, 1, 40, 0);
            fuzzyCompare(leg1.x, 187.0, 10); // 147+40
            fuzzyCompare(fk.getItem("FriseLegende", l1.id).relativeX, 187.0 / leg1.parent.width, 0.1);
        }

        function test_legende_ajout() {
            let zo1 = un.zone;
            let childs = zo1.children.length;
            mouseClick(un, 1, un.height);
            compare(fk.getItem("ZoneFrise", z1.id).legendes.length, 1);
            mouseClick(un, 10, un.height);
            compare(fk.getItem("ZoneFrise", z1.id).legendes.length, 2);
            compare(zo1.children.length, childs + 2);
            let last = zo1.children[zo1.children.length - 2]; // on décompte repeater
            compare(last.x, 10);
            verify(last.legende.activeFocus);
        }

        function test_legende_remove() {
            let rep = deux.zone.legendeItems;
            mouseClick(rep.get(0).legende, 1, 1, Qt.MiddleButton);
            compare(rep.count, 1);
        }

        function test_update_titre() {
            compare(tested.titre.text, "ma frise");
            clickAndWrite(tested.titre);
            compare(tested.titre.text, "bcd");
            compare(fk.getItem("FriseSection", friseSection.id).titre, "bcd");
        }

        testedNom: "qrc:/qml/sections/FriseSection.qml"
        name: "FriseSection"

        Item {
            id: parent100

            // dumy item with with 100, easier for relativeX
            width: 100
            height: 100
        }

    }

}
