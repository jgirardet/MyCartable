import QtQuick 2.14



Component.onCompleted: {
    loader.setSource(`qrc:/qml/annotations/${dessin.classtype}.qml`, {
      "datas": datas,
      "referent": referent,
    })
  }