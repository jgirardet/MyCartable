import "qrc:/qml/actions" as PageActions

BaseButton {

    action: PageActions.NewTextSection {
        position: targetIndex
        append: appendMode
    }

}
