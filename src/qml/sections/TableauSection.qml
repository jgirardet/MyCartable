import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    //    property var tableau: sectionId ? ddb.loadSection(sectionId) : {
    //    }

    id: root

    property int sectionId
    property var sectionItem

    width: grid.width
    height: grid.height

    GridLayout {
        id: grid

        property var selectedCells: []
        property var currentSelectedCell: null

        function reload() {
            repeater.model = ddb.initTableauDatas(root.sectionId);
            grid.columns = ddb.nbColonnes(root.sectionId);
        }

        function selectCell(obj) {
            obj.state = obj.state == "selected" ? "" : "selected";
            if (obj.state == "selected") {
                if (!selectedCells.includes(obj)) {
                    selectedCells.push(obj);
                    currentSelectedCell = obj;
                }
            } else {
                const index = selectedCells.indexOf(obj);
                if (index > -1)
                    selectedCells.splice(index, 1);

                if (obj == currentSelectedCell)
                    if (selectedCells.length > 0)
                    currentSelectedCell = selectedCells[selectedCells.length - 1];
                else
                    currentSelectedCell = null;;

            }
        }

        function setStyleFromMenu(data) {
            // set give data style to every selected cells
            for (var i of selectedCells) {
                i.state = ""; // leger hack pour les probleme de restore de value apres state
                i.setStyleFromMenu(data);
            }
            unSelectAll();
        }

        function unSelectAll() {
            // désectionne toutes les cases
            for (var i of Array(repeater.count).keys()) {
                var ite = grid.children[i];
                ite.state = "";
            }
            grid.selectedCells.length = 0;
            grid.currentSelectedCell = null;
        }

        objectName: "grid"
        columns: ddb.nbColonnes(root.sectionId) ?? 0
        columnSpacing: 3
        rowSpacing: 3

        Repeater {
            //            Connections {
            //                function onTableauLayoutChanged() {
            //                    repeater.model = ddb.initTableauDatas(root.sectionId);
            //                    print("hello");
            //                }
            //                target: ddb
            //            }
            //            model: root.sectionId ? ddb.initTableauDatas(root.sectionId) : 0

            id: repeater

            objectName: "repeater"
            model: root.sectionId ? grid.reload() : 0

            delegate: TextArea {
                id: tx

                property int colonne: modelData.x
                property int ligne: modelData.y
                property int tableauSection: root.sectionId

                function changeCase(event) {
                    var obj;
                    var newIndex = index;
                    switch (event.key) {
                    case Qt.Key_Right:
                        {
                            newIndex = newIndex + 1;
                            break;
                        };
                    case Qt.Key_Left:
                        {
                            newIndex = newIndex - 1;
                            break;
                        };
                    case Qt.Key_Up:
                        {
                            newIndex = newIndex - grid.columns;
                            break;
                        };
                    case Qt.Key_Down:
                        {
                            newIndex = newIndex + grid.columns;
                            break;
                        };
                    }
                    if (newIndex >= repeater.count)
                        return ;
                    else if (newIndex < 0)
                        return ;

                    repeater.itemAt(newIndex).forceActiveFocus();
                }

                function isFirstLine() {
                    var fl = text.split("\\n")[0].length;
                    return cursorPosition <= fl;
                }

                function isLastLine() {
                    return !text.slice(cursorPosition, length).includes("\\n");
                }

                function setBackgroundColor(value) {
                    background.color = value;
                    updateCell({
                        "style": {
                            "bgColor": value
                        }
                    });
                }

                function setForegroundColor(value) {
                    color = value;
                    updateCell({
                        "style": {
                            "fgColor": value
                        }
                    });
                }

                function setText() {
                    updateCell({
                        "texte": text
                    });
                }

                function setPointSize(key) {
                    if (key == Qt.Key_Plus)
                        font.pointSize += 2;
                    else if (key == Qt.Key_Minus)
                        font.pointSize -= 2;

                    updateCell({
                        "style": {
                            "pointSize": font.pointSize
                        }
                    });
                }

                function setStyleFromMenu(data) {
                    // pour tinput
                    if (!("style" in data))
                        return ;

                    var styleDict = data["style"];
                    if ("fgColor" in styleDict)
                        setForegroundColor(styleDict["fgColor"]);

                    if ("bgColor" in styleDict)
                        setBackgroundColor(styleDict["bgColor"]);

                    if ("underline" in styleDict)
                        setUnderline(styleDict["underline"]);

                }

                function setUnderline(value) {
                    font.underline = value;
                    updateCell({
                        "style": {
                            "underline": value
                        }
                    });
                }

                function updateCell(content) {
                    ddb.updateCell(root.sectionId, modelData.y, modelData.x, content);
                }

                focus: true
                Layout.minimumHeight: 10
                Layout.fillHeight: true
                Layout.fillWidth: true
                selectByMouse: true
                text: modelData.texte
                font.pointSize: modelData.style.pointSize ? modelData.style.pointSize : 14 // à changer aussi dans convert
                font.underline: modelData.style.underline
                color: modelData.style.fgColor
                Component.onCompleted: {
                    onTextChanged.connect(setText);
                }
                Keys.onPressed: {
                    var isMove = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Right].includes(event.key);
                    if ((isMove && (event.modifiers & Qt.ControlModifier)) || (event.key == Qt.Key_Right && cursorPosition == length) || (event.key == Qt.Key_Left && cursorPosition == 0) || (event.key == Qt.Key_Up && isFirstLine()) || (event.key == Qt.Key_Down && isLastLine())) {
                        changeCase(event);
                        event.accepted = true;
                    } else if (([Qt.Key_Minus, Qt.Key_Plus].includes(event.key)) && (event.modifiers & Qt.ControlModifier)) {
                        setPointSize(event.key);
                        event.accepted = true;
                    } else {
                    }
                }
                states: [
                    State {
                        name: "selected"

                        PropertyChanges {
                            target: background
                            color: "lightsteelblue"
                        }

                    }
                ]

                background: Rectangle {
                    anchors.fill: parent
                    border.width: 1
                    color: modelData.style.bgColor == "#00000000" ? "white" : modelData.style.bgColor
                }

            }

        }

    }

    MouseArea {
        // on ne fait rien en dehors de la zone
        // le même on fait rien
        // doit être une des cell
        // il ne faut pas sette mouse.accepted = false/true sinon pas de positionchanged

        id: bigMouse

        property bool selecting: false

        anchors.fill: parent
        preventStealing: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        propagateComposedEvents: true
        onPressed: {
            var ite = grid.childAt(mouse.x, mouse.y);
            if (mouse.button == Qt.LeftButton) {
                if (mouse.modifiers == Qt.ControlModifier) {
                    grid.selectCell(grid.childAt(mouse.x, mouse.y));
                    selecting = true;
                    return ;
                } else {
                    grid.unSelectAll();
                    selecting = false;
                    ite.forceActiveFocus();
                    mouse.accepted = false;
                }
            } else if (mouse.button == Qt.RightButton) {
                if (grid.selectedCells.includes(ite)) {
                    uiManager.menuFlottantTableau.ouvre(grid);
                    mouse.accepted = true;
                } else {
                    grid.unSelectAll();
                    uiManager.menuFlottantTableau.ouvre(ite);
                    mouse.accepted = true;
                }
            }
        }
        onPositionChanged: {
            if (!selecting)
                return ;

            var tempItem = grid.childAt(mouse.x, mouse.y);
            if (!containsMouse || !tempItem || mouse.buttons != Qt.LeftButton || (tempItem === grid.currentSelectedCell)) {
                return ;
            } else if (tempItem === grid.selectedCells[grid.selectedCells.length - 2]) {
                // si c un recul  on déselect celui en cours et change current
                grid.selectCell(grid.currentSelectedCell);
                grid.currentSelectedCell = tempItem;
            } else {
                //cas simple : nouveau = on ajoute.
                grid.currentSelectedCell = tempItem;
                grid.selectCell(grid.currentSelectedCell);
            }
        }
    }

}
