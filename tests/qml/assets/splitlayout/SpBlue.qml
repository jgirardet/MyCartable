import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    property alias lebutton: lebutton

    color: "blue"

    Button {
        id: lebutton

        x: 5
        y: 3
        text: "bla"
    }

}
