import QtQuick 2.15
import QtQuick.Controls 2.15

Row {
    required property Item lexique
    property Item items: repeater

    Repeater {
        id: repeater

        model: lexique.model.availablesLocales

        delegate: CheckBox {
            checked: modelData.active
            text: modelData.nom
            onCheckedChanged: lexique.updateActivesLocales(modelData.id, checked)
        }

    }

}
