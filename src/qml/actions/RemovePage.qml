BasePageAction {
    icon.source: "qrc:///icons/removePage"
    onTriggered: {
        page.classeur.deletePage();
    }
    tooltip: "Supprimer la page ?"
    shortcut: ""
}
