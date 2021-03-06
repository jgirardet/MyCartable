import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Item {
    id: item

    width: 600
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
            compare(tested.width, 600);
            compare(tested.height, 523);
        }

        function test_Mousearea_init() {
            compare(tested.mousearea.width, tested.width);
            compare(tested.mousearea.height, tested.height);
        }

        function test_left_click_no_modifier_currenttool_is_text() {
            imgInstance.annotationCurrentTool = "text";
            mouseClick(tested, 3, 10, Qt.LeftButton);
            verify(tested.annotations.itemAt(0).item.toString().substr("AnnotationText"));
        }

        function test_left_click_no_modifier_currenttool_is_not_text() {
            imgInstance.annotationCurrentTool = "rect";
            imgInstance.annotationDessinCurrentTool = "rect";
            mouseDrag(tested, 3, 10, 10, 10, Qt.LeftButton);
            compare(tested.annotations.itemAt(0).item.tool, "rect");
        }

        function test_left_click_ctrl_modifier_add_text() {
            imgInstance.annotationCurrentTool = "rect";
            mouseClick(tested, 3, 10, Qt.LeftButton, Qt.ControlModifier);
            verify(tested.annotations.itemAt(0).item.toString().substr("AnnotationText"));
        }

        function test_right_click_ctrl_modifier_add_fillrect() {
            imgInstance.annotationCurrentTool = "text";
            mouseDrag(tested, 3, 10, 10, 10, Qt.RightButton, Qt.ControlModifier);
            compare(tested.annotations.itemAt(0).item.tool, "fillrect");
        }

        function test_left_press_currentool_is_not_text() {
            imgInstance.annotationCurrentTool = "trait";
            imgInstance.annotationDessinCurrentTool = "trait";
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
            compare(tested.menu.visible, false);
            mouseClick(tested, 1, 1, Qt.RightButton);
            compare(tested.menu.visible, true);
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
            imgInstance.annotationDessinCurrentLineWidth = 1;
            imgInstance.annotationDessinCurrentStrokeStyle = "#ffffff";
            imgInstance.annotationCurrentTool = "rect";
            imgInstance.annotationDessinCurrentTool = "trait";
            tested.setStyleFromMenu({
                "style": {
                    "pointSize": 15,
                    "fgColor": "#111111",
                    "tool": "ellipse"
                }
            });
            compare(imgInstance.annotationDessinCurrentLineWidth, 15);
            compare(imgInstance.annotationDessinCurrentStrokeStyle, "#111111");
            compare(imgInstance.annotationCurrentTool, "ellipse");
            compare(imgInstance.annotationDessinCurrentTool, "ellipse");
        }

        function test_setStyleFromMenu_to_text(data) {
            imgInstance.annotationCurrentTool = "rect";
            imgInstance.annotationDessinCurrentTool = "trait";
            tested.setStyleFromMenu({
                "style": {
                    "tool": "text"
                }
            });
            compare(imgInstance.annotationCurrentTool, "text");
            compare(imgInstance.annotationDessinCurrentTool, "fillrect");
        }

        function test_setStyleFromMenu_nothing(data) {
            imgInstance.annotationDessinCurrentLineWidth = 1;
            imgInstance.annotationDessinCurrentStrokeStyle = "#ffffff";
            imgInstance.annotationCurrentTool = "rect";
            imgInstance.annotationDessinCurrentTool = "trait";
            tested.setStyleFromMenu({
            });
            compare(imgInstance.annotationDessinCurrentLineWidth, 1);
            compare(imgInstance.annotationDessinCurrentStrokeStyle, "#ffffff");
            compare(imgInstance.annotationCurrentTool, "rect");
            compare(imgInstance.annotationDessinCurrentTool, "trait");
        }

        function test_annotation_text_removed_if_empty() {
            imgInstance.annotationCurrentTool = "text";
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
            imgInstance.annotationCurrentTool = "text";
            mouseClick(tested);
            compare(tested.annotations.count, 1);
            mouseClick(tested.annotations.itemAt(0), 1, 1, Qt.MiddleButton);
            compare(tested.annotations.count, 0);
        }

        function test_floodfill() {
          // non testé trop compliqué et change l'image de base
        }

        function test_cursor_move() {
            // pour tester les changement de curseur on utiliser le cacheKey
            // qui reste constant pour 2 images identiques.
            let cache_before = th.python("obj.cursor().pixmap().cacheKey()", Window.window);

            imgInstance.annotationCurrentTool = "floodfill";
            mouseMove(tested, 1, 1);
            let cache_flood = th.python("obj.cursor().pixmap().cacheKey()", Window.window);

            imgInstance.annotationCurrentTool = "rect";
            mouseMove(tested, 1, 1);
            let cache_rect = th.python("obj.cursor().pixmap().cacheKey()", Window.window);


            imgInstance.annotationCurrentTool = "floodfill";
            mouseMove(tested, 1, 1);
            let cache_flood2 = th.python("obj.cursor().pixmap().cacheKey()", Window.window);

            compare(cache_before, 0)
            verify(cache_flood != cache_before)
            verify(cache_flood != cache_before)
            verify(cache_flood == cache_flood2)
        }

        function test_cursor_toolchanged() {
            let cache_before = th.python("obj.cursor().pixmap().cacheKey()", tested.mousearea);
            print(cache_before)
             tested.setStyleFromMenu({
                "style": {
                    "tool": "trait"
                }
            });
            let cache_trait = th.python("obj.cursor().pixmap().cacheKey()", tested.mousearea);
            print(cache_trait)
            tested.setStyleFromMenu({
                "style": {
                    "tool": "rect"
                }
            });
            let cache_rect = th.python("obj.cursor().pixmap().cacheKey()", tested.mousearea);
            print(cache_rect)
            verify(cache_trait != cache_before)
            verify(cache_trait != cache_rect)
        }

        name: "ImageSection"
        testedNom: "qrc:/qml/sections/ImageSection.qml"
        params: {
        }
    }

}
