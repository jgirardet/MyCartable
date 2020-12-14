import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.14
import "qrc:/qml/operations"

RowLayout {
    id: root

    required property Item sectionItem
    required property QtObject section
    property var model: section.model

    BaseOperation {
        //        Component.onCompleted: {
        //            model = root.model;
        //        }

        id: corps

        objectName: "corps"
        cellWidth: 16
        cellHeight: 30
        section: root.section
        model: section.model
        sectionItem: root.sectionItem

        delegate: DivisionDelegate {
            id: divdelegate

            quotient: quotientField
        }

    }

    Rectangle {
        height: corps.height
        Layout.preferredWidth: 5
        color: "black"
    }

    ColumnLayout {
        height: corps.height
        //    width: 200
        Layout.preferredWidth: 200

        Label {
            id: diviseur

            Layout.preferredHeight: corps.cellHeight
            Layout.preferredWidth: 200
            text: section.diviseur

            //      text: sectionId ?  corps.model.diviseur : undefined
            background: Rectangle {
                color: "white"
            }

        }

        Rectangle {
            Layout.preferredHeight: 5
            Layout.preferredWidth: 200
            color: "black"
        }

        TextField {
            id: quotientField

            Layout.preferredWidth: 200
            objectName: "quotientField"
            onTextEdited: {
                section.quotient = text;
            }
            //      Binding on text {
            //        when: root.sectionId
            //        value: corps.model.quotient
            //      }
            //      text: root.model.quotient
            Component.onCompleted: {
                text = section.quotient;
            }
            Keys.onReturnPressed: {
                section.model.getPosByQuotient();
            }

            validator: RegularExpressionValidator {
                regularExpression: /^(\d+,?(\d+)?)?$/
            }

        }

        Item {
            Layout.fillHeight: true
        }

    }

}
