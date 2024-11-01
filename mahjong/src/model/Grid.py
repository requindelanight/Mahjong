# -*- coding: utf-8 -*-

###########################################
#                libraries                #
###########################################
import pickle
from copy import *
from random import choice
###########################################

###########################################
#                modules                  #
###########################################
from model.utils.JsonLoader import JsonLoader
from model.utils.RandomGrid import RandomGrid
from model.ObservableModel import ObservableModel
from view.ViewGame import ViewGame
###########################################

class Grid(ObservableModel):
    """Représente un modèle contenant une grille généré aléatoirement avec RandomGrid.

    Attributs:
        rows: Nombre de lignes de la grille.
        columns: Nombre de colonnes de la grille.
        cards: Nombre de cartes à placer dans la grille.
        shape: Forme de la grille.
        grid: grille généré aléatoirement.
        grid_copy: copie de la grille généré aléatoirement.
        move_history: Historique des coups joué par le joueur => (carte, (coordonnée de la première carte), (coordonnée de la deuxième carte)).
    """

    def __init__(self):
        super().__init__()

        self.__rows:int = None
        self.__columns:int = None
        self.__cards:int = None
        self.__shape:str = None
        self.__grid:[[[int]]] = None
        self.__grid_copy:[[[int]]] = None
        self.__move_history:[tuple] = []

    def get_grid(self) -> [[[int]]]:
        return self.__grid

    def get_grid_copy(self) -> [[[int]]]:
        return self.__grid_copy

    def get_rows(self) -> int:
        return self.__rows
    
    def get_columns(self) -> int:
        return self.__columns

    def get_cards(self) -> int:
        return self.__cards

    def get_shape(self) -> str:
        return self.__shape

    def get_move_history(self) -> [tuple]:
        return self.__move_history

    def replay(self) -> None:
        """Jouer une nouvelle partie.
        Notes:
            - Génère une nouvelle grille aléatoirement.
            - Remet à zéro l'historique des coups du joueur.
            - Préviens les observeurs/écouteurs.
        """
        self.__grid = RandomGrid().generate_random_grid(self.__rows, self.__columns, self.__cards, self.__shape)
        self.__grid_copy = deepcopy(self.__grid)
        self.__move_history = []
        self._notify_grid_change()

    def retry(self) -> None:
        """Rejouer la partie.
        Notes:
            - Génère la même grille en utilisant la copie de celle-ci.
            - Remet à zéro l'historique des coups du joueur.
            - Préviens les observeurs/écouteurs.
        """
        self.__grid = deepcopy(self.__grid_copy)
        self.__move_history = []
        self._notify_grid_change()

    def remove(self, click1, click2) -> None:
        """Supprimer un couple de cartes de la grille.
        Notes:
            - Ajout du couple dans l'historique des coups du joueur.
            - Suppression des deux cartes dans la grille.
            - Préviens les observeurs/écouteurs.
        """
        self.__move_history.append((self.__grid[click1[0]][click1[1]][0], (click1), (click2)))
        self.__grid[click1[0]][click1[1]].pop(0)
        self.__grid[click2[0]][click2[1]].pop(0)
        self._notify_grid_change()

    def add(self) -> None:
        """Ajout d'un couple de cartes dans la grille.
        Notes:
            - Ajout dans la grille des deux dernières cartes jouées si l'historique n'est pas vide.
            - Suppression dans l'historique des deux dernières cartes jouées si l'historique n'est pas vide.
            - Préviens les observeurs/écouteurs si l'historique n'est pas vide.
        """
        if self.__move_history != []:
            move = self.__move_history.pop()
            self.__grid[move[1][0]][move[1][1]].insert(0, move[0])
            self.__grid[move[2][0]][move[2][1]].insert(0, move[0])
            self._notify_grid_change()
    
    def is_empty(self) -> bool:
        """Vérifie si la grille est vide.
        Returns:
            - True si la grille est vide.
            - False si la grille est remplie.
        """
        for row in range(self.__rows):
            for column in range(self.__columns):
                if len(self.__grid[row][column]) != 0:
                    return False
        return True

    def cards_position(self) -> list:
        """Obtenir une liste de toutes les cartes du jeu avec leur position.
        Returns:
            Une liste contenant des tuples qui contiennent le numéro de la carte, sa ligne et sa colonne.
        """
        return [(self.__grid[row][column][0], row, column) 
                for row in range(self.__rows) 
                for column in range(self.__columns)
                if len(self.__grid[row][column]) != 0]

    def playable_card_couple(self) -> [[tuple, tuple]]:
        """Obtenir une liste de tous les couples de cartes identiques pouvant être jouées.
        Returns:
            Une liste de listes, chaque sous-liste contenant deux tuples représentant un couple de cartes identiques.
        """
        positions = self.cards_position()
        position_couples = []
        uplets = []
        for i in range(len(positions)):
            uplets.append(positions[i])
            for i in range(len(positions)):
                if uplets[0][0] == positions[i][0]:
                    if uplets[0] != positions[i]:
                        if [(positions[i][1], positions[i][2]), (uplets[0][1], uplets[0][2])] not in position_couples:
                            position_couples.append([(uplets[0][1], uplets[0][2]), (positions[i][1], positions[i][2])])
            uplets = []
        return position_couples

    def is_blocked(self) -> bool:
        """Vérifie si la grille est bloquée.
        Notes:
            - La grille est bloquée quand il n'y a plus de couples de cartes jouables.
        Returns:
            - True si la grille est bloquée.
            - False si la grille n'est pas bloquées.
        """
        couple_cards = self.playable_card_couple()
        for i in range(len(couple_cards)):
            if len(couple_cards[i]) > 1:
                return False
        return True

    def one_move(self) -> [tuple, tuple]:
        """Obtenir un couple de cartes identiques jouables.
        Returns:
            Une liste contenant deux tuples. Les tuples contiennent les coordonnées et le numéro des cartes identiques.
        """
        return choice(self.playable_card_couple())

    def end(self) -> str:
        """Obtenir la phrase de fin du jeu si c'est la fin du jeu.
        Returns:
            La phrase de fin du jeu si c'est la fin du jeu sinon une chaine vide.
        """
        if self.is_empty():
            return "Well done you won !"
        elif self.is_blocked():
            return "Situation blocked, it's lost !"
        return ""

    def save_grid(self) -> None:
        """Sauvegarder la grille de jeu dans un fichier.
        Notes:
            - Utilisation de pickle.dump() pour sérialiser la sauvegarde.
        Raises:
            Exception : s'il se produit un quelconque problème lors de la sauvegarde de la grille.
        """
        try:
            backup = {"grid": self.__grid,
                        "copy_grid": self.__grid_copy,
                        "rows": self.__rows, 
                        "columns": self.__columns,
                        "cards": self.__cards,
                        "move_history": self.__move_history}
            file = open("../data/save/save", "wb")
            pickle.dump(backup, file)
            file.close()
        except Exception as e:
            raise Exception(f"An unexpected error has occurred: {e}")

    def load_grid(self, state:bool) -> None:
        """Charger la grille de jeu.
        Args:
            state : Si Vrai alors utiliser la sauvegarde si Faux alors créer une grille aléatoirement.
        Notes:
            - Lors de la création de la grille aléatoire (state = Faux), les paramètres de la grille sont ceux du fichier settings.json
            - Dans tous les cas la méthode préviens les observeurs/écouteurs.
        """
        if state:
            try:
                file = open("../data/save/save", "rb")
                save = pickle.load(file)
                file.close()
                self.__grid = save["grid"]
                self.__grid_copy = save["copy_grid"]
                self.__rows = save["rows"]
                self.__columns = save["columns"]
                self.__cards = save["cards"]
                self.__move_history = save["move_history"]
            except:
                raise Exception("Something went wrong when opening the file")
        else:
            settings = JsonLoader("./config/settings.json")
            self.__rows = settings.get_setting("grid_settings", "rows")
            self.__columns = settings.get_setting("grid_settings", "columns")
            self.__cards = settings.get_setting("grid_settings", "cards")
            self.__shape = settings.get_setting("grid_settings", "shape")
            self.__grid = RandomGrid().generate_random_grid(self.__rows, self.__columns, self.__cards, self.__shape)
            self.__grid_copy = deepcopy(self.__grid)
        self._notify_grid_change()
