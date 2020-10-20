import MyCartable 1.0
import QtQuick 2.15
import "assets/annotationsValues.mjs" as AssetAnnot

Item {
    id: item

    property var points: AssetAnnot.pointsMainLevee
    property var model
    property var section

    CasTest {
        function initPre() {
            item.section = fk.f("imageSection");
            params = {
                "anchors.fill": item
            };
        }

        function initPreCreate() {
        }

        function initPost() {
        }

        function test_init() {
            compare(tested.points, []);
        }

        function test_Draw() {
            tryCompare(tested, "available", true);
            tested.mouse = {
                "mouseX": item.points[0].x * item.width,
                "mouseY": item.points[0].y * item.height
            };
            tested.startDraw();
            let spy = getSpy(tested, "painted");
            for (const p of item.points.slice(1, item.points.length - 1)) {
                tested.mouse = {
                    "mouseX": p.x * item.width,
                    "mouseY": p.y * item.height
                };
                tested.requestPaint();
                tested.paint(item.childrenRect); // marche avec les 2 sans wait, pourquoi ?
            }
            //            tested.save("tests/qml/assets/point.png"); // garder c pour les tests
            compare(points, item.points);
        }

        function test_end_draw() {
            tryCompare(tested, "available", true);
            tested.mouse = {
                "mouseX": item.points[0].x * item.width,
                "mouseY": item.points[0].y * item.height
            };
            tested.startDraw();
            tested.points = item.points;
            tested.endDraw();
            verify(!tested.painting);
            let res = JSON.parse(fk.getSet("ImageSection", item.section.id, "annotations")[0].points);
            let respoints = res.map((x) => {
                return Qt.point(x.x, x.y);
            });
            compare(respoints, item.points);
        }

        name: "MainLevee"
        testedNom: "qrc:/qml/annotations/MainLevee.qml"
    }

    model: AnnotationModel {
        sectionId: dao && item.section ? item.section.id : ""
        dao: ddb
    }

}
