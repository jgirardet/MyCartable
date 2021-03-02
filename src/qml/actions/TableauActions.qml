import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: tableauactions

    component AddRow:  Action {
        property var cell
        icon.source: "qrc:///icons/add-row"
        onTriggered: {
          cell.parent.parent.section.insertRow(cell.ligne)

        }
    }
    component AppendRow:  Action {
        property var cell
        icon.source: "qrc:///icons/append-row"
        onTriggered: {
          cell.parent.parent.section.appendRow()

        }
    }
    component AddColumn:  Action {
        property var cell
        icon.source: "qrc:///icons/add-column"
        onTriggered: {
          cell.parent.parent.section.insertColumn(cell.colonne)


          }
    }
    component AppendColumn:  Action {
        property var cell
        icon.source: "qrc:///icons/append-column"
        onTriggered: {
          cell.parent.parent.section.appendColumn()

        }
    }
    component RemoveRow:  Action {
        property var cell
        icon.source: "qrc:///icons/remove-row"
        onTriggered: {
        cell.parent.parent.section.removeRow(cell.ligne)

        }
    }
    component RemoveColumn:  Action {
        property var cell
        icon.source: "qrc:///icons/remove-column"
        onTriggered: {
          cell.parent.parent.section.removeColumn(cell.colonne)

          }
    }

}
