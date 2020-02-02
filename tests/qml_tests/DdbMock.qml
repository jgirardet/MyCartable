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

  function addAnnotation(content) {
    return _addAnnotation
  }

  function deleteAnnotation(id) {
    _deleteAnnotation = id
  }

  function getLayoutSizes(quoi) {
    return _getLayoutSizes
  }

  function getMatiereIndexFromId(id) {
    return _getMatiereIndexFromId
  }

  function loadSection(sec) {
    return _loadSection
  }

  function loadAnnotations(sec) {
    return _loadAnnotations
  }

  function updateAnnotationText(itemId, text) {
    _updateAnnotationText = [itemId, text]
  }

  // Sous cette ligne, uniquement du non existent dans le vrai ddb
  // fake value des fonction

  /* beautify preserve:start */
  property int _addAnnotation: 0
  property var _deleteAnnotation
  property int _getLayoutSizes: 100
  property int _getMatiereIndexFromId: 1
  property var _loadAnnotations: []
  property var _loadSection: {}
  property var _updateAnnotationText: null
  /* beautify preserve:end */
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