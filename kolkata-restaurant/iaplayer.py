# -*- coding: utf-8 -*-
from utils import *

inc = [(0,1),(0,-1),(1,0),(-1,0)]
inputs = {'w':(-1,0), 'z':(-1,0), 'up':(-1,0)
          , 'left':(0,-1), 'a':(0,-1), 'q':(0,-1)
          , 's':(1,0), 'down':(1,0)
          , 'd':(0,1), 'right':(0,1)}
inputPattern = "\tw\n\t^\n\t|\n  a < --.-- > d\n\t|\n\tˇ\n\ts"

class Player():
    """
    Class Player
    """
    number = 0
    def __init__(self, initState, index, board, strategy=RandomChooserRestaurant):
        # position initiale du joueur
        self.state = initState
        # le plateau dans lequel IA se deplace
        self.board = board
        # identite du joueur pour le plateau, joueur 0, joueur 1 ... etc
        self.index = index
        # les positions precedante du joueur
        self.precState = []
        # son score
        self.score = 0
        # son objectif
        self.goal = None
        # flag qui indique si le score a change
        self.change = False
        # son ID parni les autres joueur
        self.id = Player.number + 1
        # integer static a la classe
        Player.number += 1
        # strategy a apppliquer
        self.strategy = strategy
        
    def process(self):
        """applique recherche de chemin, selection d'objectif et autre methode propre a IA
        """
        raise NotImplementedError("Please implement this method")
    def nextMove(self):
        """
        Retourne la prochaine position
        """
        raise NotImplementedError("Please implement this method")
    
    def toString(self):
        return "Player %0d"%self.id

    def isAccessible(self,state):
        """
        Retourne le boolean indiquant si la position est accessible par le joueur
        """
        return self.board.isAccessible(state)

    def isGoalState(self, pos):
        return self.board.isGoalState(pos)
    
    def chooseGoal(self):
        return self.strategy.chooseRestaurant(self,self.board)
        
    def addScore(self, gain):
        self.change = True
        self.score += gain
        
    def setState(self, state):
        self.precState.append(self.state)
        self.state = state
        self.board.setState(self.index, state)

def human_player_input():
    choice = input("direction :")
    if choice in inputs.keys():
        return inputs[choice]
    return 0,0

class HumanPlayer(Player):
    """
    Class Player Humain
    il attend une entrée pour choisir son prochain coup
    """
    ### RMQ
    ### LAISSER CHOISIR GOAL
    ###
    def process(self):
        pass
    
    def nextMove(self):
        r, c = self.state
        nextStates = board.successor(self.state)
        print(nextStates)
        print(inputPattern)
        nextState = None
        while not nextState:
            nr, nc = human_player_input()
            nextState = None if nr == nc == 0 else (r + nr, c + nc)
            if nextState != None:
                nextState = nextState if self.isAccessible(nextState) else None
        return nextState
    
    def toString(self):
        return "Human Player %0d"%self.id

class RandomPlayer(Player):
    """
    Class Player Random
    il attend une entrée pour choisir son prochain coup
    """
    def process(self):
        if self.goal == None:
            self.chooseGoal()
        if self.change:
            self.change = False
        
    def nextMove(self):
        self.process()
        r, c = self.state
        nextStates = self.board.successor(self.state)
        return rd.choice(nextStates)
    
    def toString(self):
        return "Random Player %0d"%self.id

class AStarPlayer(Player):
    """
    A* pathfinding agent with local repair
    Par default sa strategie est de choisir aleatoirement un restaurant
    """
    def __init__(self, initState, index, board, strategy=RandomChooserRestaurant):
        super().__init__(initState, index, board, strategy)
        self.path = []
        self.step = -1

    def updatePath(self):
        if self.path == []:
            self.path = AStar(self.state, self.goal, self.board)
            self.step = 1 if len(self.path) > 1 else 0
        else:
            # Le chemin ne mene plus a l'objectif
            if self.path[-1] != self.goal:
                self.path = AStar(self.state, self.goal, self.board)
                self.step = 1 if len(self.path) > 1 else 0
                
            #Si le chemin est bloqué
            elif not self.board.isAccessible(self.path[self.step]):
                self.path = AStar(self.state, self.goal, self.board)
                self.step = 1 if len(self.path) > 1 else 0
            # Si reste du chemin a faire
            elif self.step + 1 < len(self.path):
                self.step += 1
            # Sinon, on attent le nouvel objectif
            
    def process(self):
        if self.goal == None:
            self.chooseGoal()
        if self.change:
            self.change = False
            self.chooseGoal()
        self.updatePath()
            
    def nextMove(self):
        self.process()
        return self.path[self.step]
            
    def toString(self):
        return "A* Player %0d"%self.id
