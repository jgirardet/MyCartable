// Class de base pour les menus
// on open/close avec ouvre et ferme
// interface :
//    setStyleFromMenu: implémenté par target et appelé via menu
//    ex : menu.target.setStyleFromTarge(balbal)

import QtQuick 2.15
import QtQuick.Controls 2.15

Menu {
    id: root

    property var target

    function ouvre(newTarget) {
        target = newTarget;
        root.popup();
    }

}
