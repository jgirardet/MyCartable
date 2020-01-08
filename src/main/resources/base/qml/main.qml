import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import MatiereModel 1.0

ApplicationWindow {
    id: page
    width: 800
    height: 400
    visible: true

    MatiereModel {id: matiereModel}
     Label {
    id: tex
    text: "Coucouaaaggg"
    }

    Button {
    y: 50
    id: but
    height: 50
    text: "Bye"//matiereModel.hello()
    onClicked: tex.text = matiereModel.hello()
    }


 }