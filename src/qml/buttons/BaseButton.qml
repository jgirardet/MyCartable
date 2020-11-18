//import "qrc:/qml/actions"
//  component NewTextSection : BaseButton {
//      action: PageActions.NewTextSection {
//        position: targetIndex
//        append: appendMode
//      }
//}
//  component NewEquationSection : BaseButton {
//      action: PageActions.NewEquationSection {
//      position: targetIndex
//        append: appendMode
//      }
//  }
//  component NewImageSection : BaseButton {
//      action: PageActions.NewImageSection {
//      position: targetIndex
//        append: appendMode
//      }
//  }
//  component NewImageSectionVide : BaseButton {
//      id: imagesectionvidebutton
//      action: PageActions.NewImageSectionVide {
//      position: targetIndex
//        append: appendMode
//        Component.onCompleted: action.dialog.parent = imagesectionvidebutton
//      }
//  }
//  component NewOperationSection : BaseButton {
//      id : operationbutton
//      action: PageActions.NewOperationSection {
//      position: targetIndex
//        append: appendMode
//        Component.onCompleted: action.dialog.parent = operationbutton
//      }
//  }
//  component NewTableauSection : BaseButton {
//      id : tableaubutton
//      action: PageActions.NewTableauSection {
//      position: targetIndex
//        append: appendMode
//        Component.onCompleted: action.dialog.parent = tableaubutton
//      }
//  }
//    component NewFriseSection : BaseButton {
//      action: PageActions.NewFriseSection {
//        position: targetIndex
//        append: appendMode
//      }
//}
//  component RemovePage : BaseButton {
//      action: PageActions.RemovePage {
//      }
//  }
//  component ExportOdt : BaseButton {
//      action: PageActions.ExportOdt {
//      }
//  }
//  component ExportPdf : BaseButton {
//      action: PageActions.ExportPdf {
//      }
//  }

import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/actions" as PageActions

ToolButton {
    id: control

    property string sectionName
    property int targetIndex
    property var target
    property var dialog
    property bool appendMode

    enabled: ddb.currentPage
    icon.color: enabled ? "transparent" : ddb.colorPageToolBar
    visible: enabled

    PageActions.ActionToolTip {
        visible: hovered
        text: action.tooltip
        shortcut: action.shortcut ?? ""
    }

    background: Rectangle {
        //    width: 40
        implicitWidth: 40
        implicitHeight: 40
        //    height: 40
        color: Qt.darker(ddb.colorPageToolBar, control.enabled && control.hovered ? 1.5 : 1)
    }

}
