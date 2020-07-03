import QtQuick 2.14
import QtQuick.Controls 2.14

Text {
    id: root

    property int vitesse: 20 // en px/ms
    property int pauseOnLeft: 500
    property int pauseOnRight: 700
    property bool move: false
    property int dureeMove: trajet > 0 ? trajet * vitesse : 0
    property int textInitialPosition
    property int elideBackup
    property int referentiel: parent.width
    property int trajet: contentWidth - referentiel + 10

    font.family: ddb.fontMain
    elide: Text.ElideRight
    onMoveChanged: {
        if (!truncated && !textInitialPosition)
            return ;

        if (move) {
            if (textInitialPosition == 0 && x != 0)
                textInitialPosition = x;

            root.elideBackup = root.elide;
            root.elide = Text.ElideNone;
            pauseTimerRight.restart();
        } else {
            elide = elideBackup;
            moveTextLeft.stop();
            moveTextRight.stop();
            pauseTimerRight.stop();
            pauseTimerLeft.stop();
            x = textInitialPosition;
            textInitialPosition = 0;
        }
    }

    Timer {
        id: pauseTimerRight

        interval: pauseOnRight
        running: false
        repeat: false
        onTriggered: {
            moveTextLeft.restart();
        }
    }

    Timer {
        id: pauseTimerLeft

        interval: pauseOnLeft
        running: false
        repeat: false
        onTriggered: moveTextRight.restart()
    }

    NumberAnimation on x {
        id: moveTextLeft

        objectName: "moveTextLeft"
        from: textInitialPosition
        to: -trajet
        loops: 1
        duration: dureeMove
        running: false
        onFinished: {
            pauseTimerLeft.restart();
        }
    }

    NumberAnimation on x {
        id: moveTextRight

        objectName: "moveTextRight"
        from: root.x
        to: textInitialPosition
        loops: 1
        duration: dureeMove
        running: false
        onFinished: {
            pauseTimerRight.restart();
        }
    }

}
