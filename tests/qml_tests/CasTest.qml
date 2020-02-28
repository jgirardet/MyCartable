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
    /* beautify preserve:end */

    function init() {
      initPre()
      ddb = createTemporaryObject(Qt.createComponent("DdbMock.qml"), testcase.parent)
      uiManager = createTemporaryObject(Qt.createComponent("UiManager.qml"), testcase.parent)
      tested = createObj(testedNom, params)
      initPost()
    }

    function initPre() {}

    function initPost() {}

    function cleanup() {
        if (tested){tested.destroy()}
    }

    function createObj(nom, params) {
       var kwargs =   {
        'ddb': ddb,
        "uiManager": uiManager
      }
        if (params) {
          Object.assign(kwargs, params);
        }
        var comp = Qt.createComponent(nom)
        if (comp.status != 1) {print(comp, comp.status, comp.errorString())}
        var obj = createTemporaryObject(comp, testcase.parent, kwargs)
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
  }
