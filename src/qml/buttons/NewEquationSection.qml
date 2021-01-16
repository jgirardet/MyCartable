import "qrc:/qml/actions" as PageActions

BaseButton {

    action: PageActions.NewEquationSection {
        position: targetIndex
        append: appendMode
    }

}
