# Scenarios des interactions

L'idée est de décrire les mécanismes en jeu pour s'y retrouver
dans toutes les intéractions

La descriptoin commence quand l'action est déclenché. On ne traite pas ici du déclencheur

## Procédures qui appellent un ordonnanceur central
Les étapes sont décrites à partir du déclenchement de l'ordonnanceur

### Nouvelle Page
- appel à la base de donnée : Page.nouvelle_page() qui retourne les nouvelles datas.
- On recharge la Page central avec les nouvelles données
- async
    - recharger les récents
    - switcher la matiere
    
## Change Page
- On recharche la page centrale avec nouvelles données
- async
    - switcher la matiere   

## Procédures isolées    

### Recharger la page centrale
- sauvegarder les éventuelles modifs en cours.
- supprimer/creer ou reset composant en cours
- charge le text en priorité
- async:
    - afficher les images et autres trucs lourd.

### Recharger les récents
- resetModel 

### switcher la matiere
- depuis un id de Page
- une requete pour tout setter tout ?