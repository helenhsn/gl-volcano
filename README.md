Hélène HASSAN - Cyriane PINAT

# Projet de Graphique 3D

##### (Les koalas vont bientôt dominer le monde et mettre des éoliennes partout).

**Note importante** : Le code fourni à l'origine par les professeurs a été largement modifié car le but du projet était de faire les choses par nous-mêmes et d'apprendre, pas de réutiliser du code sans savoir ce qu'il fait. Au final, seules la structure pour load des fichiers .obj, les classes liées aux animations (Node) et les fonctions pour les matrices dans transform.py. La caméra de la scène est notre propre caméra même si elles n'est pas parfaite... (nous n'avons pas eu le temps de nous pencher sur l'utilisation des quaternions donc nous avons préféré utiliser quelque chose que nous connaissons malgré tout : les angles d'Euler).
- Une gamma correction est appliquée sur les objets de la scène et nous utilisons le modèle de Blinn-Phong (utilisation du halfway vector) pour éclairer nos objets (le modèle de Ward ne rend pas très bien sur l'océan avec la skybox choisie...).


## Contrôles au clavier (donnés dans le terminal)
### Bouger la position de la caméra
- **Z** : avancer dans la direction pointée par la caméra
- **S** : reculer (idem)
- **Q** : aller à gauche (sur le code on voit qu'il faut appuyer A mais le clavier par défaut est un clavier QWERTY)
- **D** : aller à droite
- **Espace** : monter
- **Backspace** : descendre
- **Click gauche** : arrête/démarre le mouvement de la caméra.

### Bouger la rotation de la caméra à l'aide des flèches du clavier
- **Flèche du haut** : tourne la caméra vers le haut (selon l'axe z)
- **Flèche du bas** : tourne la caméra vers le bas (selon l'axe z)
- **Flèche de gauche** : tourne la caméra vers la gauche (i.e. dans le sens antihoraire selon l'axe y)
- **Flèche de droite** : tourne la caméra vers la droite (i.e.sens horaire) 

Notez que lorsqu'on bouge la caméra jusqu'à 90° vers le haut ou vers le bas, la caméra se bloque. On peut facilement imaginer que la personne qui tient la caméra (si elle existe !) ne va pas se casser le cou et marcher comme une araignée afin d'avoir une caméra retournée. Non. Le plus logique est qu'elle se bloque.

Ces effets sont également possibles à l'aide de la souris, cliquez sur la scène et la caméra bougera avec le pointeur !


### Autres effets
- **K** : faire apparaître un koala
- **P** : 
  - **1ère fois** : affiche la scène uniquement avec des triangles (wireframe mode), 
  - **2ème fois** : affiche uniquement les vertices de la scène, 
  - **3ème fois** : retour à l'affichage classique.
- **C** : changer de point de vue, passer du mode caméra au sol au mode caméra en l'air puis inversement.
- **Echap** : quitte la scène



## Éléments choisis pour répondre aux critères du sujet

- L'**élément hiérarchique avec géométrie procédurale et animé avec des keyframes** correspond aux éoliennes qui sont générées avec des cylindres (déformés). Une animation y est mise avec des keyframes afin de faire bouger les pales d'une manière réaliste. Un arbre est créé de la même manière et les parties animées sont le tronc et toutes les branches terminales.
- Le **contrôle au keyboard** concerne principalement l'utilisation de la caméra et l'apparition des koalas sur le terrain. La caméra est entièrement contrôlable grâce au clavier. 
- La **skybox** est présente et est infinie (on ne peut y sortir) : elle est basée sur un cubemap (cube sur lequel on colle une texture 3D de type samplerCube).
- Deux **systèmes de particules** sont présents dans la scène : un pour la fumée qui s'échappe du volcan (contenant environ 32000 particules) et un pour les petits splash de lave sortant du volcan (environ 500 particules). Les deux systèmes sont mis à jour entièrement sur GPU (via l'utilisation de compute shaders & shader storage buffer objects). La fumée est représentée par un particle atlas trouvé sur internet (pas assez de temps pour faire nos propres textures de feu...).
- L'**océan** est généré entièrement sur GPU via une pipeline de compute shaders qui permettent de faire tourner l'algorithme de Fast Fourier Transform en parallèle. À la fin de la pipeline, on récupère une texture contenant la displacement map (déplacement horizontal et vertical des vagues) ainsi qu'une texture contenant le slope vector en chaque point de la texture ainsi que le jacobien. Ces deux textures (de taille 256*256) sont ensuite samplées dans les vertex & fragment shaders pour éclairer l'océan (calcul de normale, etc). L'ajout de la skybox a également permis d'ajouter un effet de réflexion sur l'eau (nous n'avons pas mis de réfraction car nous n'avons pas eu le temps de travailler l'aspect "sous l'eau"). Le calcul du jacobien (qui permet de souligner la crête des vagues) permet de donner un joli effet avec la réflexion.
- Le **terrain** est généré entièrement sur GPU via l'utilisation d'un compute shader appelé une seule fois en début de programme. Ce shader génère une normale map et une height map qui est samplée dans les vertex & fragment shaders (toujours le même principe). La fonction de hauteur de terrain couple l'utilisation de gaussiennes pour la forme du volcan et de fBm (fractional Brownian motion) avec du value noise (piqué sur Shadertoy, le lien est dans le compute shader) pour faire un effet un peu caillouteux à la surface. Les fBm sont utilisées égalment pour la forme de l'île (cela permet de casser l'aspect symétrique aux bords de l'île). Nous avons essayé de donner une forme un peu bizarre au sommet du volcan en ajoutant d'autres fonctions en plus des deux gaussienne de base.
- Le **terrain tout comme l'océan** correspondent à une grille de meshes qui contiennent chacun 256 x 256 vertices (espacé d'un certain facteur fixé à 4 au moment du rendu pour générer un terrain plus grand avec moins de points = optimisation). Au total, chaque grille de meshes correspond à un carré d'aire égale à 64x256x4 unités.
- Le **brouillard** est généré en post-processing via l'utilisation de frame buffer objects pour stocker la couleur de chaque pixel de la scène ainsi que le depth buffer (distances de chaque point de l'espace à la caméra). Ces deux buffers permettent de donner une nouvelle couleur à la scène en fonction de la distance point-caméra (view distance). Visuellement, le brouillard s'amplifie avec la distance à la caméra et dépend également de l'altitude de la caméra



### Optimisations 

**Notes** : De nombreuses optimisations ont été faites au niveau du gpu pour que le framerate soit suffisamment acceptable : nous le faisons tourner à 30fps environ (source : RenderDoc) mais ce dernier diminue beaucoup lorsque l'on se rapproche de la fumée du volcan. 30 fps ne paraît pas énorme aux premiers abords mais notre terrain est très grand et comme nous n'avons pas eu le temps d'implémenter un level of details (LOD), chaque mesh de notre scène possède le même niveau de détails (ce qui est très coûteux...). Nous aurions aimé pouvoir implémenter le LOD via  l'utilisation de tessellation shaders car il s'agit d'une optimisation majeure lorsque l'on génère des terrains larges grands comme celui-ci (chaque mesh a le même niveau de détails, actuellement).Vous remarquerez que le terrain a été coupé sous l'eau car nous sommes censés voir la scène qu'au dessus de l'eau...
Nous aurions aimé aussi avoir le temps de faire une plus jolie skybox (l'utilisation d'un cubemap n'est pas très optimisée car nous affichons 6 textures alors que nous en voyons 3 au maximum dans la scène...).

Parmi les optimisations réalisées :

- **GPU instancing** pour l'océan (via l'utilisation d'un ssbo contenant les model matrices de chaque mesh de l'océan) : pratique si on veut afficher un grand nombre de grilles mais pour que cela soit le cas il faudrait coupler cela avec un LOD.
- **Utilisation de compute shaders** : ces derniers ont été largement utilisés pour optimiser au maximum notre programme (océan, terrain, particules). Il s'agit d'une optimisation majeure car cette dernière permet de profiter pleinement des particularités du GPU (calcul en parallèle). Note : l'utilisation de SSBOs couplés avec les compute shaders permet de générer un grand nombre de particules (si nous voulions utiliser des textures, nous aurions été limités par OpenGL très vite).
- **Post-processing** via l'utilisation de frame buffers. Au lieu d'appeler une même fonction qui calcule le facteur de brouillard dans tous les shaders de notre programme, nous générons d'abord notre scène en entier puis lui appliquons les effets que nous voulons.
- **Génération des meshes optimisée** : les cylindres que nous créons sont créés à l'aide des indices des triangles (utilisation d'un EBO). En effet, au lieu d'ajouter à chaque fois trois sommets pour créer un triangle (donc ajouter 6 fois (pour les points qui ne sont pas les centres des deux cercles) chaque sommet), nous ajoutons 2 fois toutes les positions puis les indices font le reste du travail. Les meshes du terrain/océan sont également créés en espaçant les vertices pour aggrandir le terrain avec un coût moindre.

