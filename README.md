Hélène HASSAN - Cyriane PINAT

# Projet de Graphique 3D 

##### (Les koalas vont bientôt dominer le monde et mettre des éoliennes partout).


## Description de la scène
- Tout d'abord le terrain est généré procédurallement, entièrement sur GPU afin d'améliorer les performances. 
- Les éoliennes sont des éléments hiérarchiques basés sur des cylindres générés entièrement procéduralement en code Python. Une animation y est mise avec des keyframes afin de faire bouger les pales d'une manière réaliste. Un arbre est créé de la même manière et les parties animées sont le tronc et toutes les branches terminales.
- La scène est éclairée par le soleil et une lumière ambiante.
- Un léger brouillard s'amplifie avec la distance afin d'avoir un rendu agréable à l'oeil. 
- La skybox est présente et est infinie.
- De la fumée s'échappe du volcan, qui est représentée par un système de particules ayant une texture associée aux particules. Vous pouvez remarquer une explosion au début de la scène.
- Un océan entoure tout le terrain et a été généré sur le GPU et on aperçoit le relfet de la skybox sur l'eau. Il est également fait à l'aide de techniques non vues en cours grâce à l'ajout de nouveaux shaders.
- La caméra est entièrement contrôlable grâce au clavier, vous trouverez les touches ci-après. De plus, il est possible de faire apparaître des koalas sur la scène.




## Contrôles au clavier 
### Bouger la position de la caméra
- Z : avancer dans la direction pointée par la caméra
- S : reculer (idem)
- Q : aller à gauche (sur le code on voit qu'il faut appuyer A mais le clavier par défaut est un clavier QWERTY)
- D : aller à droite
- Espace : monter
- Backspace : descendre

### Bouger la rotation de la caméra à l'aide des flèches du clavier
- Flèche du haut : tourne la caméra vers le haut (selon l'axe z)
- Flèche du bas : tourne la caméra vers le bas (selon l'axe z)
- Flèche de gauche : tourne la caméra vers la gauche (i.e. dans le sens antihoraire selon l'axe y)
- Flèche de droite : tourne la caméra vers la droite (i.e.sens horaire) 

Notez que lorsqu'on bouge la caméra jusqu'à 90° vers le haut ou vers le bas, la caméra se bloque. On peut facilement imaginer que la personne qui tient la caméra (si elle existe !) ne va pas se casser le cou et marcher comme une araignée afin d'avoir une caméra retournée. Non. Le plus logique est qu'elle se bloque.

Ces effets sont également possibles à l'aide de la souris, cliquez sur la scène et la caméra bougera avec le pointeur !


### Autres effets
- K : faire apparaître un koala
- P : 
  - 1ère fois : affiche la scène uniquement avec des triangles, 
  - 2ème fois : affiche uniquement les sommets des objets de la scène, 
  - 3ème fois : retour à l'affichage classique.
- C : changer de point de vue, passer du mode caméra au sol au mode caméra en l'air puis inversement.
- Echap : quitte la scène


### Optimisations 

Nous avons décidé de modifier un peu le code donné à l'origine afin d'améliorer nos performances. 
Aussi, les cylindres que nous créons sont créés à l'aide des indices des triangles. En effet, au lieu d'ajouter à chaque fois trois sommets pour créer un triangle (donc ajouter 6 fois (pour les points qui ne sont pas les centres des deux cercles) chaque sommet), nous ajoutons 2 fois toutes les positions puis les indices font le reste du travail. 

