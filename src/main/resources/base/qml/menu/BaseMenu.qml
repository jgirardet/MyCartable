import QtQuick 2.14
import QtQuick.Controls 2.14

// Class de base pour les menus
//
// on open/close avec ouvre et ferme
//
// interface :
//    setStyleFromMenu: implémenté par target et appelé via menu
//    ex : menu.target.setStyleFromTarge(balbal)

Menu {
  id: root
  /* beautify preserve:start */
  property var target
  parent: target
  /* beautify preserve:end */

  function ouvre(newTarget) {
    //    parent = newTarget
    target = newTarget
    uiManager.menuTarget = newTarget
    root.popup()
  }

  function ferme() {
    //    target = null
    root.visible = false
  }

}