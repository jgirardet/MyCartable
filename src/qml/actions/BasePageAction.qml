import QtQuick 2.15
import QtQuick.Controls 2.15

Action {
    property int position
    property string nom
    property string tooltip
    property var dialog
    property bool append: true

    function newSection(kwargs = {
    }) {
        let newPos = append ? ddb.pageModel.count : position + 1;
        let params = {
            "classtype": nom,
            "position": newPos
        };
        Object.assign(params, kwargs);
        ddb.addSection(ddb.currentPage, params);
    }

}
