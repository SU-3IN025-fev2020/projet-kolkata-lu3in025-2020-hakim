# -*- coding: utf-8 -*-

# Nicolas, 2020-03-20

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys

from utils import *
import iaplayer as ia

    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'kolkata_6_10'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 60 # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 300 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    #-------------------------------
    # Initialisation
    #-------------------------------
    nbLignes = game.spriteBuilder.rowsize
    nbColonnes = game.spriteBuilder.colsize
    print("lignes", nbLignes)
    print("colonnes", nbColonnes)
    
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets  ramassables (les restaurants)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
    nbRestaus = len(goalStates)
    # on donne le gain par restaurant
    restaurantGain = [1] * nbRestaus
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    # on liste toutes les positions permises
    allowedStates = [(x,y) for x in range(nbLignes) for y in range(nbColonnes)\
                     if (x,y) not in wallStates or goalStates] 
    #-------------------------------
    #initialisation de Board et des Agents
    #-------------------------------
    restaurantBoard = RestaurantBoard(initStates, goalStates, wallStates, nbLignes, nbColonnes, restaurantGain)
    iaplayers = []

    #-------------------------------
    # initialisation du seed
    #-------------------------------
    rd.seed(42)
    #-------------------------------
    # initialisation des strategy disponible
    #-------------------------------
    strategies = [RandomChooserRestaurant, StubbornChooserRestaurant, LessCrowedChooserRestaurant, LessCrowedMoyChooserRestaurant]
    #-------------------------------
    # Placement aleatoire des joueurs, en évitant les obstacles
    # Selection aleaatoire des strategies disponibles
    #-------------------------------
        
    posPlayers = initStates
    
    for j in range(nbPlayers):
        # La nouvelle position
        x,y = random.choice(allowedStates)
        #Creation des agents : A* avec strategiy aleatoire 
        iaplayers.append(ia.AStarPlayer((x,y), j, restaurantBoard, rd.choice(strategies)))
        # mise a jour de leur position
        players[j].set_rowcol(x, y)
        restaurantBoard.playerStates[j] = (x,y)
        restaurantBoard.register(iaplayers[j])
        game.mainiteration()
        
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
    for i in range(iterations):
        print(i, ":")
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement
            # position du joueur courant
            row,col = posPlayers[j]
            # demande de la prochaine position du joueur
            next_row,next_col = iaplayers[j].nextMove()
            
            # Verifie si la prochaine position est valide
            if restaurantBoard.isAccessible((next_row, next_col)):
                # on de place le joueur
                movePlayer(iaplayers[j],players[j],(next_row,next_col))
                print ("\tpos :", j, next_row,next_col)
                game.mainiteration()
                # mise a jour de la position courante du joueur
                col=next_col
                row=next_row
            
            # si tout le monde est à l'emplacement de leur restaurant
            if restaurantBoard.isEveryBodyArrived():
                #donne les gains aux joueurs
                restaurantBoard.giveGain(iaplayers)
                #o = players[j].ramasse(game.layers)
                game.mainiteration()
                print ("\tLes joueur sont à leur restaurant.")
                print ("\tA TABLE !")
               # goalStates.remove((row,col)) # on enlève ce goalState de la liste
                # POSITIONNEMENT ALEATOIRE DES JOUEURS
                for j in range(nbPlayers):
                    # La nouvelle position
                    x,y = random.choice(allowedStates)
                    #deplace les joueurs
                    movePlayer(iaplayers[j],players[j],(x,y))
                    game.mainiteration()
                break
                
    for j in range(nbPlayers):
        print("%d score du joueur %s: %d"%(j, iaplayers[j].toString(), iaplayers[j].score))
    pygame.quit()
    
if __name__ == '__main__':
    main()
