import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import "qrc:/qml/layouts"

Item {
    id: item

    width: 800
    height: 400

    Component {
        // dummy comp pour que le role splitComp ne fasse pas d'erreur
        id: nullcomp

        QtObject {
        }

    }

    Component {
        id: splitcomp

        SplitLayout {
            nullComp: nullcomp
            layouts: {
                "rect": {
                    "splittype": "rect",
                    "splittext": "rect",
                    "splitcomp": rect,
                    "spliturl": "",
                    "splitindex": 0
                },
                "vide": {
                    "splittype": "vide",
                    "splittext": "levide",
                    "spliturl": "qrc:/qml/layouts/VideLayout.qml",
                    "splitcomp": nullcomp,
                    "splitindex": 1
                }
            }
            initDataModel: ["rect"]

            Component {
                id: rect

                Rectangle {
                    anchors.fill: parent
                    color: "blue"
                }

            }

        }

    }

    CasTest {
        property QtObject fichier
        property Item hoributton
        property Item vertibutton
        property var lv
        property SplitLayout splitobj

        function initPre() {
            splitobj = splitcomp.createObject(item);
            params = {
                "mainItem": splitobj
            };
        }

        function initPost() {
            tryCompare(splitobj.get(0), "loaded", true);
            fichier = tested.contentItem.children[0].menus[0];
            hoributton = tested.contentItem.children[1];
            vertibutton = tested.contentItem.children[2];
            tested.heightAnimation.duration = 0;
            tested.hideTimer.interval = 0;
        }

        function test_fichier() {
            compare(fichier.title, "&Fichier");
            compare(fichier.itemAt(0).text, "&Changer d'année");
        }

        function test_changer_annee() {
            fk.resetDB();
            fk.f("annee", {
                "id": 2018,
                "niveau": "ce2"
            });
            fk.f("annee", {
                "id": 2019,
                "niveau": "cm1"
            });
            fichier.visible = true;
            var buttonMenu = fichier.itemAt(0);
            var changerAnnee = findChild(tested, "changerAnnee");
            compare(changerAnnee.opened, false);
            mouseClick(buttonMenu);
            compare(changerAnnee.opened, true);
            lv = changerAnnee.contentItem;
            compare(lv.count, 2); // model ok
            compare(lv.itemAtIndex(0).text, "mon année de ce2 en 2018/2019");
            compare(lv.itemAtIndex(1).text, "mon année de cm1 en 2019/2020");
            signalChecker(ddb, "changeAnnee", "mouseClick(lv.itemAtIndex(1))", [2019]);
            compare(changerAnnee.opened, false);
        }

        function test_change_matiere_reset_tout() {
            var spy = getSpy(ddb, "changeAnnee");
            ddb.currentMatiere = 4;
            fichier.visible = true;
            var dialog = findChild(tested, "changer_matieres");
            dialog.height = 300;
            var buttonMenu = fichier.itemAt(1);
            mouseClick(buttonMenu);
            tryCompare(dialog, "visible", true);
            dialog.close();
            spy.wait();
        }

        function test_showhide() {
            //mouse in and out
            compare(tested.height, 2);
            mouseMove(tested, 1, 1);
            compare(tested.height, 50);
            mouseMove(tested, -1, -1);
            compare(tested.height, 2);
            // don't hide if menu visible
            tested.state = "expanded";
            fichier.visible = true;
            compare(tested.height, 50);
            tested.hideTimer.start();
            compare(tested.height, 50);
        }

        function test_split_buttons() {
            // un seul
            compare(splitobj.count, 1);
            compare(splitobj.orientation, Qt.Horizontal);
            // hori
            mouseClick(hoributton);
            compare(splitobj.count, 2);
            compare(splitobj.orientation, Qt.Horizontal);
            // retour
            mouseClick(hoributton);
            compare(splitobj.count, 1);
            compare(splitobj.orientation, Qt.Horizontal);
            // verti
            mouseClick(vertibutton);
            compare(splitobj.count, 2);
            compare(splitobj.orientation, Qt.Vertical);
            // retour
            wait(1);
            //evite //QQmlContext: Cannot set context object on invalid context.vQQmlComponent: Cannot create a component in an invalid context
            mouseClick(vertibutton);
            compare(splitobj.count, 1);
            compare(splitobj.orientation, Qt.Vertical);
            // hori to verti
            mouseClick(hoributton);
            compare(splitobj.count, 2);
            compare(splitobj.orientation, Qt.Horizontal);
            mouseClick(vertibutton);
            compare(splitobj.count, 2);
            compare(splitobj.orientation, Qt.Vertical);
            // verti to hori
            mouseClick(hoributton);
            compare(splitobj.count, 2);
            compare(splitobj.orientation, Qt.Horizontal);
            // retour
            mouseClick(hoributton);
            compare(splitobj.count, 1);
            compare(splitobj.orientation, Qt.Horizontal);
        }

        name: "MainMenuBar"
        testedNom: "qrc:/qml/divers/MainMenuBar.qml"
        params: {
        }
    }

}
