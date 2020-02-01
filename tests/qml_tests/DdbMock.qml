import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtTest 1.12
Item {
  id: item
  property
  var currentMatiere: 3
  property
  var currentPage: 0
  property
  var evaluationsList: ["eval1", "eval2", "eval3"]
  property
  var exercicesList: ["exo1", "exo2", "exo3"]
  property
  var lessonsList: ["leçon1", "leçon2", "leçon3"]
  property
  var matieresListNom: ["Français", "Histoire", "Géo"]
  property
  var setCurrentMatiereFromIndex
  signal setCurrentMatiereFromIndexSignal(int index)

  function getLayoutSizes(quoi) {
    return _getLayoutSizes
  }

  function getMatiereIndexFromId(id) {
    return _getMatiereIndexFromId
  }
  // Sous cette ligne, uniquement du non existent dans le vrai ddb
  // fake value des fonction
  property
  var _getLayoutSizes: 100
  property
  var _getMatiereIndexFromId: 1
  Component {
    id: compspyc
    SignalSpy {
      id: spyc
      target: item
      signalName: "setCurrentMatiereFromIndexSignal"
    }
  }

  function getSpy(signaltxt, targetObj) {
    return compspyc.createObject(item, {
      "target": targetObj,
      "signalName": signaltxt
    })
  }
}