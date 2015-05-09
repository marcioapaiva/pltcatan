import pdb
from engine.src.config.config import Config
from engine.src.lib.utils import Utils
from engine.src.exceptions import *
from engine.src.player import Player
from engine.src.dice import Dice
from engine.src.input_manager import InputManager
from engine.src.board.game_board import GameBoard
from engine.src.resource_type import ResourceType
from engine.src.position_type import PositionType
from engine.src.structure.structure import Structure
from engine.src.calamity.robber import Robber
from engine.src.longest_road_search import LongestRoadSearch

from imperative_parser.oracle import ORACLE

class Game(object):
    """A game of Settlers of Catan."""

    def __init__(self):

        Config.init()

        self.dice = Dice()
        self.board = GameBoard(Config.get('board.default_radius'))
        ORACLE.set('board', self.board)

        # Place the robber on a fallow tile.
        self.robber = Robber()
        tile = self.board.get_tile_of_resource_type(ResourceType.FALLOW)
        tile.add_calamity(self.robber)

        self.players = []
        self.input_manager = InputManager

    def start(self):
        self.create_players()
        self.initial_settlement_and_road_placement()
        self.game_loop()

    def game_loop(self):

        max_point_count = 0

        while max_point_count < Config.get('game.points_to_win'):
            for player in self.players:
                ORACLE.set('player', player)
                InputManager(self, player).cmdloop()

            self.update_point_counts()
            max_point_count = self.get_winning_player().points

        # Print out game over message.
        winner = self.get_winning_player()
        print 'Game over. {0} wins with {1} points!\n'\
            .format(winner.name, winner.victory_point_count)

    def create_players(self):
        """Create a new batch of players."""

        self.players = []
        player_names = InputManager.get_player_names()

        for player_name in player_names:
            self.players.append(Player(player_name))

        ORACLE.set('players', self.players)

    def place_structure(self, player, structure_name, must_border_claimed_edge=True,
                        struct_x=None, struct_y=None, struct_vertex_dir=None):
        """Place an edge or vertex structure.

        Prompts for placement information and attempts to place on board. Does
        not do any exception handling.
        """
        structure = player.get_structure(structure_name)

        if structure.position_type == PositionType.EDGE:
            prompt_func = InputManager.prompt_edge_placement
            placement_func = self.board.place_edge_structure
        elif structure.position_type == PositionType.VERTEX:
            prompt_func = InputManager.prompt_vertex_placement
            placement_func = self.board.place_vertex_structure

        x, y, struct_dir = prompt_func(self)

        params = [x, y, struct_dir, structure, must_border_claimed_edge]

        if struct_vertex_dir is not None:
            params.extend([struct_x, struct_y, struct_vertex_dir])

        placement_func(*params)

        return x, y, struct_dir

    def place_init_structure(self, player, structure_name,
                             must_border_claimed_edge=False,
                             struct_x=None, struct_y=None,
                             struct_vertex_dir=None):

        valid = False

        while not valid:
            try:

                x, y, struct_dir = self.place_structure(player, structure_name, must_border_claimed_edge,
                                     struct_x, struct_y, struct_vertex_dir)

                valid = True
            except (BoardPositionOccupiedException,
                    InvalidBaseStructureException,
                    InvalidStructurePlacementException), e:
                player.restore_structure(structure_name)
                InputManager.input_default(e, None, False)

        return x, y, struct_dir

    def initial_settlement_and_road_placement(self):

        InputManager.announce_initial_structure_placement_stage()

        for player in self.players:

            InputManager.announce_player_turn(player)

            # Place settlement
            InputManager.announce_structure_placement(player, 'Settlement')
            x, y, vertex_dir = self.place_init_structure(player, 'Settlement')

            # Place road
            InputManager.announce_structure_placement(player, 'Road')
            self.place_init_structure(player, 'Road', False, x, y, vertex_dir)

        distributions = Utils.nested_dict()

        for player in list(reversed(self.players)):

            InputManager.announce_player_turn(player)

            # Place settlement
            InputManager.announce_structure_placement(player, 'Settlement')
            x, y, vertex_dir = self.place_init_structure(player, 'Settlement')

            # Place road
            InputManager.announce_structure_placement(player, 'Road')
            self.place_init_structure(player, 'Road', False, x, y, vertex_dir)

            # Give initial resource cards
            resource_types = filter(
                lambda resource_type: resource_type != ResourceType.FALLOW,
                map(lambda tile: tile.resource_type,
                    self.board.get_adjacent_tiles_to_vertex(x, y, vertex_dir))
            )

            for resource_type in resource_types:

                if not distributions[player][resource_type]:
                    distributions[player][resource_type] = 0

                distributions[player][resource_type] += \
                    Config.get('structure.player_built.settlement.base_yield')

        self.board.distribute_resources(distributions)
        InputManager.announce_resource_distributions(distributions)

    def roll_dice(self, value=None):

        roll_value = self.dice.roll()
        InputManager.announce_roll_value(roll_value)
        ORACLE.set('dice_value', roll_value)

        # If a calamity value, handle calamity
        distributions = self.board.distribute_resources_for_roll(roll_value)

        InputManager.announce_resource_distributions(distributions)

    def get_winning_player(self):
        """Get the player who is winning this game of Settlers of Catan."""

        return max(self.players, key=lambda player: player.points)

    # TODO
    def update_point_counts(self):

        # Determine largest army
        player_with_largest_army = max(self.players, key=lambda player: player.knights)
        player_with_longest_road = LongestRoadSearch(self.board).execute()

        print('update_point_counts not implemented.')

