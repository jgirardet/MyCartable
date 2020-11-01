import QtQuick 2.15

Item {
    id: item

    property var _newDessin: null
    property var model

    width: 200
    height: 200

    CasTest {
        //      params = {
        //        "sectionId": 3796,
        //        "sectionItem": item
        //      }

        property var mouse

        function initPre() {
        }

        function initPreCreate() {
        }

        function initPost() {
            tested.mouse = {
                "mouseX": 50,
                "mouseY": 60
            };
            item._newDessin = null;
            tested.width = item.width;
            tested.height = item.height;
        }

        function test_init_test() {
            compare(tested.tool, "fillrect");
            compare(tested.lineWidth, 3);
            compare(tested.fillStyle, "#00000000");
            compare(tested.strokeStyle, "#000000");
            verify(!tested.visble);
            verify(!tested.painting);
        }

        function test_start_draw() {
            tested.startDraw(false);
            verify(!tested.useDefaultTool);
            tested.startDraw(true);
            verify(tested.useDefaultTool);
            compare(tested.startX, 50);
            compare(tested.startY, 60);
            compare(tested.opacity, 1);
            verify(tested.painting);
            compare(tested.width, item.width);
        }

        function test_endDraw_no_move_no_drax() {
            tested.startDraw(false);
            tested.mouse = {
                "mouseX": 50,
                "mouseY": 60
            };
            tested.endDraw();
            compare(item._newDessin, null);
        }

        function test_endDraw_simple_draw() {
            tested.startDraw(false);
            tested.mouse = {
                "mouseX": 100,
                "mouseY": 120
            };
            tested.endDraw(23);
            //      print(JSON.stringify(item._newDessin))
            //      compare(item._newDessin[0], 23)
            compare(JSON.stringify(item._newDessin[1]), "{\"x\":0.2425,\"y\":0.2925,\"startX\":0.02830188679245283,\"startY\":0.023809523809523808,\"endX\":0.9716981132075472,\"endY\":0.9761904761904762,\"width\":0.265,\"height\":0.315,\"tool\":\"fillrect\",\"lineWidth\":3,\"strokeStyle\":{\"r\":0,\"g\":0,\"b\":0,\"a\":1,\"hsvHue\":-1,\"hsvSaturation\":0,\"hsvValue\":0,\"hslHue\":-1,\"hslSaturation\":0,\"hslLightness\":0,\"valid\":true},\"fillStyle\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0,\"hsvHue\":-1,\"hsvSaturation\":0,\"hsvValue\":0,\"hslHue\":-1,\"hslSaturation\":0,\"hslLightness\":0,\"valid\":true},\"opacity\":1}");
            verify(!tested.useDefaultTool);
            verify(!tested.visble);
        }

        function test_endDraw_blue_rect() {
            uiManager.annotationDessinCurrentTool = "rect";
            uiManager.annotationDessinCurrentStrokeStyle = "blue";
            uiManager.annotationDessinCurrentLineWidth = 10;
            tested.startDraw(false);
            tested.mouse = {
                "mouseX": 100,
                "mouseY": 120
            };
            tested.endDraw(23);
            var res = item._newDessin[1];
            compare(res.strokeStyle, "#0000ff");
            compare(res.lineWidth, 10);
            compare(res.tool, "rect");
        }

        function test_endDraw_trait() {
            uiManager.annotationDessinCurrentTool = "trait";
            tested.endDraw(23);
            compare(item._newDessin[1].tool, "trait");
        }

        name: "CanvasFactory"
        testedNom: "qrc:/qml/annotations/CanvasFactory.qml"
    }

    model: Item {
        function addAnnotation(a, b) {
            item._newDessin = [a, b];
        }

    }

}
