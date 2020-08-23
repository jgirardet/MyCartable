import ".."
import QtQuick 2.15
import QtQuick.Window 2.15

Item {
    id: item

    width: 600
    height: 600

    CasTest {
        property var model: [{
            "id": 2,
            "nom": "Mathématiques",
            "annee": 2019,
            "position": 0,
            "fgColor": "black",
            "bgColor": "red"
        }, {
            "id": 3,
            "nom": "Francais",
            "annee": 2019,
            "position": 1,
            "fgColor": "black",
            "bgColor": "blue"
        }, {
            "id": 4,
            "nom": "Histoire-Géo",
            "annee": 2019,
            "position": 2,
            "fgColor": "black",
            "bgColor": "green"
        }, {
            "id": 5,
            "nom": "Langues",
            "annee": 2019,
            "position": 3,
            "fgColor": "black",
            "bgColor": "orange"
        }, {
            "id": 6,
            "nom": "Sciences",
            "annee": 2019,
            "position": 4,
            "fgColor": "black",
            "bgColor": "purple"
        }, {
            "id": 7,
            "nom": "Arts",
            "annee": 2019,
            "position": 5,
            "fgColor": "black",
            "bgColor": "pink"
        }, {
            "id": 1,
            "nom": "Divers",
            "annee": 2019,
            "position": 6,
            "fgColor": "black",
            "bgColor": "grey"
        }]

        property var modelMatieres:  [
          {'id': 15, 'nom': 'Physique', 'activites': [43, 44, 45], 'groupe': 6, 'fgColor': "red", 'bgColor': "blue", 'position': 0, "nbPages": 3},
          {'id': 16, 'nom': 'Chimie', 'activites': [46, 47, 48], 'groupe': 6, 'fgColor': "red", 'bgColor': "yellow", 'position': 1, "nbPages": 3},
          {'id': 17, 'nom': 'Technologie', 'activites': [49, 50, 51], 'groupe': 6, 'fgColor': "red", 'bgColor': "orange", 'position': 2, "nbPages": 3},
          {'id': 18, 'nom': 'SVT', 'activites': [52, 53, 54], 'groupe': 6, 'fgColor': "red", 'bgColor': "purple", 'position': 3, "nbPages": 3}]

        property var modelActivites: [
            {"id": 1, "matiere": 1, "nom": "act1", "position": 0, "nbPages": 0},
            {"id": 2, "matiere": 1, "nom": "act2", "position": 1, "nbPages": 1},
            {"id": 3, "matiere": 1, "nom": "act3", "position": 2, "nbPages": 2},
        ]

        property var un
        property var deux
        property var activite0
        property var activite1
        property var activite2
        property var changeactivite0
        property var changematiere0
        property var mat0
        property var mat1

        function initPre() {
        }

        function initPreCreate() {
            ddb._getActivites = [...modelActivites]
            ddb._getMatieres = [...modelMatieres]
            ddb._getGroupeMatieres = [...model];
        }

        function initPost() {
            tested.height = item.height;
            tested.model = ddb.getGroupeMatieres(2019);
//            tested.changematiere.model = ddb.getMatieres(1);
            un = tested.itemAtIndex(1);
            deux = tested.itemAtIndex(2);


            changeactivite0 =  tested.itemAtIndex(0).changematiere.itemAtIndex(0).children[1]
            activite0 =  tested.itemAtIndex(0).changematiere.itemAtIndex(0).children[1].children[0]
            activite1 =  tested.itemAtIndex(0).changematiere.itemAtIndex(0).children[1].children[1]
            activite2 =  tested.itemAtIndex(0).changematiere.itemAtIndex(0).children[1].children[2]

            waitForRendering(tested)
            changematiere0 = tested.itemAtIndex(0).changematiere
            mat0 = changematiere0.itemAtIndex(0).children[0]
            mat1 = changematiere0.itemAtIndex(1).children[0]
        }

        function test_init() {
            compare(tested.model, model);
        }

        function test_ddb_properties() {
            compare(un.text.text, "Francais");
            compare(deux.text.text, "Histoire-Géo");
            verify(Qt.colorEqual(un.baseColor, "blue"));
            var rect = un.colorbutton;
            verify(Qt.colorEqual(rect.gradient.stops[0].color, "blue"));
            verify(Qt.colorEqual(un.text.background.gradient.stops[0].color, "blue"));
        }

        function test_baseColorbindings() {
            un.baseColor = "yellow"
            verify(Qt.colorEqual(un.text.background.gradient.stops[0].color, "yellow") , `${un.text.background.gradient.stops[0].color} != ${"yellow"}`);
            verify(Qt.colorEqual(un.colorbutton.gradient.stops[0].color, "yellow") , `${un.colorbutton.gradient.stops[0].color} != ${"yellow"}`);
            compare(ddb._applyGroupeDegrade, [3, "#ffff00"])
        }

        function test_change_gradient_color_reject() {
            var rect = un.colorbutton
            mouseClick(rect);
            verify(Qt.colorEqual(tested.colordialog.currentColor, "blue"), `${tested.colordialog.currentColor} != "blue"`);
            tested.colordialog.currentColor = "purple"
            tested.colordialog.close()
            verify(Qt.colorEqual(un.baseColor, "blue") , `${un.baseColor} != ${"blue"}`);
          }
        function test_change_gradient_color_accept() {
            var rect = un.colorbutton;
            mouseClick(rect);
            tested.colordialog.currentColor = "purple"
            tested.colordialog.accept()
            verify(Qt.colorEqual(un.baseColor, "purple") , `${un.baseColor} != ${"purple"}`);
        }

        function test_moddif_nom_groupe() {
          un.text.text = "blabla"
          compare(un.nom, "blabla")
          compare(ddb._updateGroupeMatiereNom, [3, "blabla"])
        }

        // " COIN DES MATIERES


        function test_ChangeMAtiereProperties() {
          var mat0 = tested.itemAtIndex(0).changematiere.itemAtIndex(0).children[0]
          compare(mat0.children[0].text, "Physique")
          verify(Qt.colorEqual(mat0.children[0].background.color, "blue") , `${mat0.children[0].background.color} != ${"blue"}`);
          compare(mat0.children[1].text, "3 rubriques\n3 pages")
        }

        function test_moddif_nom_matiere() {
          var mat0 = tested.itemAtIndex(0).changematiere.itemAtIndex(0).children[0]
          mat0.children[0].text = "blabla"
          compare(mat0.parent.nom, "blabla")
          compare(ddb._updateMatiereNom, [15, "blabla"])
        }

        function test_matiere_toggle_base() {
          var tog = mat0.children[2]
          compare(tog.state, "")
          compare(tog.icon.source, "qrc:/icons/less-than")
        }

        function test_matiere_toggle_no_activite() {
          changeactivite0.model = 0
          var tog = mat0.children[2]
          compare(tog.state, "no_activite")
        }

        function test_matiere_toggle_click() {
          var tog = mat0.children[2]
          mouseClick(tog)
          tryCompare(tog, "rotation", -90)
        }

        function test_matiere_toggle_click_empty_activite() {
          changeactivite0.model = 0
          var tog = mat0.children[2]
          ddb._addActivite = [{"id": 6, "matiere": 1, "nom": "novonovo", "position": 0, "nbPages": 0}]
          mouseClick(tog)
          tryCompare(tog, "rotation", -90)
          tryCompare(changeactivite0.children[0], "nom", "novonovo")
          tryCompare(changeactivite0.children[0].activitetext, "selectedText", "novonovo")
          tog.state="toggled"

        }

        function test_up_matiere() {
          const res = [ {'id': 15, 'nom': 'Physique', 'activites': [43, 44, 45], 'groupe': 6, 'fgColor': "red", 'bgColor': "blue", 'position': 0, "nbPages": 3}]
          ddb._moveMatiereTo = res
          mouseClick(mat1.children[3])
          compare(ddb._moveMatiereTo, [16, 0])
          compare(changematiere0.model, res)
        }

        function test_down_matiere() {
          const res = [ {'id': 15, 'nom': 'Physique', 'activites': [43, 44, 45], 'groupe': 6, 'fgColor': "red", 'bgColor': "blue", 'position': 0, "nbPages": 3}]
          ddb._moveMatiereTo = res
          mouseClick(mat1.children[4], 1, 1)
          compare(ddb._moveMatiereTo, [16, 2])
          compare(changematiere0.model, res)
        }

        function test_add_matiere() {
          const res = modelMatieres[0]
          ddb._addMatiere = res
          mouseClick(mat0.children[5])
          compare(ddb._addMatiere, [15])
          compare(changematiere0.model, res)
        }
        function test_remove_matiere() {
          const res = [ {'id': 15, 'nom': 'Physique', 'activites': [43, 44, 45], 'groupe': 6, 'fgColor': "red", 'bgColor': "blue", 'position': 0, "nbPages": 3}]
          ddb._removeMatiere = res
          mouseClick(mat0.children[6])
          compare(ddb._removeMatiere, [15])
          compare(changematiere0.model, res)
          compare(changematiere0.count, 1)
        }

        //" RAyon des activites"

        function test_activites_properties() {
            compare(activite0.nom, "act1")
            compare(activite0.children[0].text, "act1") // nmo
            compare(activite0.children[1].text, "0 page ") // nb page
            compare(activite1.children[1].text, "1 page ")
            compare(activite2.children[1].text, "2 pages")
            compare(activite0.children[2].enabled, false) // up button
            compare(activite1.children[2].enabled, true)
            compare(activite2.children[2].enabled, true)
            compare(activite0.children[3].enabled, true) // downbutton
            compare(activite1.children[3].enabled, true)
            compare(activite2.children[3].enabled, false)
            compare(activite0.children[5].enabled, true) // ermovebutton
            compare(activite1.children[5].enabled, false)
            compare(activite2.children[5].enabled, false)

        }

        function test_changeactivite_states() {
          compare(changeactivite0.state, "hidden")
          compare(changeactivite0.height, 0)
          compare(changeactivite0.opacity, 0)
          changeactivite0.state = "visible"
          tryCompare(changeactivite0.transitions[0], "running", false)
          compare(changeactivite0.height, changeactivite0.childrenRect.height)
          compare(changeactivite0.opacity, 1)
        }

        function test_up_activite() {
        changeactivite0.state = "visible"
          tryCompare(changeactivite0.transitions[0], "running", false)
          const res = [{"id": 5, "matiere": 1, "nom": "act1", "position": 0, "nbPages": 0}]
          ddb._moveActiviteTo = res
          mouseClick(activite1.children[2])
          compare(ddb._moveActiviteTo, [2, 0])
          compare(changeactivite0.model, res)
        }

        function test_down_activite() {
        changeactivite0.state = "visible"
          tryCompare(changeactivite0.transitions[0], "running", false)
          const res = [{"id": 6, "matiere": 1, "nom": "act1", "position": 0, "nbPages": 0}]
          ddb._moveActiviteTo = res
          mouseClick(activite0.children[3])
          compare(ddb._moveActiviteTo, [1, 1])
          compare(changeactivite0.model, res)
        }

        function test_add_activite() {
          changeactivite0.state = "visible"
          tryCompare(changeactivite0.transitions[0], "running", false)
          const res = [{"id": 6, "matiere": 1, "nom": "novonovo", "position": 0, "nbPages": 0}]
          ddb._addActivite = res
          mouseClick(activite0.children[4])
          compare(ddb._addActivite, [1])
          compare(changeactivite0.model, res)
        }

        function test_remove_activite() {
        changeactivite0.state = "visible"
          tryCompare(changeactivite0.transitions[0], "running", false)
          const res = [{"id": 6, "matiere": 1, "nom": "act3", "position": 0, "nbPages": 0}]
          ddb._removeActivite = res
          mouseClick(activite0.children[5])
          compare(ddb._removeActivite, [1]) // attention ne pas choisir un avec nbpase > 0
          compare(changeactivite0.model, res)
        }

        function test_moddif_nom() {
          activite2.children[0].text = "blabla"
          compare(activite2.nom, "blabla")
          compare(ddb._updateActiviteNom, [3, "blabla"])
        }

        name: "ChangeGroupe"
        testedNom: "qrc:/qml/configuration/ChangeGroupe.qml"
        params: {
        }
    }

}
