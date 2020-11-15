import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    // interface de loader pour parer aux problemes dus à
    // la taille si loader est le root component
    id: itemdelegate

    property SplitView view
    property int viewIndex
    property string splitType
    property string splitText
    property int splitIndex
    property var splitUrl: ""
    property var splitComp: null
    property alias item: loader.item
    property bool loaded: loader.status == Loader.Ready

    state: view.orientation == Qt.Vertical ? "vertical" : "horizontal"
    Component.onCompleted: {
        // on charge le composant principal
        if (splitUrl !== "") {
            loader.source = splitUrl;
        } else if (splitComp !== view.nullComp) {
            loader.sourceComponent = splitComp;
        } else {
            print("either splitcomp or spliturl where defined");
            view.remove(viewIndex);
            return ;
        }
    }
    states: [
        State {
            name: "vertical"

            PropertyChanges {
                SplitView.fillWidth: true
                SplitView.fillHeight: false
                SplitView.preferredHeight: view.height / view.count
                target: itemdelegate
            }

        },
        State {
            name: "horizontal"

            PropertyChanges {
                SplitView.fillHeight: true
                SplitView.fillWidth: false
                SplitView.preferredWidth: view.width / view.count
                target: itemdelegate
            }

        }
    ]

    Loader {
        id: loader

        anchors.fill: parent
        asynchronous: true
        visible: status == Loader.Ready
    }

}
