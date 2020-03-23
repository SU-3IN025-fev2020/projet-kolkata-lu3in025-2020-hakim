# -*- coding: utf-8 -*-
import random as rd
import numpy as np
import heapq as hp

inc = [(0,1),(0,-1),(1,0),(-1,0)]

#-------------------------------
# Fonction et methode pour le main
#-------------------------------
def movePlayer(joueur, player, state):
    player.set_rowcol(state[0], state[1])
    joueur.setState(state)
#-------------------------------
# CLASS DEFINIT UN PROBLEME
#-------------------------------
class Problem():
    def __init__(self, shape, constraint):
        self.shape = shape
        self.dim = len(shape)
        # un array indiquant accessibilite de chaque etat possible
        self.mat = np.ones(shape, dtype=int)
        # met a jour les obstacle
        for c in constraint:
            self.mat[c] = 0
        # un array contenant les 4 direction possible exemple pour 2D : [[1,0],[0,1], [-1,0],[0,-1]]
        self.inc = np.vstack((np.identity(self.dim, dtype=int), np.where(np.identity(self.dim, dtype =int) == 1, -1, 0)))
        
    def isAccessible(self, state):
        return self.isIn(state) and self.mat[state] == 1

    def successor(self, state):
        """tuple[int] -> List[tuple[int]]
        """
        neighboor = [tuple(np.asarray(state) + i) for i in self.inc if self.isIn(tuple(np.asarray(state) + i))]
        return [s for s in neighboor if self.isAccessible(s)]
        
    def isIn(self, state):
        try:
            self.mat[state]
            return True
        except IndexError:
            return False
        
    def isConstraint(self, state):
        return self.mat[state] == 0
    
    def setAccessibility(self, state, accessible):
        """ tuple[int*] * boolean -> void
        """
        self.mat[state] = 1 if accessible else 0
    
class Board(Problem):
    def __init__(self, initStates, goalStates, wallStates, maxRow, maxCol, playerOverlap=False):
        super().__init__((maxRow, maxCol), wallStates)
        self.playerStates = initStates
        self.goalStates = goalStates
        self.playerOverlap = playerOverlap
        # Si on autorise pas que les joueur se superpose
        if not playerOverlap:
            for state in self.playerStates:
                self.setAccessibility(state, False)
        
    def isGoalState(self, state):
        return state in self.goalStates

    def setGoalStates(self, goalStates):
        self.goalStates = goalStates
    
    def setState(self, indexPlayer, state):
        if not self.playerOverlap:
            self.setAccessibility(self.playerStates[indexPlayer], True)
            self.setAccessibility(state, False)
        self.playerStates[indexPlayer] = state
    
    def show(self):
        tab = [["_" if self.isAccessible((i,j)) else "#" for i in range(self.shape[0])] for j in range(self.shape[1])]
        for r,c in self.playerStates:
            tab[r][c] = 'j'
        for r,c in self.goalStates:
            tab[r][c] = 'g'
        for i in range(len(tab)):
            tab[i] = ' '.join(tab[i])
        print('\n'.join(tab))

class RestaurantBoard(Board):
    def __init__(self, initStates, goalStates, wallStates, maxRow, maxCol, restaurantGain):
        super().__init__(initStates, goalStates, wallStates, maxRow, maxCol, playerOverlap=True)
        # Indique l'objectif de chaque joueur, par l'intermediaire d'un dictionnaire, Goal[indexJoueur] : goalState 
        self.goals = {}
        self.restaurantGain = restaurantGain
        #Dict[indexRestaurant:List[indexJoueur]]
        self.playerWaitingIn = {i:None for i in range(len(initStates))}
        #Dict[indexRestaurant:List[indexJoueur]]
        self.isWaiting = {i:[] for i in range(len(goalStates))}
        
    def setState(self, indexPlayer, state):
        # Si on autorise pas le superposition des joueurs
        if not self.playerOverlap:
            self.setAccessibility(self.playerStates[indexPlayer], True)
            self.setAccessibility(state, False)
        # Si le joueur attendais dans une file d'attente d'un restaurant
        if self.playerWaitingIn[indexPlayer] != None:
            # index du restaurant
            indexResto = self.playerWaitingIn[indexPlayer]
            # Retire de la file d'attente du restaurant
            self.isWaiting[indexResto].remove(indexPlayer)
            # on le retire de l'etat d'attente
            self.playerWaitingIn[indexPlayer] = None
        # mise a jour de sa position
        self.playerStates[indexPlayer] = state
        # Si mtn le joueur a atteint son restaurant
        if self.goals[indexPlayer] == state:
            # On l'ajoute dans la file d'attente du restaurant
            self.isWaiting[self.goalStates.index(state)].append(indexPlayer)
            # On le met en etat d'attente
            self.playerWaitingIn[indexPlayer] = self.goalStates.index(state)
        
    def setPlayerGoal(self, indexPlayer, goalState):
        if not self.isGoalState(goalState):
            raise NotValidGoal("the choosen goalState {0} is not in the list of goalStates {1}".format(goalState, self.goalStates))
        self.goals[indexPlayer] = goalState

    def isEveryBodyArrived(self):
        for indexPlayer in self.playerWaitingIn.keys():
            if self.playerWaitingIn[indexPlayer] == None:
                return False
        return True
    
    def giveGain(self, players):
        """
        Donne les gains aux joueurs
        """
        indexPlayersGain = []
        for r in range(len(self.isWaiting)):
            if len(self.isWaiting[r]) > 0:
                indexPlayer = rd.choice(self.isWaiting[r])
                indexPlayersGain.append(indexPlayer)
        for player in players:
            indexResto = self.playerWaitingIn[player.index]
            gain = self.restaurantGain[indexResto] if player.index in indexPlayersGain else 0
            player.addScore(gain)

