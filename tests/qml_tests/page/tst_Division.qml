import QtQuick 2.14
import ".."
import "qrc:/js/lodash.js"
as Lodash

Item {
  width: 600
  height: 600
  id: item

  Component {
    id: modelComp
    ListModel {
      id: listmodel
      property int rows: 5
      property int columns: 9
      property int cursor: 0
      property int sectionId: 0
      property int size: 45
      property int virgule: 0
      property int diviseur: 11
      property real dividende: 264
      property string quotient: ""

      /* beautify preserve:start */
      property var corps
      property var datas: ['', '2', '', '', '6', '', '', '4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
      /* beautify preserve:end */
      Component.onCompleted: {
        for (var x of datas) {
          listmodel.append({
            "display": x,
            "edit": x
          })
        }
      }
      //      function isResultLine(index) {
      //      return false
      //      }
      //      function isRetenueLine(index) {
      //      return false
      //      }
      //      function isMiddleLine(index) {
      //      return true
      //      }
      function isDividendeLine(index) {
        return _.range(0, 9).includes(index) ? true : false
      }

      function isMembreLine(index) {
        return Math.floor(index / columns) & 1 ? true : false
      }

      function isRetenue(index) {
        return [11, 3, 6, 14, 21, 24, 29, 32].includes(index) ? true : false
      }

      function isRetenueGauche(index) {
        return [3, 6, 21, 24].includes(index) ? true : false
      }

      function isRetenueDroite(index) {
        return [11, 14, 29, 32].includes(index) ? true : false
      }

      function readOnly(index) {
        var r = [3, 6, 10, 11, 13, 14, 16, 17, 18, 19, 21, 22, 24, 25, 28, 29, 31, 32, 34, 35, 37, 40, 43]
        return r.includes(index) ? false : true
      }

      function getInitialPosition() {
        return size - 1
      }

      property
      var _moveCursor

      function moveCursor(index, key) {
        _moveCursor = [index, key]

      }

      function goToResultLine() {
        if (corps.currentIndex == 13) {
          corps.currentIndex = 25
        } else if (currentIndex == 31) {
          corps.currentIndex = 43
        }
      }

      function getPosByQuotient() {
        cursor = 13
      }

      function goToAbaisseLine() {
        corps.currentIndex = 25
      }
      property
      var _addRetenues: ""

      function addRetenues() {
        _addRetenues = "added"
      }
    }
  }

  CasTest {
    name: "Division"
    testedNom: "qrc:/qml/page/operations/Division.qml"
    /* beautify preserve:start */
    property var model
    property var quotient
    property var corps
    /* beautify preserve:end */

    function initPre() {
      model = createTemporaryObject(modelComp, item)
      params = {
        "model": model
      }
    }

    function initPost() {
      quotient = findChild(tested, "quotientField")
      corps = findChild(tested, "corps")
      model.corps = corps
    }

    function test_the_mock_model() {
      compare(model.count, model.size)
      compare(tested.model, model)
    }

    function test_properties() {
      //        //1,10 (text) et 11 retenu droit,  21 : retenue gauche
      compare(corps.itemAtIndex(1).textinput.color, "#000000") //black
      compare(corps.itemAtIndex(10).textinput.color, "#000000") //black
      compare(corps.itemAtIndex(11).textinput.color, "#ff0000") //Red
      compare(corps.itemAtIndex(21).textinput.color, "#ff0000") //Red

      compare(corps.itemAtIndex(1).textinput.horizontalAlignment, TextInput.AlignHCenter)
      compare(corps.itemAtIndex(10).textinput.horizontalAlignment, TextInput.AlignHCenter)
      compare(corps.itemAtIndex(11).textinput.horizontalAlignment, TextInput.AlignLeft)
      compare(corps.itemAtIndex(21).textinput.horizontalAlignment, TextInput.AlignRight)

      compare(corps.itemAtIndex(1).textinput.verticalAlignment, TextInput.AlignVCenter)
      compare(corps.itemAtIndex(10).textinput.verticalAlignment, TextInput.AlignVCenter)
      compare(corps.itemAtIndex(11).textinput.verticalAlignment, TextInput.AlignVCenter)
      compare(corps.itemAtIndex(21).textinput.verticalAlignment, TextInput.AlignVCenter)
      //
    }

    function test_regex_validator_data() {
      return [{
        inp: "",
        res: true
      }, {
        inp: "1",
        res: true
      }, {
        inp: "12",
        res: true
      }, {
        inp: "1123443",
        res: true
      }, {
        inp: "1,",
        res: true
      }, {
        inp: "1,0",
        res: true
      }, {
        inp: "1,13245",
        res: true
      }, ]
    }

    function test_regex_validator(data) {
      var exp = quotient.validator.regularExpression
      compare(Boolean(data.inp.match(exp)), data.res)

    }

    function test_focus_is_highlighted() {
      var it = corps.itemAtIndex(1).textinput
      it.focus = true
      compare(Qt.colorEqual(it.background.color, "yellow"), true)
    }

    function test_morekeys() {

      //focus quotient ou corps quand Entrée pressé
      quotient.forceActiveFocus()
      compare(corps.focus, false)
      compare(quotient.focus, true)
      keyClick(Qt.Key_Return)
      compare(corps.itemAtIndex(13).textinput.focus, true)
      compare(quotient.focus, false)
      keyClick(Qt.Key_Return)
      compare(corps.focus, false)
      compare(quotient.focus, true)

      // got to line result
      mouseClick(corps.itemAtIndex(13))
      keyClick(Qt.Key_Minus)
      compare(corps.currentIndex, 25)

      // got to line : chiffre abaisse
      mouseClick(corps.itemAtIndex(13))
      keyClick(Qt.Key_Plus)
      compare(corps.currentIndex, 25)

      // addRetenue
      keyClick(Qt.Key_Asterisk)
      compare(model._addRetenues, "added")

    }

  }

}