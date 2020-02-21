import QtQuick 2.12
import QtTest 1.12
import "../../../src/main/resources/base/qml/page"
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
    PageTitre {
      /* beautify preserve:start */
      property var ddb //need to inject ddb
      /* beautify preserve:end */
    }
  }

  TestCase {
    id: testcase
    name: "PageTitre"
    when: windowShown
    
    property PageTitre tested
    property DdbMock ddb
    //
    function init() {
      ddb = createTemporaryObject(ddbComp, item)
//      ddb.currentPage =1
      tested = createTemporaryObject(testedComp, item, {
        'ddb': ddb
      })
    }

    function cleanup() {
      tested.destroy()
    }

    function test_init() {
      ddb.currentTitre = "le titre"
      compare(tested.readOnly,  true)
      compare(tested.text,  "")
      ddb.currentPage = 1
      compare(tested.readOnly,  false)
      compare(tested.text,  "le titre")
    }

    function test_focus_on_page_created() {
      compare(tested.focus, false)
      ddb.newPageCreated({})
      compare(tested.focus, true)
    }

    function test_update_titre() {
      ddb.currentPage=1
      tested.forceActiveFocus()
      keySequence("a")
      compare(ddb.currentTitre, "a")
    }

    function test_add_sectionText_on_enter_no_other_section() {
    tested.page = {
       model: {
          rowCount:function (){return 4}
              }
        }
      ddb.currentPage=1
      tested.forceActiveFocus()

      // rien ne se passe si text vide
      tested.page.model.rowCount = function() {return 4}
      keyClick(Qt.Key_Return)
      compare(tested.focus, true)

      // create new TextSection si aucun avant
      tested.page.model.rowCount = function() {return 0}
      ddb.currentPage = 22
      keyClick(Qt.Key_Return)
      compare(ddb._addSection, [22, {"classtype": "TextSection"}])

//     rien ne se passe is une est déja créee
       tested.page.model.rowCount = function() {return 1}
      tested.forceActiveFocus()
      ddb._addSection = null
      keyClick(Qt.Key_Return)
      compare(ddb._addSection,null)
    }

  }
}