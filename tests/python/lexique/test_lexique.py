"""
Test LExique model
"""
from unittest.mock import patch, MagicMock

import pytest
from PyQt5.QtCore import QModelIndex, Qt
from mycartable.lexique import LexiqueModel, Quizz
from mycartable.lexique import LexiqueProxy, Lexique
from pony.orm import db_session


@pytest.fixture()
def set_locales(ddbr):
    with db_session:
        ddbr.Configuration.add("actives_locales", ["fr_FR", "en_GB"])


pytestmark = pytest.mark.usefixtures("set_locales")


def test_init(fk):
    fk.f_locale(id="fr_FR")
    fk.f_locale(id="en_GB")
    lexons = fk.bulk("f_lexon", 3, td=True)
    model = LexiqueModel()
    # reset
    assert model._data == [
        {"id": lexons[0]["id"], "traductions": [None, None]},
        {"id": lexons[1]["id"], "traductions": [None, None]},
        {"id": lexons[2]["id"], "traductions": [None, None]},
    ]
    assert model.activesLocales == ["en_GB", "fr_FR"]  # order respected
    assert model.availablesLocales == [
        {"active": False, "id": "de_DE", "nom": "🇩🇪 Deutsch"},
        {"active": True, "id": "en_GB", "nom": "🇬🇧 British English"},
        {"active": False, "id": "es_ES", "nom": "🇪🇸 español de España"},
        {"active": True, "id": "fr_FR", "nom": "🇫🇷 français"},
        {"active": False, "id": "it_IT", "nom": "🇮🇹 italiano"},
    ]

    # Rowcount
    assert model.rowCount(QModelIndex()) == 3
    # columnCount
    assert model.columnCount(QModelIndex()) == 2


@pytest.fixture()
def lexons(fk):
    with db_session:
        lex0 = lex = fk.db.Lexon.add(
            [
                {"content": "bonjour", "locale": "fr_FR"},
                {"content": "hello", "locale": "en_GB"},
            ]
        )
        lex1 = lex = fk.db.Lexon.add(
            [
                {"content": "au revoir", "locale": "fr_FR"},
                {"content": "ciao", "locale": "it_IT"},
            ]
        )
        lex2 = lex = fk.db.Lexon.add(
            [
                {"content": "deux", "locale": "fr_FR"},
                {"content": "due", "locale": "it_IT"},
                {"content": "two", "locale": "en_GB"},
            ]
        )
    return lex0, lex1, lex2


def test_data(lexons, fk):
    with db_session:
        fk.db.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT"])
    m = LexiqueModel()
    # ordre de local : en fr it
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "hello"
    assert m.data(m.index(0, 1), Qt.DisplayRole) == "bonjour"
    assert m.data(m.index(0, 2), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 0), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 1), Qt.DisplayRole) == "au revoir"
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "ciao"
    assert m.data(m.index(2, 0), Qt.DisplayRole) == "two"
    assert m.data(m.index(2, 1), Qt.DisplayRole) == "deux"
    assert m.data(m.index(2, 2), Qt.DisplayRole) == "due"

    # ajout d'un lococale donc changement d'ordre
    fk.f_traduction(content="dos", locale="es_ES", lexon=lexons[2])
    with db_session:
        fk.db.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT", "es_ES"])
    m = LexiqueModel()
    # ordre de local :  en, ses,  frn it
    assert m.data(m.index(0, 0), Qt.DisplayRole) == "hello"
    assert m.data(m.index(0, 1), Qt.DisplayRole) == ""
    assert m.data(m.index(0, 2), Qt.DisplayRole) == "bonjour"
    assert m.data(m.index(0, 3), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 0), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 1), Qt.DisplayRole) == ""
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "au revoir"
    assert m.data(m.index(1, 3), Qt.DisplayRole) == "ciao"
    assert m.data(m.index(2, 0), Qt.DisplayRole) == "two"
    assert m.data(m.index(2, 1), Qt.DisplayRole) == "dos"
    assert m.data(m.index(2, 2), Qt.DisplayRole) == "deux"
    assert m.data(m.index(2, 3), Qt.DisplayRole) == "due"


