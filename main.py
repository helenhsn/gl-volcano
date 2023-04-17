#!/usr/bin/env python3


from core import Viewer

def main():

    # instructions
    instructions = """\n\n\n####################### UTILISATION DU CLAVIER #######################
    - Z : avancer dans la direction pointée par la caméra
    - S : reculer (idem)
    - Q : aller à gauche (sur le code on voit qu'il faut appuyer A mais le clavier par défaut est un clavier QWERTY)
    - D : aller à droite
    - Espace : monter
    - Backspace : descendre
    - Click gauche : arrête/démarre le mouvement de la caméra.


    - Flèche du haut : tourne la caméra vers le haut (selon l'axe z)
    - Flèche du bas : tourne la caméra vers le bas (selon l'axe z)
    - Flèche de gauche : tourne la caméra vers la gauche (i.e. dans le sens antihoraire selon l'axe y)
    - Flèche de droite : tourne la caméra vers la droite (i.e.sens horaire) 

    - K : faire apparaître un koala
    - P : 
        - 1ère fois : affiche la scène uniquement avec des triangles, 
        - 2ème fois : affiche uniquement les sommets des objets de la scène, 
        - 3ème fois : retour à l'affichage classique
    - C : changer de point de vue :
        - vue distante
        - vue de près en dessous des éoliennes, parmi les koalas
        - vue de l'océan
        - vue de l'île de derrière
        - vue près du mouton qui cherche à dominer le monde
    - F : active/désactive le fog
    - Echap : quitte la scène
######################################################################\n\n"""

    CHUNK_SIZE = 256 #nb of vertices per chunk side
    
    viewer = Viewer(instructions, size=CHUNK_SIZE)
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()
