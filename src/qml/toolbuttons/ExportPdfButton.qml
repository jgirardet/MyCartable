import QtQuick 2.14
import QtQuick.Controls 2.14

PageToolBarToolButton {
  id: root
  ToolTip.text: "Exporter la page en pdf"
  icon.source: "qrc:///icons/pdf"
  func: function() {
    ddb.exportToPDF()
  }
}