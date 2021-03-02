import QtQuick 2.15
import QtQuick.Controls 2.15

MenuSlider {
    id: root

    property int adjustedValue: Math.floor(value / 10) ? Math.floor(value / 10) : 1

    function update_target() {
        if (!menu.target)
            return ;

        menu.target.setStyleFromMenu({
            "style": {
                "weight": adjustedValue
            }
        });
    }

    triggerValue: adjustedValue
    onTargetChanged: {
        if (target) {
            value = target.item.opacity * 100;
            root.background.barre.height = 20;
        }
    }

    Binding {
        target: background
        property: "opacity"
        value: adjustedValue / 10
    }

    Binding {
        when: root.target != undefined
        target: background.barre
        property: "color"
        value: root.target ? root.target.item.strokeStyle : "black"
    }

}
