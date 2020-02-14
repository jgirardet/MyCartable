import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/page"
import ".."

Item {
  width: 200
  height: 200
  id: item
  Component {
      id: ddbcomp
      DdbMock {}
    }
  Component {
    id: refcomp
    Item {
      width: item.width
      height: item.height
      /* beautify preserve:start */
      property var annotations: []
      function deleteAnnotation(obj)  {}
      /* beautify preserve:end */
    }
  }

  Component {
    id: stabcomp
    StabyloRectangle {
      relativeX: 0.48
      relativeY: 0.10
      //referent: ref
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }

  TestCase {

    name: "StabyloRectangle";when: windowShown
    property StabyloRectangle stab
    property Item ref
    property DdbMock ddb

    function init() {
      //            ref = createTemporaryObject(refcomp, item) sinon Warn
      ref = refcomp.createObject(item)
      ddb = createTemporaryObject(ddbcomp, item)
      verify(ddb)
      stab = createTemporaryObject(stabcomp, ref, {
        "referent": ref,
        "ddb": ddb
      })
      verify(stab)
      verify(ref)
      ref.annotations.push(stab)
    }

    function cleanup() {
      ref.destroy
    }

    function test_id() {
      compare(stab.relativeX, 0.48)
      compare(stab.ddbId, 0)
    }

    function test_AnotXY() {
      compare(stab.x, 96)
      compare(stab.y, 20)
    }


    function test_update_style() {
      ddb._updateAnnotation = {}
      stab.color = "blue"
      var data = {'type':'color', 'value': 'red'}
      stab.setStyle(data)
      compare(stab.color,"#ff0000")
      compare(ddb._updateAnnotation[0], stab.ddbId)
      compare(ddb._updateAnnotation[1], data)
    }


    function test_menu_show() {
      mouseClick(stab, 0, 0, Qt.RightButton)
      compare(findChild(stab, "menuflottant").opened,true )
    }

    function test_menu_change_color() {
      compare(stab.color, "#806633")
      mouseClick(stab, 0, 0, Qt.RightButton)
      var red = findChild(stab, "menuflottant")
      waitForRendering(stab)
      mouseClick(stab, red.x, red.y, Qt.LeftButton)
      compare(Qt.colorEqual(stab.color, "red"), true)

    }


  }
}