# import pytest
# from PySide2.QtCore import Signal
# from package.page.tableau_section import TableauModel, create_tableau
#
#
# @pytest.fixture
# def tt():
#     class Dbo:
#         recentsModelChanged = Signal()
#         sectionIdChanged = Signal()
#
#     class MockTableau(TableauModel):
#         def __call__(self, rows, columns):
#             rows, columns, datas = create_tableau(rows, columns)
#             self.params["rows"] = rows
#             self.params["columns"] = columns
#             self.params["datas"] = datas["datas"]
#
#     MockTableau.ddb = Dbo()
#     a = MockTableau()
#     return a
#
#
# #
# # @pytest.fixture
# # def tt_db(dao):
# #     class TempTableau(TableauModel):
# #         ddb = dao
# #
# #         def __call__(self,rows, columns):
# #             self.f_entry = f_tableau(rows, columns)
# #             print(self.f_entry)
# #             self.sectionId = self.f_entry.id
# #             print(self.sectionId)
# #
# #     return TempTableau()
# #
# # class TestTableauModel:
# #     def test_rowCount(self):
