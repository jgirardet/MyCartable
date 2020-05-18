import QtQuick 2.14

PageToolBarToolButton {
  id: root
  func: function() {
    ddb.addSection(ddb.currentPage, {
      "classtype": sectionName,
      "position": typeof targetIndex == "number" ? targetIndex : null
    })
  }
  Binding on icon.source {
    when: sectionName
    value: `qrc:///icons/new${sectionName}`
  }
}