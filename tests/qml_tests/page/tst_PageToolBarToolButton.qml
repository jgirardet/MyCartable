import QtQuick 2.14
import ".."
import QtQuick.Controls 2.14

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "PageToolBarToolButton"
    testedNom: "qrc:/qml/toolbuttons/PageToolBarToolButton.qml"
    params: {
      "icon.source": "qrc:///icons/newImageSection"
    }

    function initPre() {}

    function initPreCreate() {}

    function initPost() {}

    function test_enabled() {
      ddb.currentPage = 0
      compare(tested.enabled, false)
      ddb.currentPage = 1
      compare(tested.enabled, true)
    }

    function test_hovered() {
      // disabled
      ddb.currentPage = 0
      compare(tested.visible, false)
      compare(tested.ToolTip.visible, false)
      compare(tested.background.color, ddb.colorPageToolBar) // disabled

      //enabled
      ddb.currentPage = 1 // active
      compare(tested.background.color, ddb.colorPageToolBar) // enabled

      //hovered
      mouseMove(tested, 1, 1)
      compare(tested.ToolTip.visible, true)
      compare(tested.background.color, "#838383") // hovered

    }

  }
}