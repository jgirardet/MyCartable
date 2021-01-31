import QtQuick 2.15
import "assets/annotationsValues.mjs" as AssetAnnot

Item {
    id: item

    property int index: 0

    implicitWidth: width
    implicitHeight: height // si pas de taille, pas ed paint
    width: 200 // important pout les tests
    height: 300 //important pour les

    CasTest {
        // en haut a gauche
        // trou
        // en haut a gauche
        //                "style": {
        //                },

        id: testCase

        property var annotdata
        property var annot
        property var img
        property var ref

        function initPre() {
            let img = fk.f("imageSection");
            annotdata = fk.f("annotationDessin", {
                "section": img.id,
                "x": 0.4,
                "y": 0.2,
                "style": {
                    "fgColor": "#0000ff",
                    "bgColor": "#654321",
                    "pointSize": 12,
                    "weight": 10
                },
                "width": 0.4,
                "height": 0.5,
                "startX": 0.3,
                "startY": 0.7,
                "endX": 0.5,
                "endY": 0.9,
                "tool": "rect"
            });
            ref = th.getBridgeInstance(item, "ImageSection", img.id);
            //            annot = th.getBridgeInstance(ref, "AnnotationDessin", annotdata.id);
            annot = ref.model.data(ref.model.index(0, 0), 258);
            params = {
                "annot": annot,
                "referent": item
            };
        }

        function initPost() {
            tryCompare(tested, "available", true);
        }

        function test_init() {
            compare(tested.strokeStyle, "#0000ff");
            compare(tested.fillStyle, "#654321");
            compare(tested.lineWidth, 12);
        }

        function test_opacity() {
            annot.weight = 2;
            //            uiManager.menuFlottantAnnotationDessin = item;
            var nt = createObj("qrc:/qml/annotations/AnnotationDessin.qml", {
                "annot": annot,
                "referent": item
            });
            compare(nt.opacity, 0.2);
        }

        function test_requestPaint_on_fgcolor() {
            var spy = getSpy(tested, "painted");
            tested.strokeStyle = "#33333";
            spy.wait();
        }

        function test_requestPaint_on_bg_color() {
            var spy = getSpy(tested, "painted");
            annot.bgColor = "#33333";
            spy.wait();
        }

        function test_requestPaint_on_lineWidth() {
            var spy = getSpy(tested, "painted");
            annot.pointSize = 999;
            spy.wait();
        }

        function test_checkpointis_NotDraw_data() {
            // strokeREct(24, 205, 16, 30)
            //linewidth = 12
            return [{
                "mx": 1,
                "my": 1,
                "res": true
            }, {
                "mx": 24 + 1,
                "my": 105 + 2,
                "res": false
            }, {
                "mx": 24 + 7,
                "my": 105 + 7,
                "res": true
            }, {
                "mx": 40,
                "my": 135,
                "res": false
            }];
        }

        function test_checkpointis_NotDraw(data) {
            var spy = getSpy(tested, "painted");
            annot.tool = "rect";
            tested.fillStyle = "transparent";
            //            annot.Style = "transparent";
            tested.requestPaint();
            spy.wait();
            compare(tested.checkPointIsNotDraw(data.mx, data.my), data.res);
        }

        function test_draw_data() {
            return [{
                "tool": "trait"
            }, {
                "tool": "rect"
            }, {
                "tool": "ellipse"
            }];
        }

        function test_draw(data) {
            // en pratique on test surtout en regression
            tested.fillStyle = "transparent";
            tested.tool = data.tool;
            var spy = getSpy(tested, "painted");
            //            annot.tool = data.tool;
            //            wait(10000);
            tested.requestPaint();
            spy.wait();
            var img = Qt.createQmlObject("import QtQuick 2.15; Image {source: 'assets/" + data.tool + ".png'}", item);
            var c = Qt.createQmlObject("import QtQuick 2.15; Canvas {height:" + tested.height + ";width:" + tested.width + "}", item);
            tryCompare(c, "available", true);
            var ctx = c.getContext("2d");
            ctx.drawImage(img, 0, 0);
            //            wait(1000);
            compare(tested.toDataURL(), c.toDataURL());
        }

        name: "AnnotationDessin"
        testedNom: "qrc:/qml/annotations/AnnotationDessin.qml"
    }

}
