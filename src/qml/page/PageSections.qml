/*
AFfiche les sections de chaque page.

## Chronologie et principe:

La logique globabl se pase sur l'émission d'un signal `loaded` par les delegates(sections).
Cela permet de laisser le temps à tous les delegate de se charger complétement avant de les afficher.

### Chargement initial:

la property populated (default false) est changé en true quand tous les élements sont chargés et affichés
on customize le comportement dans `onPopulatedChanged`

### Ajout d'un élément:

Le signal `itemAdded` est émis quand l'élément est chargé avec idx comme index de l'item ajouté.
On customize le comportement dans `onItemAdded`

*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

Flickable {
    id: root

    required property QtObject page
    readonly property int lastPosition: page ? page.lastPosition : 0
    readonly property int count: repeater.count // count du visual, pas du model
    property bool populated: false
    property int _itemAlreadyLoaded: 0
    property alias removeDialog: removeDialog
    property alias addDialog: addSectionDialog
    property alias spacing: column.spacing

    signal itemAdded(int index)
    signal itemPopulating(int index)
    signal populateComplete()

    function itemAt(idx) {
        return repeater.itemAt(idx);
    }

    function positionAtIndex(idx) {
        if (idx > 0) {
            column.forceLayout();
            let item = itemAt(idx);
            let scrollToY = item.mapToItem(column, 0, 0).y;
            contentY = scrollToY - (height * 0.3);
        } else {
            contentY = 0;
        }
        returnToBounds();
    }

    function scrollToIndex(idx) {
        content_y_behavior.enabled = true;
        positionAtIndex(idx);
        content_y_behavior.enabled = false;
    }

    function removeItem(idx) {
        removeDialog.open(idx);
    }

    function _itemLoaded(index, item) {
        if (populated)
            item.loaded.connect(itemAdded);
        else
            item.loaded.connect(itemPopulating);
    }

    onItemPopulating: {
        _itemAlreadyLoaded += 1;
        if (_itemAlreadyLoaded == repeater.count) {
            column.forceLayout();
            positionAtIndex(index);
            populated = true;
        }
    }
    Component.onCompleted: {
        if (!page.model.count)
            populated = true;

    }
    onItemAdded: scrollToIndex(index)
    boundsBehavior: Flickable.StopAtBounds
    contentWidth: column.width
    contentHeight: column.height
    clip: true
    states: [
        State {
            name: "jumping"

            PropertyChanges {
                target: scrollanimation
                duration: 0
            }

        }
    ]

    Column {
        id: column

        spacing: 10

        Repeater {
            id: repeater

            model: page.model
            onItemAdded: root._itemLoaded(index, item)

            delegate: BasePageDelegate {
                referent: root
            }

        }

        Rectangle {
            id: basdepage

            color: "transparent"
            visible: root.count
            height: root.height * 2 / 3
            width: parent.width
        }

    }

    IndexedDialog {
        id: removeDialog

        message: "Supprimer cet élément ?"
        onAccepted: {
            page.model.remove(itemIndex, 1);
        }
        standardButtons: Dialog.Ok | Dialog.Cancel
    }

    AddSectionDialog {
        id: addSectionDialog

        page: root.page
    }

    Behavior on contentY {
        id: content_y_behavior

        enabled: false

        NumberAnimation {
            id: scrollanimation

            duration: 800
            easing.type: Easing.OutQuart
        }

    }

    ScrollBar.vertical: ScrollBar {
        id: scrollbar
    }

}