def test_setdata(lexons, fk, qtbot):
    with db_session:
        fk.db.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT"])
    m = LexiqueModel()
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "ciao"
    with qtbot.waitSignal(m.dataChanged):
        assert m.setData(m.index(1, 2), "haha", Qt.EditRole)
    assert m.data(m.index(1, 2), Qt.DisplayRole) == "haha"

    # empty case
    with qtbot.waitSignal(m.dataChanged):
        assert m.setData(m.index(1, 0), "haha", Qt.EditRole)
    assert m.data(m.index(1, 0), Qt.DisplayRole) == "haha"

    assert not m.setData(m.index(99, 99), "haha", Qt.EditRole)  # bad index
    assert not m.setData(m.index(1, 2), "haha", Qt.BackgroundRole)  # bad role
    assert not m.setData(m.index(1, 2), ["haha"], Qt.EditRole)  # base data format


def test_headerData(lexons, ddbr):
    with db_session:
        ddbr.Configuration.add("actives_locales", ["fr_FR", "en_GB", "it_IT"])
    m = LexiqueModel()
    assert "English" in m.headerData(0, Qt.Horizontal, Qt.DisplayRole)
    assert "français" in m.headerData(1, Qt.Horizontal, Qt.DisplayRole)
    assert "italiano" in m.headerData(2, Qt.Horizontal, Qt.DisplayRole)


"""
    TestLexique Proxy
"""


def test_map_from_source(lexons):
    l = Lexique()
    m = l._model
    p = l._proxy
    p.sort(0, Qt.AscendingOrder)
    assert p.mapFromSource(m.index(0, 0)) == p.index(1, 0)

    assert p.mapToSource(p.index(0, 0)) == m.index(1, 0)


def test_removeRow(lexons, ddbr, qtbot):
    l = Lexique()
    with qtbot.waitSignal(l._proxy.rowsAboutToBeRemoved):
        l._proxy.removeRow(1)
    assert l._model.rowCount(QModelIndex()) == 2
    assert l._model._data[0]["id"] == str(lexons[0].id)
    assert l._model._data[1]["id"] == str(lexons[2].id)
    with db_session:
        assert ddbr.Lexon.select().count() == 2
        assert not ddbr.Lexon.get(id=lexons[1].id)


"""
    Test Lexique Controlleur
"""


def test_lexique_init(qtbot):
    l = Lexique()
    assert isinstance(l._model, LexiqueModel)
    assert isinstance(l._proxy, LexiqueProxy)
    assert l._proxy.sourceModel() is l._model
    assert l.model is l._model
    assert l.proxy is l._proxy


def test_add_lexon(lexons):
    l = Lexique()
    assert l.model.rowCount(QModelIndex()) == 3
    assert l.addLexon(
        [
            {"content": "trois", "locale": "fr_FR"},
            {"content": "three", "locale": "en_GB"},
        ]
    )
    assert l.model.rowCount(QModelIndex()) == 4
    assert l.model._data[-1]["traductions"][0]["content"] == "three"
    assert l.model._data[-1]["traductions"][1]["content"] == "trois"


def test_doSort(lexons):
    l = Lexique()
    l.doSort(1)  # debut column 9, sortorder0
    # procy à jour
    assert l._proxy.data(l._proxy.index(0, 1), Qt.DisplayRole) == "au revoir"
    assert l._proxy.data(l._proxy.index(1, 1), Qt.DisplayRole) == "bonjour"
    assert l._proxy.data(l._proxy.index(2, 1), Qt.DisplayRole) == "deux"

    l.doSort(1)  # nouvelle colonne ascending
    # procy à jour
    assert l._proxy.data(l._proxy.index(0, 1), Qt.DisplayRole) == "deux"
    assert l._proxy.data(l._proxy.index(1, 1), Qt.DisplayRole) == "bonjour"
    assert l._proxy.data(l._proxy.index(2, 1), Qt.DisplayRole) == "au revoir"

    l.doSort(1)  # meme colonne toggle
    # proxy à jour
    assert l._proxy.data(l._proxy.index(0, 1), Qt.DisplayRole) == "au revoir"
    assert l._proxy.data(l._proxy.index(1, 1), Qt.DisplayRole) == "bonjour"
    assert l._proxy.data(l._proxy.index(2, 1), Qt.DisplayRole) == "deux"


def test_filter(lexons):
    l = Lexique()
    l.filter(1, "on")
    assert l._proxy.rowCount(QModelIndex()) == 1
    l.filter(1, "o")
    assert l._proxy.rowCount(QModelIndex()) == 2
    l.filter(1, "")
    assert l._proxy.rowCount(QModelIndex()) == 3
    assert l._proxy.sortOrder() == Qt.AscendingOrder


