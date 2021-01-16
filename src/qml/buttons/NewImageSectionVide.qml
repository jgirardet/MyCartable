import QtQuick 2.15
import "qrc:/qml/actions" as PageActions

BaseButton {
    id: imagesectionvidebutton

    action: PageActions.NewImageSectionVide {
        position: targetIndex
        append: appendMode
        Component.onCompleted: {
            action.dialog.parent = imagesectionvidebutton;
        }
    }

}
