import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

TextField {

  /* beautify preserve:start */
      property var page
      /* beautify preserve:end */

  text: ddb.currentPage ? ddb.currentTitre : ""
  id: root
  readOnly: ddb.currentPage == 0 ? true : false
  Layout.fillWidth: true
  Layout.preferredHeight: 50

  onTextChanged: {
    ddb.currentTitre = text
  }

  Keys.onPressed: {
    if (event.key == Qt.Key_Return) {
      if (!page.model.rowCount()) {
        ddb.addSection(ddb.currentPage, {
          "classtype": "TextSection"
        })
      }
    }
  }

  Connections {
    target: ddb
    onNewPageCreated: {
      forceActiveFocus()
    }
  }

}