import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3
import QtQuick.Shapes 1.15
import QtQuick.Window 2.15

Rectangle {
    id: root

    property var basemodel: [{
        "bgColor": "red",
        "ratio": 0.3
    }, {
        "bgColor": "blue",
        "ratio": 0.11
    }, {
        "bgColor": "green",
        "ratio": 0.05
    }]
    property string sectionId: "sectionId"
    property var ddb
    property var initmodel: ddb.friseGetInitModel(sectionId)
    property alias repeater: repeater
    property alias listmodel: listmodel
    property alias corps: corps

    height: 400
    width: parent.width
    color: "white"

    Rectangle {
        //        }
        //        Shape {
        //            id: fleche
        //            z: 0
        //            anchors.left: corps.right
        //            anchors.leftMargin: -4
        //            anchors.top: corps.top
        //            anchors.topMargin: -10
        //            height: corps.height + 20
        //            width: 30
        //            ShapePath {
        //                strokeWidth: 4
        //                strokeColor: "black"
        //                strokeStyle: ShapePath.SolidLine
        //                startX: 0
        //                startY: 0
        //                PathLine {
        //                    x: fleche.width
        //                    y: fleche.height / 2
        //                }
        //                PathLine {
        //                    x: 0
        //                    y: fleche.height
        //                }
        //            }
        //        }

        id: corps

        height: 100
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 10
        anchors.right: parent.right
        anchors.rightMargin: 30
        color: "white"
        border.width: 3

        MouseArea {
            //                    repeater.model = modd

            anchors.fill: parent
            hoverEnabled: true
            onClicked: {
                //                    var modd = repeater.model
                repeater.model.append({
                    "bgColor": "purple",
                    "ratio": 0.1
                });
            }
        }

        //        ListView {
        //            id: grandrow
        ListView {
            //                Rectangle {
            //                    id: rightborder
            //                    color: mouserightborder.held ? "yellow" : "black"
            //                    height: parent.height + 20
            //                    width: 5
            //                    anchors.top: parent.top
            //                    anchors.topMargin: 0
            //                    //                        anchors.right: parent.right
            //                    state: "down"
            //                    Drag.active: mouserightborder.held
            //                    //                        Drag.source: rightborder
            //                    Drag.source: mouserightborder
            //                    states: [
            //                        State {
            //                            name: "up"
            //                            PropertyChanges {
            //                                target: rightborder
            //                                anchors.topMargin: -20
            //                            }
            //                            AnchorChanges {
            //                                target: rightborder
            //                                anchors {
            //                                    right: mouserightborder.held ? undefined : parent.right
            //                                }
            //                            }
            //                        },
            //                        State {
            //                            name: "down"
            //                            PropertyChanges {
            //                                target: rightborder
            //                                anchors.topMargin: 0
            //                            }
            //                            AnchorChanges {
            //                                target: rightborder
            //                                anchors {
            //                                    right: mouserightborder.held ? undefined : parent.right
            //                                }
            //                            }
            //                        }
            //                    ]
            //                    MouseArea {
            //                        id: mouserightborder
            //                        property real startx
            //                        property bool held: false
            //                        anchors.fill: parent
            //                        hoverEnabled: true
            //                        onEntered: {
            //                            parent.color = "red";
            //                        }
            //                        onExited: {
            //                            parent.color = "black";
            //                        }
            //                        onPressed: {
            //                            startx = mouse.x;
            //                            held = true;
            //                        }
            //                        onWheel: {
            //                            if (wheel.angleDelta.y > 0)
            //                                rightborder.state = "up";
            //                            else
            //                                rightborder.state = "down";
            //                        }
            //                        onReleased: {
            //                            //                                        repeater.model.setProperty(index, "ratio", zone.width/corps.width)
            //                            if (held)
            //                                held = false;
            //                        }
            //                        drag.target: parent
            //                        drag.axis: Drag.XAxis
            //                        drag.minimumX: 0
            //                        drag.maximumX: corps.width - 5
            //                        drag.threshold: 0
            //                        drag.smoothed: false
            //                        onPositionChanged: {
            //                            if (held)
            //                                listmodel.setProperty(index, "ratio", (rightborder.x + rightborder.width) / corps.width);
            //                        }
            //                    }
            //                }

            id: repeater

            orientation: ListView.Horizontal
            width: parent.width

            model: ListModel {
                id: listmodel

                Component.onCompleted: {
                    for (let el of root.initmodel) {
                        append(el);
                    }
                }
            }

            delegate: TextArea {
                id: zone

                property bool hold: false
                property alias rightborder: rightborder
                property alias legende: legende
                property int startx

                function previousItem(item) {
                    if (item.parent == null)
                        return null;

                    var index = itemIndex(item);
                    return (index > 0) ? item.parent.children[itemIndex(item) - 1] : null;
                }

                height: corps.height
                width: corps.width * ratio
                selectByMouse: true
                padding: 10
                color: "black"
                horizontalAlignment: TextEdit.AlignHCenter
                verticalAlignment: TextEdit.AlignVCenter
                wrapMode: TextEdit.Wrap
                z: mousezone.held ? 1 : 0
                onXChanged: {
                    if (mousezone.held) {
                        if (x > width + startx) {
                            print(index, index + 1);
                            listmodel.move(index, index + 1, 1);
                            repeater.forceLayout();
                        }
                    }
                }
                //                    state: index ? "" : "first"
                //                    onStateChanged: print(state)
                states: [
                    State {
                        name: "moving"
                        when: mousezone.held

                        AnchorChanges {
                            target: zone

                            //                                anchors.left: previousItem(zone).right
                            anchors {
                                horizontalCenter: undefined
                                verticalCenter: undefined
                            }

                        }

                        ParentChange {
                            target: zone
                            parent: repeater.contentItem
                        }

                    }
                ]

                MouseArea {
                    //                        repeater.forceLayout()

                    id: mousezone

                    property bool held: false

                    anchors.fill: parent
                    drag.target: parent
                    drag.axis: Drag.XAxis
                    drag.minimumX: 0
                    drag.maximumX: corps.width - width
                    //                        drag.threshold: 0
                    //                        drag.smoothed: false
                    onPressed: {
                        if (mouse.button == Qt.LeftButton && mouse.modifiers == Qt.ControlModifier) {
                            held = true;
                            startx = zone.x;
                        } else {
                            mouse.accepted = false;
                        }
                    }
                    onReleased: {
                        held = false;
                    }
                }

                TextArea {
                    id: legende

                    height: Math.max(contentHeight + 10, 10)
                    width: Math.max(contentWidth + 20, 40)
                    anchors.bottomMargin: 10
                    anchors.topMargin: 10
                    anchors.horizontalCenter: rightborder.horizontalCenter
                    state: rightborder.state
                    horizontalAlignment: TextEdit.AlignHCenter
                    verticalAlignment: TextEdit.AlignVCenter
                    states: [
                        State {
                            name: "up"

                            AnchorChanges {
                                //                                    anchors.top: undefined

                                target: legende
                                anchors.bottom: rightborder.top
                            }

                        },
                        State {
                            name: "down"

                            AnchorChanges {
                                //                                    anchors.bottom: undefined

                                target: legende
                                anchors.top: rightborder.bottom
                            }

                        }
                    ]

                    background: Rectangle {
                        anchors.fill: parent
                        color: "pink"
                    }

                }

                background: Rectangle {
                    color: bgColor
                    border.width: 0
                    border.color: "black"
                }

            }

        }

    }

    ddb: QtObject {

        function friseGetInitModel(sectionid) {
            return basemodel;
        }

    }

}
