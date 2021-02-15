import MyCartable 1.0
import PyTest 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

TestCase {
    id: testcase

    property var tested
    property var testedNom
    property var params
    property var backupParams
    property var ddbData
    property bool autocreate: true
    property var dtb

    function init() {
        fk.resetDB();
        backupParams = params;
        initPre();
        if (autocreate)
            tested = createObj(testedNom, params);

        initPost();
    }

    function initPre() {
    }

    function initPost() {
    }

    function createObj(nom, rabParams, parentItem) {
        var kwargs = {
        };
        if (rabParams)
            Object.assign(kwargs, rabParams);

        var comp = Qt.createComponent(nom);
        if (comp.status != 1)
            print(comp, comp.status, comp.errorString());

        var obj = createTemporaryObject(comp, parentItem ? parentItem : testcase.parent, kwargs);
        return obj;
    }

    function getSpy(targetObj, signaltxt) {
        return compspyc.createObject(item, {
            "target": targetObj,
            "signalName": signaltxt
        });
    }

    function signalChecker(obj, signaltxt, command, calledArgs = []) {
        var spy = getSpy(obj, signaltxt);
        eval(command);
        spy.wait();
        var i = 0;
        for (var j of calledArgs) {
            compare(spy.signalArguments[0][i], j);
            i += 1;
        }
    }

    function menuClick(menu, x, y, ref = parent) {
        var bx = x;
        var by = y;
        menu.x = 0;
        menu.y = 0;
        mouseClick(ref, x, y);
        menu.x = bx;
        menu.y = by;
    }

    function menuGetItem(menu, index, positions) {
        var itm = menu.contentItem.itemAtIndex(index);
        for (var i of positions) {
            itm = itm.children[i];
        }
        return itm;
    }

    function clickAndWrite(_obj, seq = "Ctrl+a,b,c,d") {
        // click select all erase
        mouseClick(_obj);
        keySequence(seq);
    }

    function clickAndUndo(_obj) {
        // click select all erase
        clickAndWrite(_obj, "ctrl+z");
    }

    function clickAndRedo(_obj) {
        // click select all erase
        clickAndWrite(_obj, "ctrl+shift+z");
    }

    when: windowShown

    Component {
        id: compspyc

        SignalSpy {
        }

    }

    dtb: Database {
    }

}
