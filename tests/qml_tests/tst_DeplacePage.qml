
import ".."
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {

    id: item
    width: 400
    height: 400
    Button {
        id: basebutton
        x: 100
        y: 100
    }
    CasTest {
        //            wait(3000);
        property var model
        function initPre() {
        }
        function initPreCreate() {
            model = [{
                "activites": [{
                    "id": "ac7",
                    "nom": "aaa"
                }, {
                    "id": "ac8",
                    "nom": "bbb"
                }, {
                    "id": "ac9",
                    "nom": "ccc"
                }],
                "bgColor": "red",
                "nom": "trois"
            }, {
                "activites": [{
                    "id": "ac10",
                    "nom": "eee"
                }, {
                    "id": "ac11",
                    "nom": "fff"
                }, {
                    "id": "ac12",
                    "nom": "ggg"
                }],
                "bgColor": "blue",
                "nom": "quatre"
            }];
            ddb._getDeplacePageModel = model;
            ddb.anneeActive = 3000;
        }
        function initPost() {
            tested.ouvre("pageid", basebutton);
            waitForRendering(item);
        }
        function test_init() {
            compare(tested.model, model);
            compare(tested.pageId, "pageid");
            compare(ddb._getDeplacePageModel, [3000]);
        }
        function test_matiere() {
            var mat1 = tested.matieres.children[0];
            compare(tested.matieres.children.length,3) // faut ajouter le repeater
            // modelData
            compare(mat1.text, "trois");
            verify(Qt.colorEqual(mat1.background.color, "red") , `${mat1.background.color} != ${"red"}`);
            // hover
            compare(mat1.highlighted, false)
            mouseMove(mat1,0,0)
            compare(mat1.highlighted, true)
            compare(mat1.activites.visible, true)
        }
        function test_activite() {
          // creation
          var mat2 = tested.matieres.children[1]
          compare(mat2.activites.children.length, 4) // on ajouter repeater
          var ac = mat2.activites.children[1]
          // properties
          compare(ac.text, "fff")
          verify(Qt.colorEqual(ac.background.color, "blue") , `${ac.background.color} != ${"blue"}`);
         // click
         mouseMove(mat2, 5,5)
          mouseClick(ac)
          compare(ddb._changeActivite, ["pageid","ac11"])
          compare(tested.visible, false)
        }
        function test_close_in_empty_space() {
          compare(tested.visible, true)
          mouseClick(tested.contentItem, 50,50)
          compare(tested.visible, false)
        }
        name: "DeplacePage"
        testedNom: "qrc:/qml/menu/DeplacePage.qml"
        params: {
        }
    }
}
