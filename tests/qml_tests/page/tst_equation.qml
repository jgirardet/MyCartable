import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "Equation"
    testedNom: "qrc:/qml/page/operations/Equation.qml"
    params: {
      "base": item
    }

    function initPre() {}

    function initPreCreate() {}

    function initPost() {
      ddb._loadSection = {
        'id': 1,
        'created': '2019-09-22T19:21:57.521813',
        'modified': '2019-09-22T19:21:57.521813',
        'page': 1,
        'position': 1,
        'classtype': 'EquationSection',
        'content': '1     \n__ + 1\n15    '
      }
      tested.sectionId = 1
    }

    function test_init() {
      // test on section id changed
      compare(tested.data, {
        'id': 1,
        'created': '2019-09-22T19:21:57.521813',
        'modified': '2019-09-22T19:21:57.521813',
        'page': 1,
        'position': 1,
        'classtype': 'EquationSection',
        'content': '1     \n__ + 1\n15    '
      })
    }

    function test_bind_text_data_contnat() {
      compare(tested.text, '1     \n__ + 1\n15    ')
    }

  }
}