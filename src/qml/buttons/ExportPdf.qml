import "qrc:/qml/actions" as PageActions

BaseButton {
    onClicked: toast.showToast("Export en PDF démarré, cela peut prendre plusieurs secondes")

    action: PageActions.ExportPdf {
    }

}
