import QtQuick 2.15
//import QtQuick.Window 2.15
//import "qrc:/qml/layouts"

Item {
    //    Rectangle {
    //        id: leftbread
    //        width: 200
    //        height: ham.height
    //        color: "red"
    //    }

    id: item

    width: 1200
    height: 800

    property string comptxt : `
    import QtQuick 2.15
    import "qrc:/qml/layouts"
    SandwichLayout {
        id: tested
        width: 600
        height: item.height
        widthLimit: 600

        hamAndCheese: Rectangle {
            width: 1000
            height: parent.height
            color: "purple"
            border.color: "black"
            border.width: 10
        }

        leftBread: Rectangle {
            width: 100
            height: tested.height
            color: "green"
        }

        rightBread: Rectangle {
            width: 100
            height: tested.height
            color: "yellow"
        }

    }
    `
    CasTest {
        //        property Item ham: ham

        function initPre() {
          tested = createTemporaryQmlObject(comptxt, item)
          tested.leftBread.parent.animDuration = 0
          tested.rightBread.parent.animDuration = 0
        }

        function initPreCreate() {
        }

        function initPost() {
        }

        function test_init() {
            compare(tested.breadsState, "small");
            compare(tested.state, "smallsandwich");
        }


        function test_width_greater_then_widthlimit() {
            tested.width = tested.widthLimit + 100
            compare(tested.state, "bigsandwich");
            compare(tested.breadsState, "big")
        }
        function test_smallsandwich_smallbread() {
          compare(tested.leftBread.width, 20) // widthsmall defaut
          compare(tested.hamAndCheese.width, tested.width-40) // width- 2 x widthSmall
        }

        function test_smallsandwich_bigbread() {
          tested.breadsState= "big"
          tryCompare(tested.leftBread,"width", 250) // bigwidth
          compare(tested.hamAndCheese.width, tested.width-40) // width- 2 x widthSmall
        }

        function test_bigsandwich() {
          tested.state = "bigsandwich"
          compare(tested.hamAndCheese.width, tested.width-500) // width- 2 x bigWidth
        }

        function test_mouse_smallsandwich() {
          mouseMove(tested.leftBread, 10,10) //in
          tryCompare(tested.leftBread,"width", 250) // bigwidth
          compare(tested.hamAndCheese.width, tested.width-40) // width- 2 x widthSmall

          mouseMove(tested.leftBread,-1,-1) // out
          tryCompare(tested.leftBread,"width", 20) // widthsmall defaut
        }

        function test_mouse_bigsandwich() {
          //setup
          tested.width = tested.widthLimit + 100
          tryCompare(tested.leftBread,"width", 250) // widthsmall defaut

          mouseMove(tested.leftBread, 10,10) //in
          compare(tested.leftBread.width, 250) // bigwidth
          mouseMove(tested.leftBread,-1,-1) // out
          compare(tested.leftBread.width, 250) // bigwidth
        }


        autocreate: false
        name: "Sandwich"
        testedNom: "qrc:/qml/layouts/SandwichLayout.qml"
        params: {
        }
    }

}
