import QtQuick 2.14
import QtTest 1.14
import "../../../src/main/resources/base/qml/page/menu"
import ".."

Item {
  id: item
  width: 200
  height: 300

  Component {
    id: ddbComp
    DdbMock {}
  }

  Component {
    id: testedComp
    MenuFlottant {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }

  TestCase {
    id: testcase
    name: "MenuFlottant"
    when: windowShown

    property MenuFlottant tested
    property DdbMock ddb
    //
    function init() {
      ddb = createTemporaryObject(ddbComp, item)
      tested = createTemporaryObject(testedComp, item, {
        'ddb': ddb
      })
    }

    function cleanup() {
    }

    function test_init() {

    }

  }
}