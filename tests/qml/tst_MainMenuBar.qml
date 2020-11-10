import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        property QtObject fichier
        property var lv

        function initPre() {
        }

        function initPost() {
            fichier = tested.menus[0];
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
            var buttonMenu = tested.menus[0].itemAt(0);
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
            var buttonMenu = tested.menus[0].itemAt(2);
            mouseClick(buttonMenu);
            tryCompare(dialog, "visible", true);
            dialog.close();
            spy.wait();
        }

        function test_ajouter_matieres() {
            fichier.visible = true;
            var buttonMenu = tested.menus[0].itemAt(1);
            var repeupler = findChild(tested, "repeupler");
            var changerAnnee = findChild(tested, "changerAnnee");
            ddb.anneeActive = 2019;
            compare(repeupler.opened, false);
            mouseClick(buttonMenu);
            compare(changerAnnee.opened, false);
            compare(repeupler.opened, true);
            let spy = getSpy(ddb, "changeMatieres");
            repeupler.accept(); // émis par chargeMatireParDefault
            spy.wait();
        }

        function test_ajouter_matieres_sans_annee() {
            ddb.anneeActive = 0;
            fichier.visible = true;
            var buttonMenu = tested.menus[0].itemAt(1);
            var repeupler = findChild(tested, "repeupler");
            var changerAnnee = findChild(tested, "changerAnnee");
            // si pas d'année selectionnée
            compare(repeupler.opened, false);
            mouseClick(buttonMenu);
            compare(changerAnnee.opened, true);
            compare(repeupler.opened, true);
            repeupler.close();
            changerAnnee.close();
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
            tested.menus[0].visible = true;
            compare(tested.height, 50);
            tested.hideTimer.start();
            compare(tested.height, 50);
        }

        name: "MainMenuBar"
        testedNom: "qrc:/qml/divers/MainMenuBar.qml"
        params: {
        }
    }

}
