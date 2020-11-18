import "qrc:/qml/actions" as PageActions

BaseButton {

    action: PageActions.NewImageSection {
        position: targetIndex
        append: appendMode
    }

}
