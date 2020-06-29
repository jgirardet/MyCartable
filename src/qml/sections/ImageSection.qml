import MyCartable 1.0
import QtQuick 2.15
import "qrc:/qml/annotations"

ImageSectionBase {

    model: AnnotationModel {
        sectionId: root.sectionId
    }

}
