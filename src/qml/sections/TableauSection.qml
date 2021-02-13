import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "qrc:/qml/menu"

Item {
    id: root

    required property Item sectionItem
    required property QtObject section
    property alias menu: menuFlottantTableau

    width: grid.width
    height: grid.height
    onSectionChanged: grid.reload()

    MenuFlottantTableau {
        id: menuFlottantTableau
    }

    Connections {
        function onColonnesChanged() {
            grid.reload();
        }

        function onLignesChanged() {
            grid.reload();
        }

        target: section
    }

    GridLayout {
        id: grid

        property var selectedCells: []
        property var currentSelectedCell: null

        function reload() {
            repeater.model = section.initTableauDatas();
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
        columns: section.colonnes
        columnSpacing: 3
        rowSpacing: 3

        Connections {
            function onCellUpdated(params) {
                let ite = repeater.itemAt(params._index);
                ite.updatable = false;
                if ("texte" in params)
                    ite.text = params["texte"];

                if ("style" in params) {
                    let st = params.style;
                    if ("fgColor" in st)
                        ite.color = st.fgColor;

                    if ("bgColor" in st)
                        ite.background.color = st.bgColor;

                    if ("underline" in st)
                        ite.font.underline = st.underline;

                    if ("pointSize" in st)
                        ite.font.pointSize = st.pointSize ? st.pointSize : 14;

                }
                ite.forceActiveFocus();
                ite.cursorPosition = params._cursor;
                ite.updatable = true;
            }

            target: section
        }

        Repeater {
            //            model: root.section ? grid.reload() : 0

            id: repeater

            objectName: "repeater"

            delegate: TextArea {
                id: tx

                property int colonne: modelData.x
                property int ligne: modelData.y
                property string tableauSection: section.id
                property bool updatable: true
                property int cursorAvant

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
                    if (updatable)
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
                    let cursor_avant = cursorAvant != undefined ? cursorAvant : length;
                    let cursor = cursorPosition != undefined ? cursorPosition : length;
                    section.updateCell(modelData.y, modelData.x, content, cursor_avant, cursor);
                }

                focus: true
                Layout.minimumHeight: 10
                Layout.fillHeight: true
                Layout.fillWidth: true
                selectByMouse: true
                font.pointSize: modelData.style.pointSize ? modelData.style.pointSize : 14 // à changer aussi dans convert
                font.underline: modelData.style.underline
                color: modelData.style.fgColor
                Component.onCompleted: {
                    text = modelData.texte;
                    onTextChanged.connect(setText);
                }
                Keys.onPressed: {
                    var isMove = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Down, Qt.Key_Right].includes(event.key);
                    if ([Qt.Key_Control, Qt.Key_Shift].includes(event.key)) {
                        //on ignore controle seul
                        return ;
                    } else if ((event.key == Qt.Key_Z) && (event.modifiers & Qt.ControlModifier)) {
                        if (event.modifiers & Qt.ShiftModifier)
                            section.undoStack.redo();
                        else
                            section.undoStack.undo();
                    } else if ((isMove && (event.modifiers & Qt.ControlModifier)) || (event.key == Qt.Key_Right && cursorPosition == length) || (event.key == Qt.Key_Left && cursorPosition == 0) || (event.key == Qt.Key_Up && isFirstLine()) || (event.key == Qt.Key_Down && isLastLine())) {
                        changeCase(event);
                        event.accepted = true;
                    } else if (([Qt.Key_Minus, Qt.Key_Plus].includes(event.key)) && (event.modifiers & Qt.ControlModifier)) {
                        setPointSize(event.key);
                        event.accepted = true;
                    } else {
                        cursorAvant = cursorPosition;
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
                    if (ite)
                        ite.forceActiveFocus();

                    mouse.accepted = false;
                }
            } else if (mouse.button == Qt.RightButton) {
                if (grid.selectedCells.includes(ite)) {
                    root.menu.ouvre(grid);
                    mouse.accepted = true;
                } else {
                    grid.unSelectAll();
                    root.menu.ouvre(ite);
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
