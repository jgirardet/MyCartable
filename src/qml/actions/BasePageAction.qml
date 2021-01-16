import QtQuick 2.15
import QtQuick.Controls 2.15

Action {
    property int position
    property string nom
    property string tooltip
    property var dialog
    property bool append: true
    property QtObject page

    function newSection(kwargs = {
    }) {
        let newPos = append ? page.model.count : position + 1;
        page.addSection(nom, newPos, kwargs);
    }

}
