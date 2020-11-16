import QtQuick 2.15

Item {
    id: item

    width: 600
    height: 600

    CasTest {
        property var zero
        property var un
        property var deux
        property var six
        property var activite0
        property var activite1
        property var activite2
        property var changeactivite0
        property var changeactivite1
        property var changematiere0
        property var mat0
        property var mat1

        function initPre() {
            let math = fk.f("groupeMatiere", {
                "nom": "Mathématiques",
                "annee": 2019,
                "fgColor": "black",
                "bgColor": "red"
            });
            let fra = fk.f("groupeMatiere", {
                "nom": "Francais",
                "annee": 2019,
                "fgColor": "black",
                "bgColor": "blue"
            });
            let geo = fk.f("groupeMatiere", {
                "nom": "Histoire-Géo",
                "annee": 2019,
                "fgColor": "black",
                "bgColor": "green"
            });
            let phy = fk.f("matiere", {
                "groupe": math.id,
                "nom": 'Physique',
                "fgColor": "red",
                "bgColor": "blue"
            });
            let chimie = fk.f("matiere", {
                "groupe": math.id,
                "nom": 'Chimie',
                "fgColor": "red",
                "bgColor": "yellow"
            });
            let techno = fk.f("matiere", {
                "groupe": math.id,
                "nom": 'Technologie',
                "fgColor": "red",
                "bgColor": "orange"
            });
            let ac1 = fk.f("activite", {
                "matiere": phy.id,
                "nom": "act1"
            });
            let ac2 = fk.f("activite", {
                "matiere": phy.id,
                "nom": "act2"
            });
            let ac3 = fk.f("activite", {
                "matiere": phy.id,
                "nom": "act3"
            });
            fk.f("page", {
                "activite": ac2.id
            });
            fk.f("page", {
                "activite": ac3.id
            });
            fk.f("page", {
                "activite": ac3.id
            });
            params = {
                "annee": 2019
            };
        }

        function initPost() {
            tested.height = item.height;
            wait(50);
            zero = tested.itemAtIndex(0);
            un = tested.itemAtIndex(1);
            deux = tested.itemAtIndex(2);
            six = tested.itemAtIndex(6);
            changematiere0 = zero.changematiere;
            mat0 = changematiere0.itemAtIndex(0);
            mat1 = changematiere0.itemAtIndex(1);
            changeactivite0 = changematiere0.itemAtIndex(0).children[1];
            //            wait(3000);
            changeactivite1 = changematiere0.itemAtIndex(1).children[1];
            activite0 = changeactivite0.repeater.itemAt(0);
            activite1 = changeactivite0.repeater.itemAt(1);
            activite2 = changeactivite0.repeater.itemAt(2);
        }

        function test_init() {
        }

        function test_ddb_properties() {
            compare(un.text.text, "Francais");
            compare(deux.text.text, "Histoire-Géo");
            fuzzyCompare(un.baseColor, "blue", 0);
            var rect = un.colorbutton;
            fuzzyCompare(rect.gradient.stops[0].color, "blue", 0);
            verify(Qt.colorEqual(un.text.background.gradient.stops[0].color, "blue"));
        }

        function test_baseColorbindings() {
            un.baseColor = "yellow";
            fuzzyCompare(un.text.background.gradient.stops[0].color, "yellow", 0);
            fuzzyCompare(un.colorbutton.gradient.stops[0].color, "yellow", 0);
        }

        function test_change_gradient_color_reject() {
            var rect = un.colorbutton;
            mouseClick(rect);
            fuzzyCompare(tested.colordialog.currentColor, "blue", 0);
            tested.colordialog.currentColor = "purple";
            tested.colordialog.close();
            fuzzyCompare(un.baseColor, "blue", 0);
        }

        function test_change_gradient_color_accept() {
            var rect = un.colorbutton;
            mouseClick(rect);
            tested.colordialog.currentColor = "purple";
            tested.colordialog.accept();
            fuzzyCompare(un.baseColor, "purple", 0);
        }

        function test_moddif_nom_groupe() {
            un.text.text = "blabla";
            compare(un.nom, "blabla");
            compare(fk.getItem("GroupeMatiere", un.groupeid).nom, "blabla");
        }

        function test_moddif_nom_groupe_empty() {
            un.text.text = "a";
            compare(un.nom, "a");
            un.text.text = "";
            compare(un.nom, "a");
        }

        function test_up_groupe() {
            //check enabled properties of button
            compare(zero.children[0].children[1].enabled, false);
            compare(un.children[0].children[1].enabled, true);
            mouseClick(un.children[0].children[1]);
            let res = tested.itemAtIndex(0);
            compare(res.nom, "Francais");
            compare(fk.getItem("GroupeMatiere", res.groupeid).position, 0);
        }

        function test_down_groupe() {
            compare(un.children[0].children[2].enabled, true);
            compare(deux.children[0].children[2].enabled, false);
            mouseClick(un.children[0].children[2]);
            compare(tested.itemAtIndex(1).nom, "Histoire-Géo");
            compare(tested.itemAtIndex(2).nom, "Francais");
        }

        function test_add_groupe() {
            mouseClick(un.children[0].children[3]);
            //            wait(10000);
            compare(tested.model.length, 4);
            compare(tested.itemAtIndex(1).nom, "nouveau");
        }

        function test_add_groupe_if_empty_groupe() {
            var but = findChild(tested, "initgroupeButton");
            verify(!but.visible);
            tested.model = [];
            verify(but.visible);
            fk.f("annee", {
                "id": 1234
            });
            tested.annee = 1234;
            mouseClick(but);
            compare(tested.model.length, 1);
            compare(tested.itemAtIndex(0).nom, "nouveau groupe");
        }

        function test_remove_groupe() {
            compare(zero.children[0].children[4].enabled, false);
            compare(un.children[0].children[4].enabled, true);
            compare(deux.children[0].children[4].enabled, true);
            mouseClick(un.children[0].children[4]);
            compare(tested.count, 2);
            compare(tested.itemAtIndex(0).nom, "Mathématiques");
            compare(tested.itemAtIndex(1).nom, "Histoire-Géo");
        }

        function test_groupe_add_matiere_quand_empty() {
            compare(un.changematiere.count, 0);
            var button = un.text.children[3];
            compare(button.enabled, true);
            mouseClick(button);
            compare(button.enabled, false);
            compare(un.changematiere.itemAtIndex(0).nom, "nouvelle");
        }

        // " COIN DES MATIERES
        function test_ChangeMAtiereProperties() {
            var mat0 = changematiere0.itemAtIndex(0).children[0];
            compare(mat0.children[0].text, "Physique");
            fuzzyCompare(mat0.children[0].background.color, "blue", 0);
            compare(mat0.children[1].text, "3 rubriques\n3 pages");
        }

        function test_moddif_nom_matiere() {
            //            var mat0 = changematiere0.itemAtIndex(0)
            mat0.matieretexte.text = "blabla";
            compare(fk.getItem("Matiere", mat0.matiereid).nom, "blabla");
            compare(mat0.nom, "blabla");
        }

        function test_moddif_nom_matiere_mepty() {
            var mat0 = changematiere0.itemAtIndex(0).children[0];
            mat0.children[0].text = "a";
            mat0.children[0].text = "";
            compare(mat0.parent.nom, "a");
        }

        function test_matiere_toggle_base() {
            var tog = mat0.children[0].children[2];
            compare(tog.state, "");
            compare(tog.icon.source, "qrc:/icons/less-than");
        }

        function test_matiere_toggle_no_activite() {
            changeactivite0.model = 0;
            var tog = mat0.children[0].children[2];
            compare(tog.state, "no_activite");
        }

        function test_matiere_toggle_click() {
            var tog = mat0.children[0].children[2];
            mouseClick(tog);
            tryCompare(tog, "rotation", -90);
        }

        function test_matiere_toggle_click_empty_activite() {
            var tog = mat1.children[0].children[2];
            mouseClick(tog);
            tryCompare(tog, "rotation", -90);
            tryCompare(changeactivite1.children[0], "nom", "nouvelle");
            tryCompare(changeactivite1.children[0].activitetext, "selectedText", "nouvelle");
            tog.state = "toggled";
        }

        function test_up_matiere() {
            mouseClick(mat1.children[0].children[3]);
            var cm = changematiere0;
            let res = changematiere0.itemAtIndex(0);
            compare(res.nom, "Chimie");
            compare(fk.getItem("Matiere", res.matiereid).position, 0);
        }

        function test_down_matiere() {
            mouseClick(mat1.children[0].children[4], 1, 1);
            compare(changematiere0.itemAtIndex(2).nom, "Chimie");
        }

        function test_add_matiere() {
            mouseClick(mat0.children[0].children[5]);
            var newmate0 = changematiere0.itemAtIndex(0);
            compare(newmate0.matieretexte.selectedText, "nouvelle");
            compare(newmate0.matieretexte.activeFocus, true);
        }

        function test_remove_matiere() {
            mouseClick(mat1.children[0].children[6]);
            compare(changematiere0.count, 2);
            compare(changematiere0.itemAtIndex(0).nom, "Physique");
            compare(changematiere0.itemAtIndex(1).nom, "Technologie");
        }

        function test_remove_matiere_disabled_reste_des_pages() {
            compare(mat0.children[0].children[6].enabled, false);
        }

        //" RAyon des activites"
        function test_activites_properties() {
            compare(activite0.nom, "act1");
            compare(activite0.children[0].text, "act1"); // nmo
            compare(activite0.children[1].text, "0 page "); // nb page
            compare(activite1.children[1].text, "1 page ");
            compare(activite2.children[1].text, "2 pages");
            compare(activite0.children[2].enabled, false); // up button
            compare(activite1.children[2].enabled, true);
            compare(activite2.children[2].enabled, true);
            compare(activite0.children[3].enabled, true); // downbutton
            compare(activite1.children[3].enabled, true);
            compare(activite2.children[3].enabled, false);
            compare(activite0.children[5].enabled, true); // ermovebutton
            compare(activite1.children[5].enabled, false);
            compare(activite2.children[5].enabled, false);
        }

        function test_changeactivite_states() {
            compare(changeactivite0.state, "hidden");
            compare(changeactivite0.height, 0);
            compare(changeactivite0.opacity, 0);
            changeactivite0.state = "visible";
            tryCompare(changeactivite0.transitions[0], "running", false);
            compare(changeactivite0.height, changeactivite0.childrenRect.height);
            compare(changeactivite0.opacity, 1);
        }

        function test_up_activite() {
            changeactivite0.state = "visible";
            tryCompare(changeactivite0.transitions[0], "running", false);
            mouseClick(activite1.children[2]);
            let res = changeactivite0.repeater.itemAt(0);
            compare(res.nom, "act2");
            compare(fk.getItem("Activite", res.activiteId).position, 0);
        }

        function test_down_activite() {
            changeactivite0.state = "visible";
            tryCompare(changeactivite0.transitions[0], "running", false);
            mouseClick(activite0.children[3]);
            compare(changeactivite0.repeater.itemAt(1).nom, "act1");
        }

        function test_add_activite() {
            changeactivite0.state = "visible";
            tryCompare(changeactivite0.transitions[0], "running", false);
            mouseClick(activite0.children[4]);
            let rep = changeactivite0.repeater;
            compare(rep.count, 4);
            compare(rep.itemAt(0).nom, "nouvelle");
        }

        function test_remove_activite() {
            changeactivite0.state = "visible";
            tryCompare(changeactivite0.transitions[0], "running", false);
            compare(changeactivite0.repeater.count, 3);
            mouseClick(activite0.children[5]);
            compare(changeactivite0.repeater.count, 2);
            compare(changeactivite0.repeater.itemAt(0).nom, "act2");
            compare(changeactivite0.repeater.itemAt(1).nom, "act3");
        }

        function test_moddif_nom() {
            activite2.children[0].text = "blabla";
            compare(activite2.nom, "blabla");
            let res = fk.getItem("Activite", activite2.activiteId);
            compare(res.nom, "blabla");
        }

        function test_moddif_nom_empty() {
            activite2.children[0].text = "a";
            activite2.children[0].text = "";
            compare(activite2.nom, "a");
        }

        name: "ChangeGroupe"
        testedNom: "qrc:/qml/configuration/ChangeGroupe.qml"
        params: {
        }
    }

}
