BasePageAction {
    icon.source: "qrc:///icons/removePage"
    onTriggered: ddb.removePage(ddb.currentPage)
    tooltip: "Supprimer la page ?"
    shortcut: ""
}
