import QtQuick 2.14
import ".."

Item {
  width: 200
  height: 200
  id: item

  CasTest {
    name: "MainMenuBar"
    testedNom: "qrc:/qml/divers/MainMenuBar.qml"
    params: {}
    property QtObject fichier

    function initPre() {}

    function initPost() {
      fichier = tested.menus[0]
    }

    function test_fichier() {
      compare(fichier.title, "&Fichier")
      compare(fichier.itemAt(0).text, "&Changer d'année")
    }

    function test_changer_annnee() {
      ddb._getMenuAnnees = [{
        "id": 2018,
        "niveau": "ce2"
      }, {
        "id": 2019,
        "niveau": "cm1"
      }, ]
      fichier.visible = true
      var buttonMenu = tested.menus[0].itemAt(0)
      var changerAnnee = findChild(tested, "changerAnnee")
      compare(changerAnnee.opened, false)
      mouseClick(buttonMenu)
      compare(changerAnnee.opened, true)

      var lv = changerAnnee.contentItem
      compare(lv.count, 2) // model ok
      compare(lv.itemAtIndex(0).text, "mon année de ce2 en 2018/2019")
      compare(lv.itemAtIndex(1).text, "mon année de cm1 en 2019/2020")

      mouseClick(lv.itemAtIndex(1))
      compare(ddb._changeAnnee, 2019)
      compare(changerAnnee.opened, false)

    }
  }
}