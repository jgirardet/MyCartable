import "qrc:/qml/actions" as PageActions

BaseButton {

    action: PageActions.NewFriseSection {
        position: targetIndex
        append: appendMode
    }

}
