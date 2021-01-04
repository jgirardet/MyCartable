import QtQuick 2.15
import QtQuick.Controls 2.15

GridView {
    id: root

    required property Item sectionItem
    required property QtObject section

    model: section.model
    height: contentHeight
    contentWidth: cellWidth * section.columns
    width: contentWidth
    contentHeight: cellHeight * section.rows
    cellWidth: 50
    cellHeight: 50
    keyNavigationEnabled: false
    onCurrentItemChanged: {
        if (currentItem)
            currentItem.textinput.forceActiveFocus();

    }

    Binding on currentIndex {
        when: section.model
        value: model.cursor
    }

}
