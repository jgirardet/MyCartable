import QtQuick 2.14
import QtQuick.Controls 2.14

Dialog {
    id: root
    property color color: "transparent"
    contentItem: ColorGrid {
        id: colorgrid
        colors: ["transparent", "darkblue", "blue", "dodgerblue", "steelblue", "deepskyblue", "lightskyblue", "aqua", "aquamarine", "lightcyan", "darkred", "firebrick", "crimson", "red", "orangered", "darkorange", "orange", "coral", "lightsalmon", "goldenrod", "gold", "yellow", "lightgoldenrodyellow", "darkgreen", "green", "olivedrab", "yellowgreen", "mediumseagreen", "limegreen", "lime", "springgreen", "lightgreen", "sienna", "peru", "chocolate", "sandybrown", "peachpuff", "rosybrown", "grey", "darkgray", "lightgray", "indigo", "purple", "blueviolet", "mediumorchid", "mediumpurple", "mediumvioletred", "hotpink", "violet", "fuchsia", "pink", "black", "white"]
    }
    Connections {
        target: colorgrid
        function onPicked(colorPicked) {
            color = colorPicked
            close()
        }

    }
    header: Label {
        text: "Choisir la couleur"
        horizontalAlignment: Text.AlignHCenter
        background: Rectangle {
            anchors.fill: parent
            color: root.color
        }
    }
}


