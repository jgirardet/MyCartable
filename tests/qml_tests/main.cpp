#include <QtQuickTest>
#include <QQmlEngine>
#include <QQmlContext>
class Setup : public QObject
{
    Q_OBJECT public:
    Setup() {
        qDebug() << "setup" ;
    }public slots:
    void applicationAvailable() {
        qDebug() << "appli available" ;
    }
    void qmlEngineAvailable(QQmlEngine *engine)
    {
        //CircleCommon circleCommon;
        engine->addImportPath("/home/jimmy/dev/cacahuete/MyCartable/tests/qml_tests/mmm/");
        qDebug() << QCoreApplication::applicationDirPath();
    }
};
QUICK_TEST_MAIN_WITH_SETUP(qml_tests, Setup)
#include "main.moc"