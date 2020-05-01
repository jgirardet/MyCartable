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
    property var ddbData
    /* beautify preserve:end */

  function init() {
    backupParams = params
    initPre()
    uiManager = createTemporaryObject(Qt.createComponent("UiManager.qml"), testcase.parent)
    ddb = createTemporaryObject(Qt.createComponent("DdbData.qml"), testcase.parent)

    initPreCreate()
    tested = createObj(testedNom, params)
    initPost()
  }

  function initPre() {}

  function initPreCreate() {}

  function initPost() {}

  function cleanup() {
    if (tested) {
      tested.destroy()
    }
    params = backupParams //restore deafaut params if modified
  }

  function createObj(nom, rabParams, parentItem) {
    var kwargs = {
      'ddb': ddb,
      "uiManager": uiManager
    }
    if (rabParams) {
      Object.assign(kwargs, rabParams);
    }
    var comp = Qt.createComponent(nom)
    if (comp.status != 1) {
      print(comp, comp.status, comp.errorString())
    }
    var obj = createTemporaryObject(comp, parentItem ? parentItem : testcase.parent, kwargs)
    return obj
  }

  Component {
    id: compspyc
    SignalSpy {}
  }

  function getSpy(targetObj, signaltxt) {
    return compspyc.createObject(item, {
      "target": targetObj,
      "signalName": signaltxt
    })
  }

  function signalChecker(obj, signaltxt, command, calledArgs = []) {
    var spy = getSpy(obj, signaltxt)
    eval(command)
    spy.wait()
    var i = 0
    for (var j of calledArgs) {
      compare(spy.signalArguments[0][i], j)
      i += 1
    }
  }

  function menuClick(menu, x, y, ref = parent) {
    var bx = x
    var by = y
    menu.x = 0
    menu.y = 0
    mouseClick(ref, x, y)
    menu.x = bx
    menu.y = by
  }

  function menuGetItem(menu, index, positions) {
    var itm = menu.contentItem.itemAtIndex(index)
    for (var i of positions) {
      itm = itm.children[i]
    }
    return itm
  }

}