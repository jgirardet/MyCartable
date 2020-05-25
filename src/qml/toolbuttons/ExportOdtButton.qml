import QtQuick 2.14
import QtQuick.Controls 2.14

PageToolBarToolButton {
  id: root
  ToolTip.text: "Exporter la page en odt"
  icon.source: "qrc:///icons/odt"
  func: function() {
    ddb.exportToOdt()
  }
}