#include <QtQuickTest>

class Setup : public QObject
{
    Q_OBJECT

public:
    Setup() {}

public slots:
    void applicationAvailable()
    {
        qApp->setApplicationName("blabla");
        qApp->setOrganizationName("une org");
        qApp->setOrganizationDomain("domain.org");
    }
};

QUICK_TEST_MAIN_WITH_SETUP(qmltests, Setup)

#include "main.moc"
