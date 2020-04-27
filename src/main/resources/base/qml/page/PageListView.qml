import QtQuick 2.14
import QtQuick.Controls 2.14
import "operations"
import Operations 1.0
import Tableau 1.0

BasePageListView {
  id: lv
  Component {
    id: textDelegate
    TextSection {
      sectionId: curSectionId
      base: lv
      position: curPosition

    }

  }

  Component {
    id: imageDelegate
    AnnotableImage {
      sectionId: curSectionId
      base: lv
      position: curPosition
    }
  }
  Component {
    id: additionDelegate
    Addition {
      sectionId: curSectionId
      position: curPosition
      model: AdditionModel {
        sectionId: curSectionId // on laisse tout là pour les tests
      }

    }
  }
  Component {
    id: soustractionDelegate
    Soustraction {
      sectionId: curSectionId
      position: curPosition
      model: SoustractionModel {
        sectionId: curSectionId // on laisse tout là pour les tests
      }
    }
  }
  Component {
    id: multiplicationDelegate
    Multiplication {
      sectionId: curSectionId
      position: curPosition
      model: MultiplicationModel {
        sectionId: curSectionId // on laisse tout là pour les tests
      }
    }
  }
  Component {
    id: divisionDelegate
    Division {
      sectionId: curSectionId
      position: curPosition
      model: DivisionModel {
        sectionId: curSectionId // on laisse tout là pour les tests
      }
    }
  }
  Component {
    id: tableauDelegate
    Tableau {
      sectionId: curSectionId
      position: curPosition
      base: lv
      model: TableauModel {
        sectionId: curSectionId // on laisse tout là pour les tests
      }
    }
  }
  delegate: Component {
    Loader {
      id: load
      property int curSectionId: page.id
      property int curPosition: index

      sourceComponent: switch (page.classtype) {
        case "ImageSection": {
          return imageDelegate
        }
        case "TextSection": {
          return textDelegate
        }
        case "AdditionSection": {
          return additionDelegate
        }
        case "SoustractionSection": {
          return soustractionDelegate
        }
        case "MultiplicationSection": {
          return multiplicationDelegate
        }
        case "DivisionSection": {
          return divisionDelegate
        }
        case "TableauSection": {
          return tableauDelegate
        }
      }

    }
  }
}