// Class de base pour les menus
// on open/close avec ouvre et ferme
// interface :
//    setStyleFromMenu: implémenté par target et appelé via menu
//    ex : menu.target.setStyleFromTarge(balbal)

import QtQuick 2.15
import QtQuick.Controls 2.15

Menu {
    //    implicitWidth: contentWidth

    id: root

    property var target

    function ouvre(newTarget) {
        //    parent = newTarget
        target = newTarget;
        uiManager.menuTarget = newTarget;
        root.popup();
    }

    function ferme() {
        root.visible = false;
    }

}
