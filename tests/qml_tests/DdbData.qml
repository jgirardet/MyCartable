/* on changes:
matiereList : annee en moins
              famille, actiite, position
              */

import QtQuick 2.15
import QtTest 1.15

Item {
    //    print("##############  DDBDATA NON A JOURS##########")
    // PAGE
    // IMAGE
    // important pout les test
    // important pout les test
    // ne pas changer cet object (sauf adapter)
    // SECTION
    // text section
    // session
    //    property var anneeActive
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */
    /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */

    // Matiere MIXIN
    property int currentMatiere: 0
    property int _getMatiereIndexFromId
    property var matieresList: [{
        "id": 6,
        "nom": "Lecture",
        "annee": 2019,
        "activites": [16, 17, 18],
        "groupe": 3,
        "fgColor": "red",
        "bgColor": "blue"
    }, {
        "id": 7,
        "nom": "Mathematiques",
        "annee": 2019,
        "activites": [19, 20, 21],
        "groupe": 2,
        "fgColor": "yellow",
        "bgColor": "black"
    }, {
        "id": 8,
        "nom": "Géométrie",
        "annee": 2019,
        "activites": [22, 23, 24],
        "groupe": 2,
        "fgColor": "pink",
        "bgColor": "orange"
    }, {
        "id": 9,
        "nom": "Histoire",
        "annee": 2019,
        "activites": [25, 26, 27],
        "groupe": 1,
        "fgColor": "red",
        "bgColor": "green"
    }]
    property var pagesParSection: [{
        "id": 7,
        "nom": "Leçons",
        "famille": 0,
        "matiere": 3,
        "pages": [{
            "id": 90,
            "created": "2019-08-01T20:05:37.013406",
            "modified": "2019-08-01T20:05:37.013406",
            "titre": "santé foutre d'autres dos truc",
            "activite": 7,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 0
        }, {
            "id": 88,
            "created": "2019-04-20T04:02:27.952091",
            "modified": "2019-04-20T04:02:27.952091",
            "titre": "falloir crever robe emmener début",
            "activite": 7,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 0
        }]
    }, {
        "id": 8,
        "nom": "Exercices",
        "famille": 1,
        "matiere": 3,
        "pages": [{
            "id": 31,
            "created": "2020-02-21T00:59:13.917202",
            "modified": "2020-02-21T00:59:13.917202",
            "titre": "vérité sûr maman impression simplement",
            "activite": 8,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 1
        }, {
            "id": 100,
            "created": "2019-10-19T23:58:16.160327",
            "modified": "2019-10-19T23:58:16.160327",
            "titre": "seigneur reconnaître supposer voiture souvent",
            "activite": 8,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 1
        }]
    }, {
        "id": 9,
        "nom": "Evaluations",
        "famille": 2,
        "matiere": 3,
        "pages": [{
            "id": 22,
            "created": "2020-03-26T15:57:52.204835",
            "modified": "2020-03-26T15:57:52.204835",
            "titre": "sauter course envoyer sympa boîte",
            "activite": 9,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 2
        }, {
            "id": 25,
            "created": "2019-08-04T00:09:19.567436",
            "modified": "2019-08-04T00:09:19.567436",
            "titre": "spécial avis appartenir rue jeter",
            "activite": 9,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 2
        }, {
            "id": 76,
            "created": "2019-06-29T22:48:50.893157",
            "modified": "2019-06-29T22:48:50.893157",
            "titre": "ailleurs frapper très plaire femme",
            "activite": 9,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 2
        }, {
            "id": 11,
            "created": "2019-05-25T00:50:11.225147",
            "modified": "2019-05-25T00:50:11.225147",
            "titre": "honneur filer société retourner deux",
            "activite": 9,
            "lastPosition": null,
            "matiere": 3,
            "matiereNom": "Conjugaison",
            "matiereFgColor": "red",
            "matiereBgColor": "white",
            "famille": 2
        }]
    }]
    property var currentMatiereItem: {
        "id": 10,
        "nom": "Géographie",
        "annee": 2019,
        "activites": [28, 29, 30],
        "groupe": 4,
        "fgColor": "red",
        "bgColor": "white"
    }
    property var _getLayoutSizes: 100
    property color colorFond: Qt.rgba(130, 134, 138, 1)
    property color colorMainMenuBar: Qt.rgba(83 / 255, 93 / 255, 105 / 255, 1)
    property color colorPageToolBar: Qt.rgba(197 / 255, 197 / 255, 197 / 255, 1)
    property string fontMain: "Verdana"
    property var _setStyle: {
        "id": 2,
        "family": "",
        "underline": true,
        "pointSize": null,
        "strikeout": false,
        "weight": null,
        "annotation": null,
        "bgColor": "red",
        "fgColor": "yellow"
    }
    property int currentPage
    property var _newPage
    property string currentTitre
    property var _setCurrentTitre
    // RECENTS
    property var recentsModel: [{
        "id": 23,
        "created": "2020-04-14T18:03:41.495701",
        "modified": "2020-04-14T18:03:41.495701",
        "titre": "professeur secret espoir clé discuter",
        "activite": 39,
        "lastPosition": null,
        "matiere": 13,
        "matiereNom": "Musique",
        "matiereFgColor": "red",
        "matiereBgColor": "orange",
        "famille": 2
    }, {
        "id": 99,
        "created": "2019-10-24T10:04:08.546545",
        "modified": "2019-10-24T10:04:08.546545",
        "titre": "pousser grand-mère sur sept disparaître",
        "activite": 18,
        "lastPosition": null,
        "matiere": 6,
        "matiereNom": "Lecture",
        "matiereFgColor": "blue",
        "matiereBgColor": "pink",
        "famille": 2
    }, {
        "id": 10,
        "created": "2019-12-11T21:43:38.560859",
        "modified": "2019-12-11T21:43:38.560859",
        "titre": "écrire selon rencontrer refuser continuer",
        "activite": 17,
        "lastPosition": null,
        "matiere": 6,
        "matiereNom": "Lecture",
        "matiereFgColor": "green",
        "matiereBgColor": "white",
        "famille": 1
    }, {
        "id": 15,
        "created": "2019-06-04T05:27:19.212722",
        "modified": "2019-06-04T05:27:19.212722",
        "titre": "frapper tort fuir ravir tas",
        "activite": 14,
        "lastPosition": null,
        "matiere": 5,
        "matiereNom": "Rédaction",
        "matiereFgColor": "black",
        "matiereBgColor": "purple",
        "famille": 1
    }]
    property var _addAnnotation: [{
        "id": 1,
        "relativeX": 0.3,
        "relativeY": 0.4,
        "section": 1,
        "classtype": "Stabylo",
        "relativeWidth": 0.5,
        "relativeHeight": 0.6
    }, {
        "id": 1,
        "family": "",
        "underline": false,
        "pointSize": null,
        "strikeout": false,
        "weight": null,
        "annotation": 1,
        "bgColor": "transparent",
        "fgColor": "black"
    }]
    property var _deleteAnnotation
    property var _loadAnnotations: [[{
        "id": 7,
        "relativeX": 0.4,
        "relativeY": 0.5,
        "section": 3796,
        "classtype": "AnnotationText",
        "text": "un annotation"
    }, {
        "id": 1,
        "family": "",
        "underline": false,
        "pointSize": null,
        "strikeout": false,
        "weight": null,
        "annotation": 1,
        "bgColor": "orange",
        "fgColor": "red"
    }], [{
        "id": 6,
        "relativeX": 0.48,
        "relativeY": 0.1,
        "section": 3796,
        "classtype": "Stabylo",
        "relativeWidth": 0.226457,
        "relativeHeight": 0.0796915
    }, {
        "id": 12,
        "family": "",
        "underline": false,
        "pointSize": null,
        "strikeout": false,
        "weight": null,
        "annotation": 1,
        "bgColor": "blue",
        "fgColor": "black"
    }], [{
        "id": 5,
        "relativeX": 0.302691,
        "relativeY": 0.383033,
        "section": 3796,
        "classtype": "AnnotationText",
        "text": "fzefzefzef"
    }, {
        "id": 44,
        "family": "",
        "underline": true,
        "pointSize": null,
        "strikeout": false,
        "weight": null,
        "annotation": 1,
        "bgColor": "transparent",
        "fgColor": "orange"
    }], [{
        "id": 4,
        "relativeX": 0.163677,
        "relativeY": 0.18509,
        "section": 3796,
        "classtype": "Stabylo",
        "relativeWidth": 0.0941704,
        "relativeHeight": 0.059126
    }, {
        "id": 5,
        "family": "",
        "underline": false,
        "pointSize": null,
        "strikeout": false,
        "weight": null,
        "annotation": 1,
        "bgColor": "transparent",
        "fgColor": "black"
    }]]
    property var _updateAnnotation: {
        "id": 1,
        "relativeX": 0.44,
        "relativeY": 0.93,
        "section": 1,
        "classtype": "AnnotationText",
        "text": "bla"
    }
    property var _pivoterImage
    property real annotationTextBGOpacity: 0.3
    property var _addSection
    property var _loadSection: {
        "id": 3796,
        "created": "2019-04-19T22:44:14.176013",
        "modified": "2019-04-19T22:44:14.176013",
        "page": 88,
        "position": 9,
        "classtype": "ImageSection",
        "path": "qrc:/tests/tst_AnnotableImage.png",
        "annotations": [4, 5, 6, 7]
    }
    property var _loadSectionParams
    property var _removeSection
    property var _getMenuAnnees: [{
        "id": 2018,
        "niveau": "ce2"
    }, {
        "id": 2019,
        "niveau": "cm1"
    }]
    property var _updateEquation
    property var _updateEquationParams
    property var _isEquationFocusable: true
    property var _getTextSectionColor: "red"
    property var _initTableauDatas
    property var _updateCell
    property var _newUser
    property var currentUser: {
        /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */

    }
    property var _newAnnee
    property var anneeActive
    property var _peuplerLesMatieresParDefault
    property var _insertColumn
    property var _insertRow
    property var _removeRow
    property var _removeColumn
    property var _nbColonnes
    property var _appendRow
    property var _appendColumn
    property var _getGroupeMatieres
    property var _getMatieres
    property var _applyGroupeDegrade
    property var _getActivites
    property var _moveActiviteTo
    property var _removeActivite
    property var _updateActiviteNom
    property var _updateMatiereNom
    property var _updateGroupeMatiereNom

    signal setCurrentMatiereFromIndexSignal(int index)
    signal newPageCreated(var un)
    signal recentsItemClicked(int page, int matiere)
    signal changeAnnee(int annee)

    function setCurrentMatiereFromIndex(value) {
        _setCurrentMatiereFromIndex = value;
    }

    function getMatiereIndexFromId(value) {
        return _getMatiereIndexFromId;
    }

    // LAYOUTS
    function getLayoutSizes(value) {
        return _getLayoutSizes;
    }

    function setStyle(styleId, content) {
        var res = Object.assign(_setStyle, content);
        _setStyle = [styleId, content];
        return res;
    }

    function newPage(activite) {
        _newPage = activite;
    }

    function setCurrentTitre(value) {
        _setCurrentTitre = value;
    }

    function addAnnotation(content) {
        var backup = _addAnnotation;
        _addAnnotation = content;
        return backup;
    }

    function deleteAnnotation(sectionid) {
        _deleteAnnotation = sectionid;
    }

    function loadAnnotations(section) {
        return _loadAnnotations;
    }

    function updateAnnotation(anotid, dico) {
        var backup = _updateAnnotation;
        _updateAnnotation = [anotid, dico];
        return backup;
    }

    function pivoterImage(id, sens) {
        _pivoterImage = [id, sens];
    }

    function addSection(sectionid, content) {
        _addSection = [sectionid, content];
        return sectionid + 1;
    }

    function loadSection(sectionid) {
        _loadSectionParams = sectionid;
        return _loadSection;
    }

    function removeSection(sectoinid, index) {
        _removeSection = [sectoinid, index];
    }

    // Settings
    function getMenuAnnees() {
        return _getMenuAnnees;
    }

    // Equation
    function updateEquation(sectionid, content, curseur, event) {
        _updateEquationParams = [sectionid, content, curseur, event];
        return _updateEquation;
    }

    function isEquationFocusable(content, curseur) {
        var backup = _isEquationFocusable;
        _isEquationFocusable = [content, curseur];
        return backup;
    }

    function getTextSectionColor(arg) {
        return _getTextSectionColor;
    }

    // tableau
    function initTableauDatas(arg) {
        return _initTableauDatas;
    }

    function updateCell(secId, mdy, mdx, content) {
        _updateCell = [secId, mdy, mdx, content];
    }

    function insertColumn(tab, value) {
        _insertColumn = [tab, value];
    }

    function insertRow(tab, value) {
        _insertRow = [tab, value];
    }

    function removeRow(tab, value) {
        _removeRow = [tab, value];
    }

    function removeColumn(tab, value) {
        _removeColumn = [tab, value];
    }

    function appendRow(arg) {
        _appendRow = [arg];
    }

    function appendColumn(arg) {
        _appendColumn = [arg];
    }

    function nbColonnes(secId) {
        let toReturn = _nbColonnes;
        _nbColonnes = [secId];
        return toReturn;
    }

    function newUser(nom, prenom) {
        _newUser = [nom, prenom];
    }

    function newAnnee(annee, classe) {
        _newAnnee = [annee, classe];
    }

    function peuplerLesMatieresParDefault(anne) {
        _peuplerLesMatieresParDefault = [anne];
    }

    function getGroupeMatieres(annee) {
        let toReturn = _getGroupeMatieres;
        //        _getGroupeMatieres = [annee];
        return toReturn;
    }

    function getMatieres(matiere) {
        let toReturn = _getMatieres;
        //        _getMatieres = [matiere];
        return toReturn;
    }

    function applyGroupeDegrade(id, couleur) {
        let toReturn = _applyGroupeDegrade;
        _applyGroupeDegrade = [id, couleur];
        return toReturn;
    }

    function getActivites(matid) {
        let toReturn = _getActivites;
        //        _getActivites = [matid];
        return toReturn;
    }

    function moveActiviteTo(id, pos) {
        let toReturn = _moveActiviteTo;
        _moveActiviteTo = [id, pos];
        return toReturn;
    }

    function removeActivite(id) {
        let toReturn = _removeActivite;
        _removeActivite = [id];
        return toReturn;
    }

    function updateActiviteNom(id, text) {
        let toReturn = _updateActiviteNom;
        _updateActiviteNom = [id, text];
        return toReturn;
    }

    function updateMatiereNom(id, text) {
        let toReturn = _updateMatiereNom;
        _updateMatiereNom = [id, text];
        return toReturn;
    }

    function updateGroupeMatiereNom(id, nom) {
        _updateGroupeMatiereNom = [id, nom];
    }

    Component.onCompleted: {
        /* on changes:
matiereList : annee en moins
              famille, actiite, position
              */

    }
}
