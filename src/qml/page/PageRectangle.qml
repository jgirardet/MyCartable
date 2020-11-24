import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/menu"

Rectangle {
    id: base

    property QtObject page

    color: Qt.rgba(98 / 255, 105 / 255, 123 / 255, 1)
    Component.onCompleted: {
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantAnnotationDessin.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantAnnotationDessin = newComp.createObject(base);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantText.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantText = newComp.createObject(base);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantAnnotationText.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantAnnotationText = newComp.createObject(base);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantTableau.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantTableau = newComp.createObject(base);
        else
            print(newComp.errorString());
        var newComp = Qt.createComponent("qrc:/qml/menu/MenuFlottantImage.qml");
        if (newComp.status == Component.Ready)
            uiManager.menuFlottantImage = newComp.createObject(base);
        else
            print(newComp.errorString());
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        PageToolBar {
            id: pageToolBar

            page: base.page
            Layout.fillWidth: true
            height: ddb.getLayoutSizes("preferredHeaderHeight")
        }

        Rectangle {
            Layout.preferredWidth: parent.width - 20
            Layout.preferredHeight: 50
            Layout.alignment: Qt.AlignHCenter
            color: "transparent"

            PageTitre {
                id: titre

                anchors.fill: parent
                page: base.page
            }

        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"
            radius: 10

            PageListView {
                id: pagelistview

                model: base.page ? base.page.model : 0
                anchors.fill: parent
            }

        }

    }

}
