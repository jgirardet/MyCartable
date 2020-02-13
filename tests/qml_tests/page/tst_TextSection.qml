import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/page"
import ".."
//import Mmm 1.0
import "../mmm" as Mmm

Item {
  id: item
  width: 200
  height: 300
//
  Component {
    id: ddbComp
    Mmm.MyModule {}
  }
//
//  Component {
//    id: testedComp
//    TextSection {
//      /* beautify preserve:start */
//      property var ddb //need to inject ddb
//      /* beautify preserve:end */
//    }
//  }
//
  TestCase {
    id: testcase
    name: "TextSection"
    when: windowShown


//    property TextSection tested
//    property DdbMock ddb
//    //
//    function init() {
//      ddb = createTemporaryObject(ddbComp, item)
//      tested = createTemporaryObject(testedComp, item, {
//        'ddb': ddb
//      })
//    }
//
//    function cleanup() {
//    }
//
    function test_init() {
      var ddb = createTemporaryObject(ddbComp, item)
      print(ddb.bla)
    }
    }
//
//  }
}