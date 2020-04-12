import QtQuick 2.14

BaseOperation {
  id: root
  cellWidth: 30
  cellHeight: 50

  delegate: SoustractionDelegate {
    model: root.model
  }

}