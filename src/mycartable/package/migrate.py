"""
Ici sont expliquées les migrations chaque changement dans la ddb.
"""

"""
type:
    1 ajout d'une foreignKey : Optional <=> Optional:
        1 Si nouvelle table : ajouter la relation dans la nouvelle table via:
        new_field_de_new_class =  Optional("OldClasse", column="new_field_de_new_class")
        Du coup rien à faire de plus
        - Si 2 anciennes table: ???
        
"""


migrations_list = {"1.3.0": {"type": "1.1"}}