#-------------------------------
# CLASS & METHODE pour IA
#-------------------------------
def AStar(state, goal, problem):
        nodeInit = Node(state)
        frontiere = [(nodeInit.g + manhattan(state, goal), nodeInit)]
        reserve = {}
        bestNode = nodeInit
        # FRONTIERE NON VIDE ET OBJECTIF NON ATTEINT
        while frontiere != [] and goal != bestNode.state:
            # SELECTIONNE LE PLUS PETIT G DE LA FRONTIERE
            (min_f, bestNode) = hp.heappop(frontiere)
            # NOEUD JAMAIS EXPLORE
            if not(bestNode in reserve):
                reserve[bestNode] = bestNode.g
                # EXPLORE LES NOEUDS VOISINS
                nodes = bestNode.expand(problem)
                for node in nodes:
                    f = node.g + manhattan(node.state, goal)
                    # AJOUTE FRONTIERE NOEUD VOISINS
                    hp.heappush(frontiere, (f, node))
        # RETOURNE LE CHEMIN VERS SE NOEUD
        return bestNode.path()

def manhattan(pos1, pos2):
    return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])

class Node():
    number = 0
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.successor = []
        self.g = 0 if parent == None else parent.g + 1
        self.id = Node.number
        Node.number += 1
        
    def __eq__(self, other):
        """
        other -> boolean Or NotImplemented
        Retourne True si les noeud contienne le meme etat, sinon False
        """
        if isinstance(other, Node):
            return self.state == other.state
        return False
    
    def __lt__(self, other):
        """
        other -> boolean Or NotImplemented
        retourne True si le coût du noeud actuelle est inférieur au noeud 
        spécifié.
        """
        if isinstance(other, self.__class__):
            return self.g < other.g
        return NotImplemented
    
    def __hash__(self):
        return hash(self.state)
    
    def __repr__(self):
        return 'Node(%d,%d)'%(self.state[0], self.state[1])
    
    def __str__(self):
        return 'Node(%d,%d)'%(self.state[0], self.state[1])
    
    def expand(self, problem):
        if self.successor == []:
            self.successor = [Node(s, self) for s in problem.successor(self.state)]
        return self.successor
    
    def path(self):
        node, res = self, [self.state]
        while node.parent != None:
            res.insert(0,node.parent.state)
            node = node.parent
        return res
#-------------------------------
# STRATEGY DE SELECTION DU RESTAURANT
#-------------------------------
class IStrategy:
    def chooseRestaurant(player, restaurentProblem):
        """
        Methode pour choisir le restaurant
        """
        raise NotImplemented("Implementer l'algorithme de decision")

class RandomChooserRestaurant(IStrategy):
    """Choisi aleatoirement le restaurant
    """
    def chooseRestaurant(player, restaurantBoard):
        goal = rd.choice(restaurantBoard.goalStates)
        player.goal = goal
        restaurantBoard.setPlayerGoal(player.index, goal)

class StubornChooserRestaurant(IStrategy):
    """Pour le meme joueur choisi le meme restaurant
    """
    def chooseRestaurant(player, restaurantBoard):
        goal = player.index % len(restaurantBoard.goalStates)
        player.goal = goal
        restaurantBoard.setPlayerGoal(player.index, goal)

#-------------------------------
# CUSTOM EXCEPTION
#-------------------------------

class NotValidGoal(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        print('calling str')
        if self.message:
            return 'NotValidGoal, {0}'.format(self.message)
        else:
            return 'NotValidGoal, the choosen goalState is not in the list of goalStates'
