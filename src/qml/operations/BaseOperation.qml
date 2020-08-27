import QtQuick 2.15
import QtQuick.Controls 2.15

GridView {
    id: root

    property int sectionId
    property var sectionItem

    contentWidth: cellWidth * model.columns
    width: contentWidth
    height: contentHeight
    contentHeight: cellHeight * model.rows
    //  height: cellHeight * model.rows
    cellWidth: 50
    cellHeight: 50
    keyNavigationEnabled: false
    onCurrentItemChanged: {
        if (currentItem)
            currentItem.textinput.forceActiveFocus();

    }

    Binding on currentIndex {
        when: model.sectionIdChanged
        value: model.cursor
    }

}
