import QtQuick 2.15
import QtQuick.Controls 2.15

MenuSlider {
    id: root

    property int pointSize: 5
    property bool initial_load: true

    function update_target() {
        if (!menu.target)
            return ;
        else if (initial_load)
            initial_load = false;
        else
            menu.target.setStyleFromMenu({
            "style": {
                "pointSize": value
            }
        });
    }

    from: 1
    to: 20
    onPointSizeChanged: {
        if (target)
            value = pointSize;

    }

    Binding {
        target: background.barre
        property: "height"
        value: root.value
    }

}
