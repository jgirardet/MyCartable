import ".."
import QtQuick 2.15

Item {
    id: item

    property var item: {
        "tool": "rien",
        "fillStyle": "red"
    }
    property var _setStyleFromMenu

    function setStyleFromMenu(data) {
        _setStyleFromMenu = data;
    }

    width: 200
    height: 200

    CasTest {
        //            compare(ddb_)

        //            wait(3000);
        property var titrerempli
        property var rempli
        property var titrevide
        property var vide

        function initPre() {
        }

        function initPreCreate() {
        }

        function initPost() {
            tested.ouvre(item);
            titrevide= tested.itemAt(0);
            vide= tested.itemAt(1);
            titrerempli = tested.itemAt(2);
            rempli = tested.itemAt(3);
        }

        function test_init() {
            compare(tested.target, item);
        }



        function test_rempli_args_rect() {
            item.item.tool = "rect";
            tested.target = item;
            waitForRendering(rempli);
            var res = new  Map([["red",0], ["blue",1],["lime",2],["black",3]])
            for (const [col,ind] of res) {
              tested.ouvre(item)
              mouseClick(rempli.children[0].children[ind]);
              verify(Qt.colorEqual(item._setStyleFromMenu.style.bgColor, col) , `${item._setStyleFromMenu.style.fgColor} != ${col}`);
            }
            }

        function test_rempli_args_ellipse() {
            item.item.tool = "ellipse";
            tested.target = item;
            waitForRendering(rempli);
            var res = new  Map([["red",0], ["blue",1],["lime",2],["black",3]])
            for (const [col,ind] of res) {
              tested.ouvre(item)
              mouseClick(rempli.children[0].children[ind]);
              verify(Qt.colorEqual(item._setStyleFromMenu.style.bgColor, col) , `${item._setStyleFromMenu.style.fgColor} != ${col}`);
            }
            }
        function test_vide_args_ellipse() {
            item.item.tool = "fillellipse";
            tested.target = item;
            waitForRendering(rempli);
            var res = new  Map([["red",0], ["blue",1],["lime",2],["black",3]])
            for (const [col,ind] of res) {
              tested.ouvre(item)
              mouseClick(rempli.children[0].children[ind]);
              verify(Qt.colorEqual(item._setStyleFromMenu.style.bgColor, col) , `${item._setStyleFromMenu.style.fgColor} != ${col}`);
            }
            }


        function test_rempli_args_fillrect() {
            item.item.tool = "fillrect";
            tested.target = item;
            waitForRendering(rempli);
            var res = new  Map([["red",0], ["blue",1],["lime",2],["black",3]])
            for (const [col,ind] of res) {
              tested.ouvre(item)
              mouseClick(rempli.children[0].children[ind]);
              verify(Qt.colorEqual(item._setStyleFromMenu.style.bgColor, col) , `${item._setStyleFromMenu.style.fgColor} != ${col}`);
            }
            }



        function test_rempli_args_trait() {
            item.item.tool = "trait";
            tested.target = item;
            waitForRendering(rempli);
            var res = new  Map([["red",0], ["blue",1],["lime",2],["black",3]])
            for (const [col,ind] of res) {
              tested.ouvre(item)
              mouseClick(rempli.children[0].children[ind]);
              verify(Qt.colorEqual(item._setStyleFromMenu.style.bgColor, col) , `${item._setStyleFromMenu.style.fgColor} != ${col}`);
            }
            }


        name: "MenuFlottantAnnotationDessin"
        testedNom: "qrc:/qml/menu/MenuFlottantAnnotationDessin.qml"
        params: {
        }
    }

}
