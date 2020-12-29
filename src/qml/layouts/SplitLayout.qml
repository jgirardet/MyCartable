import QtQuick 2.15
import QtQuick.Controls 2.15
import "qrc:/qml/divers"

SplitView {
    id: root

    property var layouts: []
    property alias items: repeater
    property alias initDataModel: repeater.modelObject
    property var layoutsAsArray: _layoutsAsArray()

    function _layoutsAsArray() {
        var innerArray = [];
        for (const key in layouts) {
            innerArray.push(layouts[key]);
        }
        innerArray.sort((a, b) => {
            return a.splitindex - b.splitindex;
        });
        return innerArray;
    }

    // append un element via son splittype
    function append(str) {
        insert(str, count);
    }

    // clear layout
    function clear() {
        repeater.clear();
        append("vide");
    }

    // Retourne le SplitLoader pour item
    function findSplitLoader(item) {
        if (item.splitType === undefined)
            return findSplitLoader(item.parent);
        else
            return item;
    }

    // Change orientation with newOrientation or switch to other
    function flip(newOrientation) {
        if (newOrientation != undefined)
            orientation = newOrientation;
        else if (orientation == Qt.Vertical)
            orientation = Qt.Horizontal;
        else
            orientation = Qt.Vertical;
    }

    // renvoie l'element  à index ou calcul l'index si besoin
    function get(el) {
        if (typeof el != "number")
            return findSplitLoader(el);
        else
            return repeater.get(el);
    }

    // append un element via son splittype
    function insert(str, idx) {
        let layout = layouts[str];
        repeater.insert(idx, layout);
    }

    // remove the last
    function pop() {
        remove(count - 1);
    }

    // efface  l'element position idx
    function remove(caller) {
        let idx = get(caller).viewIndex;
        repeater.remove(idx);
    }

    // change le type de layout
    function select(caller, value) {
        let idx = get(caller).viewIndex;
        repeater.remove(idx);
        insert(value, idx);
    }

    // simple hack pour que les flipps soient bien pris en compte
    onOrientationChanged: {
        root.width = root.width + 1;
        root.width = root.width - 1;
        root.height = root.height + 1;
        root.height = root.height - 1;
    }

    DynamicRepeater {
        id: repeater

        // overload default behavior
        function populate() {
            for (const el of modelObject) {
                root.append(el);
            }
        }

        delegate: SplitLoader {
            splitType: splittype
            splitText: splittext
            splitIndex: splitindex
            splitUrl: spliturl
            viewIndex: index
            view: root
        }

    }

}
