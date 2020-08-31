import QtQuick 2.15
import QtQuick.Controls 2.15
//import "qrc:/qml/actions"

Item {
  component BaseButton : ToolButton {
      id: control

      property string sectionName
      property int targetIndex
      property var target
      property var dialog

      enabled: ddb.currentPage
      icon.color: enabled ? "transparent" : ddb.colorPageToolBar
      visible: enabled

      PageActions.ActionToolTip {
          visible: hovered
          text: action.tooltip
          shortcut: action.shortcut
      }

      background: Rectangle {
          //    width: 40
          implicitWidth: 40
          implicitHeight: 40
          //    height: 40
          color: Qt.darker(ddb.colorPageToolBar, control.enabled && control.hovered ? 1.5 : 1)
      }

  }


  component NewTextSection : BaseButton {
      action: PageActions.NewTextSection {
        position: targetIndex
      }

}

  component NewEquationSection : BaseButton {
      action: PageActions.NewEquationSection {
      position: targetIndex
      }
  }

  component NewImageSection : BaseButton {
      action: PageActions.NewImageSection {
      position: targetIndex
      }
  }

  component NewOperationSection : BaseButton {
      id : operationbutton
      action: PageActions.NewOperationSection {
      position: targetIndex
        Component.onCompleted: action.dialog.parent = operationbutton
      }
  }

  component NewTableauSection : BaseButton {
      id : tableaubutton
      action: PageActions.NewTableauSection {
      position: targetIndex
        Component.onCompleted: action.dialog.parent = tableaubutton
      }
  }

  component RemovePage : BaseButton {
      action: PageActions.RemovePage {
      }
  }

  component ExportOdt : BaseButton {
      action: PageActions.ExportOdt {
      }
  }

  component ExportPdf : BaseButton {
      action: PageActions.ExportPdf {
      }
  }


}