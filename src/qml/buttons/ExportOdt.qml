import "qrc:/qml/actions" as PageActions

BaseButton {
    onClicked: toast.showToast("Export en ODT démarré, cela peut prendre plusieurs secondes")

    action: PageActions.ExportOdt {
    }

}
