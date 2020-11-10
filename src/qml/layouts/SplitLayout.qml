import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

SplitView {
    //        repeater.model =

    id: root

    //key/value obj with key:str and value:Component
    property var componentKeys: object()
    // Dynamic collection
    property alias items: repeater
    // Data du 1er chargement. Seulement utilisé au début
    property alias initModel: repeater.modelObject

    // Change orientation with newOrientation or switch to other
    function flip(newOrientation) {
        if (newOrientation != undefined)
            orientation = newOrientation;
        else if (orientation == Qt.Vertical)
            orientation = Qt.Horizontal;
        else
            orientation = Qt.Vertical;
    }

    // simple hack pour que les flipps soient bien pris en compte
    onOrientationChanged: {
        root.width = root.width + 1;
        root.width = root.width - 1;
        root.height = root.height + 1;
        root.height = root.height - 1;
    }

    DynamicRepeater {
        id: repeater

        delegate: Loader {
            id: loader

            Component.onCompleted: {
            }
            sourceComponent: componentKeys[type]
            state: root.orientation == Qt.Vertical ? "vertical" : "horizontal"
            states: [
                State {
                    name: "vertical"

                    PropertyChanges {
                        target: loader
                        SplitView.fillWidth: true
                        SplitView.fillHeight: false
                        SplitView.preferredHeight: root.height / root.count
                    }

                },
                State {
                    name: "horizontal"

                    PropertyChanges {
                        target: loader
                        SplitView.fillHeight: true
                        SplitView.fillWidth: false
                        SplitView.preferredWidth: root.width / root.count
                    }

                }
            ]
        }

    }

}
