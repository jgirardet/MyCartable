import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: tableauactions
    function complete(ite) {
        uiManager.menuFlottantTableau.ferme()
        ite.parent.reload()
    }

    component AddRow:  Action {
        property var cell
        icon.source: "qrc:///icons/add-row"
        onTriggered: {
          ddb.insertRow(cell.tableauSection, cell.ligne)
          uiManager.menuFlottantTableau.ferme()
          cell.parent.reload()

        }
    }
    component AppendRow:  Action {
        property var cell
        icon.source: "qrc:///icons/append-row"
        onTriggered: {
          ddb.appendRow(cell.tableauSection)
          uiManager.menuFlottantTableau.ferme()
          cell.parent.reload()

        }
    }
    component AddColumn:  Action {
        property var cell
        icon.source: "qrc:///icons/add-column"
        onTriggered: {
          ddb.insertColumn(cell.tableauSection, cell.colonne)
          uiManager.menuFlottantTableau.ferme()
          cell.parent.reload()


          }
    }
    component AppendColumn:  Action {
        property var cell
        icon.source: "qrc:///icons/append-column"
        onTriggered: {
          ddb.appendColumn(cell.tableauSection)
          uiManager.menuFlottantTableau.ferme()
          cell.parent.reload()

        }
    }
    component RemoveRow:  Action {
        property var cell
        icon.source: "qrc:///icons/remove-row"
        onTriggered: {
        ddb.removeRow(cell.tableauSection, cell.ligne)
        uiManager.menuFlottantTableau.ferme()
        cell.parent.reload()

        }
    }
    component RemoveColumn:  Action {
        property var cell
        icon.source: "qrc:///icons/remove-column"
        onTriggered: {
          ddb.removeColumn(cell.tableauSection, cell.colonne)
          uiManager.menuFlottantTableau.ferme()
          cell.parent.reload()

          }
    }

}
