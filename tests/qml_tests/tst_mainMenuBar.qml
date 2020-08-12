import QtQuick 2.14

Item {
    id: item

    width: 200
    height: 200

    CasTest {
        //            compare(repeupler.opened, true);
        //            lv = changerAnnee.contentItem;
        //            compare(lv.count, 2); // model ok
        //            compare(lv.itemAtIndex(0).text, "mon année de ce2 en 2018/2019");
        //            compare(lv.itemAtIndex(1).text, "mon année de cm1 en 2019/2020");
        //            signalChecker(ddb, "changeAnnee", "mouseClick(lv.itemAtIndex(1))", [2019]);
        //            compare(changerAnnee.opened, false);
        //            compare(changerAnnee.opened, false);
        //            compare(repeupler.opened, true);
        //            repeupler.close();
        //            changerAnnee.close();
        // si un annee selectionne
        //            ddb.anneeActive = 2020;
        //            mouseClick(buttonMenu);

        property QtObject fichier
        property var lv

        function initPre() {
        }

        function initPost() {
            fichier = tested.menus[0];
        }

        function test_fichier() {
            compare(fichier.title, "&Fichier");
            compare(fichier.itemAt(0).text, "&Changer d'année");
        }

        function test_changer_annee() {
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

        function test_ajouter_matieres_sans_annee() {
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

        function test_ajouter_matieres() {
            fichier.visible = true;
            var buttonMenu = tested.menus[0].itemAt(1);
            var repeupler = findChild(tested, "repeupler");
            var changerAnnee = findChild(tested, "changerAnnee");
            ddb.anneeActive = 2050;
            compare(repeupler.opened, false);
            mouseClick(buttonMenu);
            compare(changerAnnee.opened, false);
            compare(repeupler.opened, true);
            repeupler.accept();
            compare(ddb._peuplerLesMatieresParDefault, [2050]);
        }

        name: "MainMenuBar"
        testedNom: "qrc:/qml/divers/MainMenuBar.qml"
        params: {
        }
    }

}
