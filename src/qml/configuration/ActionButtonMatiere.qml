import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: root
    property Item referent
           ToolTip.visible: hovered
           ToolTip.timeout: 1000
           background: Rectangle {
               color: "transparent"
           }
           icon.color: "transparent"
           display: AbstractButton.IconOnly
           anchors.verticalCenter: referent.verticalCenter
           contentItem.opacity: enabled ? 1 : 0.5
           onEnabledChanged: {
               if (enabled) {
                   contentItem.opacity = 1
               } else {
                   0.5
               }
           }

           onHoveredChanged:  {
               if (hovered) {
                   animbutton.restart()
               } else {
                   animbutton.restart()
                   animbutton.stop()

               }

           }


           SequentialAnimation {
                   id: animbutton
                   running: enabled && hovered
                   loops: Animation.Infinite
                   NumberAnimation { target: root; property: "opacity"; from: 1; to: 0.6; duration: 700 }
                   NumberAnimation { target: root; property: "opacity"; to: 1; duration: 700 }
               }


           }
