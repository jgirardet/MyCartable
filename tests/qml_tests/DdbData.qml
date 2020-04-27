import QtQuick 2.14

Item {

  // Matiere MIXIN
  property int  currentMatiere: 0

  function setCurrentMatiereFromIndex(value) {
    _setCurrentMatiereFromIndex = value
  }

  function getMatiereIndexFromId(value) {
    return _getMatiereIndexFromId
  }
  property int _getMatiereIndexFromId


  property var matieresList:   [
    {'id': 6, 'nom': 'Lecture', 'annee': 2019, 'activites': [16, 17, 18], 'groupe': 3, 'fgColor': "red", 'bgColor': "blue",},
    {'id': 7, 'nom': 'Mathematiques', 'annee': 2019, 'activites': [19, 20, 21], 'groupe': 2, 'fgColor': "yellow", 'bgColor': "black"},
    {'id': 8, 'nom': 'Géométrie', 'annee': 2019, 'activites': [22, 23, 24], 'groupe': 2, fgColor: "pink", 'bgColor': "orange"},
    {'id': 9, 'nom': 'Histoire', 'annee': 2019, 'activites': [25, 26, 27], 'groupe': 1, fgColor: "red", "bgColor": "green"}
    ]


  property var pagesParSection: [
  {'id': 7, 'nom': 'Leçons', 'famille': 0, 'matiere': 3, 'pages': [
    {'id': 90, 'created': '2019-08-01T20:05:37.013406', 'modified': '2019-08-01T20:05:37.013406', 'titre': "santé foutre d'autres dos truc", 'activite': 7, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 0},
    {'id': 88, 'created': '2019-04-20T04:02:27.952091', 'modified': '2019-04-20T04:02:27.952091', 'titre': 'falloir crever robe emmener début', 'activite': 7, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 0}]},
  {'id': 8, 'nom': 'Exercices', 'famille': 1, 'matiere': 3, 'pages': [
    {'id': 31, 'created': '2020-02-21T00:59:13.917202', 'modified': '2020-02-21T00:59:13.917202', 'titre': 'vérité sûr maman impression simplement', 'activite': 8, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 1},
    {'id': 100, 'created': '2019-10-19T23:58:16.160327', 'modified': '2019-10-19T23:58:16.160327', 'titre': 'seigneur reconnaître supposer voiture souvent', 'activite': 8, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 1}]},
  {'id': 9, 'nom': 'Evaluations', 'famille': 2, 'matiere': 3, 'pages': [
    {'id': 22, 'created': '2020-03-26T15:57:52.204835', 'modified': '2020-03-26T15:57:52.204835', 'titre': 'sauter course envoyer sympa boîte', 'activite': 9, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 2},
    {'id': 25, 'created': '2019-08-04T00:09:19.567436', 'modified': '2019-08-04T00:09:19.567436', 'titre': 'spécial avis appartenir rue jeter', 'activite': 9, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 2},
    {'id': 76, 'created': '2019-06-29T22:48:50.893157', 'modified': '2019-06-29T22:48:50.893157', 'titre': 'ailleurs frapper très plaire femme', 'activite': 9, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 2},
    {'id': 11, 'created': '2019-05-25T00:50:11.225147', 'modified': '2019-05-25T00:50:11.225147', 'titre': 'honneur filer société retourner deux', 'activite': 9, 'lastPosition': null, 'matiere': 3, 'matiereNom': 'Conjugaison', 'matiereFgColor': "red", 'matiereBgColor': "white", 'famille': 2}]}]

  property var currentMatiereItem: {'id': 10, 'nom': 'Géographie', 'annee': 2019, 'activites': [28, 29, 30], 'groupe': 4, 'fgColor': "red", 'bgColor': "white"}

  signal setCurrentMatiereFromIndexSignal(int index)


  // LAYOUTS
  function getLayoutSizes(value) {
    return _getLayoutSizes
  }
  property var _getLayoutSizes: 100
  property color colorFond: "grey"

  // PAGE

  property int currentPage

}