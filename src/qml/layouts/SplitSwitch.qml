import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

ComboBox {
    id: combo

    // surtout pour eviter les Warnings dans les tests
    property Item mainItem: Window.window.mainItem ? Window.window.mainItem : null
    property SplitLoader splitParent: mainItem ? mainItem.findSplitLoader(combo) : null

    textRole: "splittext"
    valueRole: "splittype"
    onActivated: mainItem.select(splitParent.viewIndex, currentValue)
    currentIndex: splitParent ? splitParent.splitIndex : 0
    model: mainItem ? mainItem.layoutsAsArray : []
}
