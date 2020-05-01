import QtQuick 2.14
import ".."

Item {
  width: 50
  height: 200
  id: item
  CasTest {
    name: "MovingText"
    testedNom: "qrc:/qml/divers/MovingText.qml"
    params: {
      "referentiel": item.width,
      "text": "a",
      "width": item.width,
      "vitesse": 1, // pour avoir le temps de tester
      "pauseOnLeft": 0,
      "pauseOnRight": 0 //pas de latence
    }
    /* beautify preserve:start */
    property var moveTextLeft
    property var moveTextRight
    /* beautify preserve:end */

    function initPre() {}

    function initPreCreate() {}

    function initPost() {
      moveTextLeft = findChild(tested, "moveTextLeft")
      moveTextRight = findChild(tested, "moveTextRight")
      verify(moveTextLeft.loops == 1)
      verify(moveTextRight.loops == 1)
    }

    function test_init() {
      verify(tested.text == "a")
      tested.text = "azeraezrtrerter".repeat(10)
      compare(tested.truncated, true)
    }

    function test_do_nothing_if_no_truncated() {
      tested.text = "a"
      tested.move = true
      verify(moveTextLeft.running == false)
    }

    function test_start_animation() {
      tested.text = "azeraezrtrerter"
      tested.move = true
      waitForRendering(tested)
      verify(moveTextLeft.running == true)
    }

    function test_start_animation_and_stop() {
      tested.text = "azeraezrtrerter"
      verify(tested.truncated == true)
      var oldX = tested.x
      tested.move = true
      waitForRendering(tested)
      verify(moveTextLeft.running == true)
      tested.move = false
      tryCompare(moveTextLeft, "running", false)
      tryCompare(tested, "x", oldX, 10000) // timeout pour la CI
      tryCompare(tested, "textInitialPosition", 0)
    }

  }
}