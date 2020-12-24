import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 200
    height: 600

    CasTest {
        // onPaint called

        property var model
        property var canvas
        property var imgsection
        property var imgInstance

        function initPre() {
            imgsection = fk.f("imageSection", {
                "path": "tst_AnnotableImage.png"
            });
            imgInstance = th.getBridgeInstance(item, "ImageSection", imgsection.id);
            params = {
                "sectionItem": item,
                "section": imgInstance
            };
        }

        function initPost() {
            tryCompare(tested, "progress", 1); // permet le temps de chargement async de l'image
            canvas = findChild(tested, "canvasFactory");
        }

        function test_init() {
            tryCompare(tested, "implicitWidth", item.width);
        }

        function test_img_load_init() {
            verify(tested.source.toString().endsWith("tst_AnnotableImage.png"));
            compare(tested.width, 200);
            compare(tested.height, 174); // 669 * item.width / 767
        }

        function test_Mousearea_init() {
            compare(tested.mousearea.width, tested.width);
            compare(tested.mousearea.height, tested.height);
        }

        function test_left_click_no_modifier_currenttool_is_text() {
            uiManager.annotationCurrentTool = "text";
            mouseClick(tested, 3, 10, Qt.LeftButton);
            verify(tested.annotations.itemAt(0).item.toString().substr("AnnotationText"));
        }

        function test_left_click_no_modifier_currenttool_is_not_text() {
            uiManager.annotationCurrentTool = "rect";
            uiManager.annotationDessinCurrentTool = "rect";
            mouseDrag(tested, 3, 10, 10, 10, Qt.LeftButton);
            compare(tested.annotations.itemAt(0).item.tool, "rect");
        }

        function test_left_click_ctrl_modifier_add_text() {
            uiManager.annotationCurrentTool = "rect";
            mouseClick(tested, 3, 10, Qt.LeftButton, Qt.ControlModifier);
            verify(tested.annotations.itemAt(0).item.toString().substr("AnnotationText"));
        }

        function test_right_click_ctrl_modifier_add_fillrect() {
            uiManager.annotationCurrentTool = "text";
            mouseDrag(tested, 3, 10, 10, 10, Qt.RightButton, Qt.ControlModifier);
            compare(tested.annotations.itemAt(0).item.tool, "fillrect");
        }

        function test_left_press_currentool_is_not_text() {
            uiManager.annotationCurrentTool = "trait";
            uiManager.annotationDessinCurrentTool = "trait";
            mousePress(tested, 3, 10, Qt.LeftButton);
            verify(canvas.painting); // painting True == startDraw called
            verify(!canvas.useDefaultTool);
            compare(canvas.tool, "trait");
        }

        function test_release_enddraw() {
            mousePress(tested, 3, 10, Qt.RightButton, Qt.ControlModifier);
            verify(canvas.painting); // painting True == startDraw called
            mouseRelease(tested, 3, 10, Qt.RightButton);
            verify(!canvas.painting);
        }

        function test_move_draw() {
            mousePress(tested, 3, 10, Qt.RightButton, Qt.ControlModifier);
            verify(!canvas.visible);
            mouseMove(tested, 33, 100);
            tryCompare(canvas, "visible", true);
        }

        function test_right_click_affiche_menu() {
            uiManager.menuFlottantImage = createObj("qrc:/qml/menu/MenuFlottantImage.qml");
            compare(uiManager.menuFlottantImage.visible, false);
            mouseClick(tested, 1, 1, Qt.RightButton);
            compare(uiManager.menuFlottantImage.visible, true);
        }

        function test_annotation_repeter() {
            var rep = findChild(tested, "repeater");
            compare(rep.count, 0);
            tested.model.addAnnotation("AnnotationText", {
                "x": 100,
                "y": 100,
                "width": item.width,
                "height": item.height
            });
            //            wait(2000);
            compare(rep.count, 1);
        }

        function test_CanvasFactory_init() {
            compare(canvas.mouse, tested.mousearea);
            compare(canvas.width, tested.width);
            compare(canvas.height, tested.height);
        }

        function test_setStyleFromMenu_all(data) {
            uiManager.annotationDessinCurrentLineWidth = 1;
            uiManager.annotationDessinCurrentStrokeStyle = "#ffffff";
            uiManager.annotationCurrentTool = "rect";
            uiManager.annotationDessinCurrentTool = "trait";
            tested.setStyleFromMenu({
                "style": {
                    "pointSize": 15,
                    "fgColor": "#111111",
                    "tool": "ellipse"
                }
            });
            compare(uiManager.annotationDessinCurrentLineWidth, 15);
            compare(uiManager.annotationDessinCurrentStrokeStyle, "#111111");
            compare(uiManager.annotationCurrentTool, "ellipse");
            compare(uiManager.annotationDessinCurrentTool, "ellipse");
        }

        function test_setStyleFromMenu_to_text(data) {
            uiManager.annotationCurrentTool = "rect";
            uiManager.annotationDessinCurrentTool = "trait";
            tested.setStyleFromMenu({
                "style": {
                    "tool": "text"
                }
            });
            compare(uiManager.annotationCurrentTool, "text");
            compare(uiManager.annotationDessinCurrentTool, "fillrect");
        }

        function test_setStyleFromMenu_nothing(data) {
            uiManager.annotationDessinCurrentLineWidth = 1;
            uiManager.annotationDessinCurrentStrokeStyle = "#ffffff";
            uiManager.annotationCurrentTool = "rect";
            uiManager.annotationDessinCurrentTool = "trait";
            tested.setStyleFromMenu({
            });
            compare(uiManager.annotationDessinCurrentLineWidth, 1);
            compare(uiManager.annotationDessinCurrentStrokeStyle, "#ffffff");
            compare(uiManager.annotationCurrentTool, "rect");
            compare(uiManager.annotationDessinCurrentTool, "trait");
        }

        function test_annotation_text_removed_if_empty() {
            uiManager.annotationCurrentTool = "text";
            mouseClick(tested);
            compare(tested.annotations.count, 1);
            let timer = findChild(tested.annotations.itemAt(0), "timerRemove");
            compare(timer.running, true);
            timer.stop();
            timer.interval = 0;
            timer.start();
            tryCompare(tested.annotations, "count", 0);
        }

        function test_baseannotation_removed_if_middle_click() {
            uiManager.annotationCurrentTool = "text";
            mouseClick(tested);
            compare(tested.annotations.count, 1);
            mouseClick(tested.annotations.itemAt(0), 1, 1, Qt.MiddleButton);
            compare(tested.annotations.count, 0);
        }

        function test_floodfill() {
            uiManager.annotationCurrentTool = "floodfill";
            uiManager.annotationDessinCurrentStrokeStyle = "blue";
            let mname = "floodFill";
            th.mock(imgInstance, mname);
            mouseClick(tested, 34, 54);
            verify(th.mock_called(imgInstance, mname));
            let args = th.mock_call_args_list(imgInstance, mname);
            compare(args[0], [imgInstance.id, "#0000ff", Qt.point(34 / tested.width, 54 / tested.height)]);
            th.unmock(imgInstance, mname);
        }

        function test_cursor_move() {
            uiManager.annotationCurrentTool = "floodfill";
            uiManager.annotationDessinCurrentStrokeStyle = "blue";
            let mname = "setImageSectionCursor";
            th.mock(imgInstance, mname);
            mouseMove(tested, 1, 1);
            verify(th.mock_called(imgInstance, mname));
            th.unmock(imgInstance, mname);
        }

        function test_cursor_toolchanged() {
            let mname = "setImageSectionCursor";
            th.mock(imgInstance, mname);
            tested.setStyleFromMenu({
                "style": {
                    "tool": "trait"
                }
            });
            verify(th.mock_called(imgInstance, mname));
            th.unmock(imgInstance, mname);
        }

        name: "ImageSection"
        testedNom: "qrc:/qml/sections/ImageSection.qml"
        params: {
        }
    }

}
