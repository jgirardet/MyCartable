import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14
import QtTest 1.14

TestCase {
    id: testcase
    when: windowShown
    /* beautify preserve:start */
    property var tested
    property var ddb
    property var uiManager
    property var testedNom
    property var params
    property var backupParams
    /* beautify preserve:end */

    function init() {
      backupParams = params
      initPre()
      ddb = createTemporaryObject(Qt.createComponent("DdbMock.qml"), testcase.parent)
      uiManager = createTemporaryObject(Qt.createComponent("UiManager.qml"), testcase.parent)
      initPreCreate()
      tested = createObj(testedNom, params)
      initPost()
    }

    function initPre() {}

    function initPreCreate() {}

    function initPost() {}

    function cleanup() {
        if (tested){tested.destroy()}
        params=backupParams //restore deafaut params if modified
    }

    function createObj(nom, rabParams, parentItem) {
       var kwargs =   {
        'ddb': ddb,
        "uiManager": uiManager
      }
        if (rabParams) {
          Object.assign(kwargs, rabParams);
        }
        var comp = Qt.createComponent(nom)
        if (comp.status != 1) {print(comp, comp.status, comp.errorString())}
        var obj = createTemporaryObject(comp, parentItem ? parentItem :testcase.parent, kwargs)
      return obj
    }

    Component {
    id: compspyc
    SignalSpy {
    }
  }

  function getSpy(targetObj, signaltxt) {
    return compspyc.createObject(item, {
      "target": targetObj,
      "signalName": signaltxt
    })
  }

  function menuClick(menu, x, y) {
    var bx = x
    var by = y
    menu.x = 0
    menu.y = 0
    mouseClick(testcase.parent, x, y)
    menu.x = bx
    menu.y = by
  }

  }
