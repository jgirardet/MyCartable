/*
  Acte as repeater with behaviour of Container.
  Parent of created items will be containers parent

*/

import QtQml.Models 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15

Repeater {
    id: root

    property var modelObject: []

    signal itemSet(int index, Item item, var dict)

    function append(dict) {
        listmodel.append(dict);
    }

    function clean() {
        listmodel.clear();
    }

    function get(index) {
        return itemAt(index);
    }

    function insert(index, dict) {
        listmodel.insert(index, dict);
    }

    function move(from, to, n) {
        listmodel.move(from, to, n);
    }

    function set(index, dict) {
        listmodel.set(index, dict);
        itemSet(index, get(index), dict);
    }

    function setProperty(index, property, value) {
        listmodel.setProperty(index, property, value);
        let dict = {
        }; // see QTBUG-87222
        dict[property] = value;
        itemSet(index, get(index), dict);
    }

    function remove(index, count = 1) {
        listmodel.remove(index, count);
    }

    function populate() {
        for (const el of root.modelObject) {
            append(el);
        }
    }

    model: ListModel {
        id: listmodel

        Component.onCompleted: {
            populate();
        }
    }

}
