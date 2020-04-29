import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "PageToolBar"
    testedNom: "qrc:/qml/page/PageToolBar.qml"
    params: {}

    function initPre() {}

    function initPreCreate() {}

    function initPost() {}
  }
}