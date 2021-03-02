from mycartable.undoredo import BaseCommand

"""
Tout seul pour des problèmes d'import circulaires
"""


class BasePageCommand(BaseCommand):
    def __init__(self, *, page: "Page", **kwargs):
        super().__init__(**kwargs)
        self.page = page
        self.position: int = 0  # position où a été ajouté la section
