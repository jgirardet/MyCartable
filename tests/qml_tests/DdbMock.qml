import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import QtTest 1.12
import "echantillon.js" as Sample

Item {
  id: item
  /* beautify preserve:start */
  property var sp: Sample.samples
  property var currentMatiere: 3
  property var currentPage: 0
  property var evaluationsList: sp.evaluationsList
  property var exercicesList: sp.exercicesList
  property var lessonsList: sp.lessonsList
  property var matieresListNom: sp.matieresListNom
  property var pageModel: []
  property var pagesParSection: sp.pagesParSection
  property var recentsModel: Sample.samples.recentsModel
  property var setCurrentMatiereFromIndex
  /* beautify preserve:end */

  signal setCurrentMatiereFromIndexSignal(int index)

  function addAnnotation(content) {
    return _addAnnotation
  }

  function addSection(page, content) {
    return _addSection
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

  function recentsItemClicked(itemId, matiere) {
    _recentsItemClicked = [itemId, matiere]
  }



  function updateAnnotation(itemId, params) {
    _updateAnnotation = [itemId, params]
  }

  // Sous cette ligne, uniquement du non existent dans le vrai ddb
  // fake value des fonction

  /* beautify preserve:start */
  property int _addAnnotation: 0
  property int _addSection: sp.addSection
  property var _deleteAnnotation
  property int _getLayoutSizes: 100
  property int _getMatiereIndexFromId: 1
  property var _loadAnnotations: []
  property var _loadSection: {}
  property var  _recentsItemClicked: []
  property var _updateAnnotation: null
  /* beautify preserve:end */
  Component {
    id: compspyc
    SignalSpy {
     // target: item
      //signalName: "setCurrentMatiereFromIndexSignal"
    }
  }

  function getSpy(targetObj, signaltxt) {
    return compspyc.createObject(item, {
      "target": targetObj,
      "signalName": signaltxt
    })
  }

  function reset_sp() {
    sp = Sample.samples
  }

  // Component.onCompleted: sp = Sample.samples
}