def test_updateActivesLocales(qtbot):
    l = Lexique()
    assert l._model.activesLocales == ["en_GB", "fr_FR"]
    with qtbot.waitSignal(l._model.activesLocalesChanged):
        l.updateActivesLocales("it_IT", True)
    assert l.model.activesLocales == ["en_GB", "fr_FR", "it_IT"]


"""
Test Quizz
"""

@pytest.mark.freeze_time('2017-03-03')
class TestQuizz:

    provider = {
        "question": "hello",
        "question_locale": "en_GB",
        "reponse": "coucou",
        "reponse_locale": "fr_FR",
    }

    @pytest.fixture()
    def q(self):
        data = [
            {
                "traductions": [
                    {
                        "content": "hello",
                        "locale": "en_GB",
                        "modified": "2021-03-02T07:27:31.371659",
                    },
                    {
                        "content": "coucou",
                        "locale": "fr_FR",
                        "modified": "2021-02-02T07:27:31.371659",
                    },
                ]
            }
        ]
        m = LexiqueModel()
        m._data = data
        return Quizz(None, m)

    def test_init(self, q):
        assert q.anteriorite == 14
        assert q.score == 0
        assert q.total == 0
        assert q.questionFlag == ""
        assert q.question == ""
        assert q.reponse == ""
        assert q.reponseFlag == ""
        assert q.showError == False

    def test_question_provider(self, q):
        m = MagicMock(return_value=0)
        with patch("mycartable.lexique.random.randint", m):
            assert q._question_provider() == self.provider

    def test_start_and_new_question(self, q, qtbot):
        q._question_provider = lambda: self.provider
        q.start()
        q._score = 2
        q._total = 4
        assert q.question == "hello"
        assert q.reponse == "coucou"
        assert q.questionFlag is not None
        assert q.reponseFlag is not None
        q._showError = True
        with qtbot.waitSignals(
            [
                q.showErrorChanged,
                q.propositionChanged,
                q.questionChanged,
                q.questionFlagChanged,
                q.reponseChanged,
                q.reponseFlagChanged,
            ]
        ):
            q._new_question()
        assert not q._showError

    @pytest.mark.parametrize(
        "prop, emit, score, total, err_avant, err_apres, res_check",
        [
            ("coucou", True, 1, 1, False, False, True),  # bonne reponse du premier coup
            (
                "coucou",
                False,
                0,
                1,
                True,
                False,
                True,
            ),  # bonne reponse apres corrention
            (
                "bad",
                False,
                0,
                0,
                False,
                True,
                False,
            ),  # mauvaise reponse avantcorrention
            (
                "bad",
                False,
                0,
                0,
                True,
                True,
                False,
            ),  # mauvaise reponse apres corrention
        ],
    )
    def test_checkreponse(
        self, q, prop, emit, score, total, err_avant, err_apres, res_check, qtbot
    ):
        q._question_provider = lambda: self.provider
        q.start()
        q._showError = err_avant
        q.proposition = prop
        if emit:
            with qtbot.waitSignal(q.bonneReponse):
                res = q.checkReponse()
        else:
            res = q.checkReponse()
        assert res is res_check
        assert q.score == score
        assert q.total == total
        assert q.showError == err_apres

    def test_most_recent_trad(self):
        data = {
            "traductions": [
                {"modified": "2021-01-02T07:27:31.371659"},
                {"modified": "2021-05-02T07:27:31.371659"},
                {"modified": "2021-04-02T07:27:31.371659"},
                {"modified": "2021-03-02T07:27:31.371659"},
            ]
        }

        assert Quizz._most_recent_trad(data) == {
            "modified": "2021-05-02T07:27:31.371659"
        }

    def test_timestamp_update(self, q):
        assert q._data == [
            {
                "content": "hello",
                "locale": "en_GB",
                "modified": "2021-03-02T07:27:31.371659",
                "traductions": [
                    {
                        "content": "hello",
                        "locale": "en_GB",
                        "modified": "2021-03-02T07:27:31.371659",
                    },
                    {
                        "content": "coucou",
                        "locale": "fr_FR",
                        "modified": "2021-02-02T07:27:31.371659",
                    },
                ],
            }
        ]

    @pytest.mark.freeze_time("2021-03-14T7:48:05")
    def test__limite_to_anteriorite(
        self,
    ):
        data = [
            {"modified": "2021-03-02T07:27:31.371659"},
            {"modified": "2021-03-14T07:27:31.371659"},
            {"modified": "2021-02-27T07:27:31.371659"},
            {"modified": "2021-01-27T07:27:31.371659"},
            {"modified": "2021-03-10T07:27:31.371659"},
        ]
        assert Quizz._limite_to_anteriorite(data, 14) == [
            {"modified": "2021-03-02T07:27:31.371659"},
            {"modified": "2021-03-14T07:27:31.371659"},
            {"modified": "2021-03-10T07:27:31.371659"},
        ]

    @pytest.mark.freeze_time("2021-03-14T7:48:05")
    def test_prepare_data(
        self,
    ):
        class Model:
            model_data = [
                {
                    "id": "66baa33f-4319-499f-bbcd-5cc88bcf9e74",
                    "traductions": [
                        None,  # important à laisser
                        {
                            "id": "1b393cc3-69f7-4a43-95e0-d2944453150d",
                            "lexon": "66baa33f-4319-499f-bbcd-5cc88bcf9e74",
                            "content": "aaa",
                            "locale": "en_GB",
                            "modified": "2021-03-02T07:27:31.368469",
                        },
                        {
                            "id": "350a1a3f-26b4-4df5-94d6-7c28da42080e",
                            "lexon": "66baa33f-4319-499f-bbcd-5cc88bcf9e74",
                            "content": "bbb",
                            "locale": "fr_FR",
                            "modified": "2021-03-02T07:27:31.371659",
                        },
                    ],
                },
                {
                    "id": "b9b999cc-925a-4aa0-89bd-cc3a1f34b842",
                    "traductions": [
                        {
                            "id": "212d2f1f-11eb-4efd-b944-9ee3dded291a",
                            "lexon": "b9b999cc-925a-4aa0-89bd-cc3a1f34b842",
                            "content": "zzz",
                            "locale": "en_GB",
                            "modified": "2021-01-02T07:31:50.537117",
                        },
                        {
                            "id": "60e2805c-5fc5-4a5c-a43b-3de7decbd67f",
                            "lexon": "b9b999cc-925a-4aa0-89bd-cc3a1f34b842",
                            "content": "zzz",
                            "locale": "fr_FR",
                            "modified": "2021-01-02T07:31:50.539828",
                        },
                    ],
                },
                {
                    "id": "9cfe7a81-40d0-4f7d-ac3e-0d417518db07",
                    "traductions": [
                        {
                            "id": "b0dd8621-fe0c-49f5-9892-879de26082b8",
                            "lexon": "9cfe7a81-40d0-4f7d-ac3e-0d417518db07",
                            "content": "zef",
                            "locale": "en_GB",
                            "modified": "2021-03-02T08:03:10.882939",
                        },
                        {
                            "id": "b9bd6537-8dcc-4e9d-b611-90fcd061a60d",
                            "lexon": "9cfe7a81-40d0-4f7d-ac3e-0d417518db07",
                            "content": "fez",
                            "locale": "fr_FR",
                            "modified": "2021-03-02T08:03:10.885216",
                        },
                    ],
                },
                {
                    "id": "3d26e6fb-ad5a-4505-8eb4-f29b2211e513",
                    "traductions": [
                        {
                            "id": "b90ca256-0822-4586-8797-18c5b090e787",
                            "lexon": "3d26e6fb-ad5a-4505-8eb4-f29b2211e513",
                            "content": "fezezf",
                            "locale": "en_GB",
                            "modified": "2021-01-02T08:03:15.281842",
                        },
                        {
                            "id": "3dcd03c0-7aaf-454a-8b77-a9ad639c1c63",
                            "lexon": "3d26e6fb-ad5a-4505-8eb4-f29b2211e513",
                            "content": "fzezeff",
                            "locale": "fr_FR",
                            "modified": "2021-01-02T08:03:15.283613",
                        },
                    ],
                },
                {
                    "id": "d449c37f-a4ee-47c8-8a6d-4adeecb64327",
                    "traductions": [
                        {
                            "id": "8302a274-96f2-4882-9bff-258484beb4b3",
                            "lexon": "d449c37f-a4ee-47c8-8a6d-4adeecb64327",
                            "content": "aaa",
                            "locale": "en_GB",
                            "modified": "2021-02-02T08:03:20.440033",
                        },
                        {
                            "id": "f2958c45-6cbf-4596-97dc-bc4aa5ed726b",
                            "lexon": "d449c37f-a4ee-47c8-8a6d-4adeecb64327",
                            "content": "dafezf",
                            "locale": "fr_FR",
                            "modified": "2021-02-02T08:03:20.441641",
                        },
                    ],
                },
                {
                    "id": "857f94be-9c76-42a0-9d1e-e5cc5779d1d3",
                    "traductions": [
                        {
                            "id": "3c09b58b-f033-4c12-9c78-6d1311b5c09f",
                            "lexon": "857f94be-9c76-42a0-9d1e-e5cc5779d1d3",
                            "content": "zef",
                            "locale": "en_GB",
                            "modified": "2021-03-02T08:03:28.173293",
                        },
                        {
                            "id": "f5031be9-570f-42a7-9625-7d8d2fb705fe",
                            "lexon": "857f94be-9c76-42a0-9d1e-e5cc5779d1d3",
                            "content": "zef",
                            "locale": "fr_FR",
                            "modified": "2021-03-02T08:03:28.175098",
                        },
                    ],
                },
            ]

        a = Quizz(None, Model())
        assert a._data == [
            {
                "content": "bbb",
                "id": "350a1a3f-26b4-4df5-94d6-7c28da42080e",
                "lexon": "66baa33f-4319-499f-bbcd-5cc88bcf9e74",
                "locale": "fr_FR",
                "modified": "2021-03-02T07:27:31.371659",
                "traductions": [
                    None,  # important à laisser
                    {
                        "content": "aaa",
                        "id": "1b393cc3-69f7-4a43-95e0-d2944453150d",
                        "lexon": "66baa33f-4319-499f-bbcd-5cc88bcf9e74",
                        "locale": "en_GB",
                        "modified": "2021-03-02T07:27:31.368469",
                    },
                    {
                        "content": "bbb",
                        "id": "350a1a3f-26b4-4df5-94d6-7c28da42080e",
                        "lexon": "66baa33f-4319-499f-bbcd-5cc88bcf9e74",
                        "locale": "fr_FR",
                        "modified": "2021-03-02T07:27:31.371659",
                    },
                ],
            },
            {
                "content": "fez",
                "id": "b9bd6537-8dcc-4e9d-b611-90fcd061a60d",
                "lexon": "9cfe7a81-40d0-4f7d-ac3e-0d417518db07",
                "locale": "fr_FR",
                "modified": "2021-03-02T08:03:10.885216",
                "traductions": [
                    {
                        "content": "zef",
                        "id": "b0dd8621-fe0c-49f5-9892-879de26082b8",
                        "lexon": "9cfe7a81-40d0-4f7d-ac3e-0d417518db07",
                        "locale": "en_GB",
                        "modified": "2021-03-02T08:03:10.882939",
                    },
                    {
                        "content": "fez",
                        "id": "b9bd6537-8dcc-4e9d-b611-90fcd061a60d",
                        "lexon": "9cfe7a81-40d0-4f7d-ac3e-0d417518db07",
                        "locale": "fr_FR",
                        "modified": "2021-03-02T08:03:10.885216",
                    },
                ],
            },
            {
                "content": "zef",
                "id": "f5031be9-570f-42a7-9625-7d8d2fb705fe",
                "lexon": "857f94be-9c76-42a0-9d1e-e5cc5779d1d3",
                "locale": "fr_FR",
                "modified": "2021-03-02T08:03:28.175098",
                "traductions": [
                    {
                        "content": "zef",
                        "id": "3c09b58b-f033-4c12-9c78-6d1311b5c09f",
                        "lexon": "857f94be-9c76-42a0-9d1e-e5cc5779d1d3",
                        "locale": "en_GB",
                        "modified": "2021-03-02T08:03:28.173293",
                    },
                    {
                        "content": "zef",
                        "id": "f5031be9-570f-42a7-9625-7d8d2fb705fe",
                        "lexon": "857f94be-9c76-42a0-9d1e-e5cc5779d1d3",
                        "locale": "fr_FR",
                        "modified": "2021-03-02T08:03:28.175098",
                    },
                ],
            },
        ]
