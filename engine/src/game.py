from engine.src.config import Config
from engine.src.lib.utils import Utils
from engine.src.player import Player
from engine.src.dice.dice import Dice
from engine.src.input_manager import InputManager
from engine.src.board.game_board import GameBoard
from engine.src.structure.vertex_structure.settlement import Settlement
from engine.src.structure.edge_structure.road import Road


class Game(object):
    """A game of Settlers of Catan."""

    def __init__(self):

        self.dice = Dice()
        self.board = GameBoard(GameBoard.DEFAULT_RADIUS)
        self.players = []

    def start(self):
        self.create_players()
        self.initial_settlement_and_road_placement()
        self.game_loop()

    def game_loop(self):

        max_point_count = 0

        while max_point_count < Config.POINTS_TO_WIN:
            for player in self.players:
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

    def place_vertex_structure(self, player, structure_cls):

        x, y, vertex_dir = \
            InputManager.prompt_vertex_placement(self)

        # TODO: Enforce valid.
        self.board.place_vertex_structure(x, y, vertex_dir,
                                          structure_cls(player))

        return x, y, vertex_dir

    # TODO: Consider taking structure_cls and *args.
    def place_edge_structure(self, player, structure_cls):

        x, y, edge_dir = \
            InputManager.prompt_edge_placement(self)

        # TODO: Enforce valid.
        self.board.place_edge_structure(x, y, edge_dir,
                                        structure_cls(player))

        return x, y, edge_dir

    def initial_settlement_and_road_placement(self):

        InputManager.announce_initial_structure_placement_stage()

        for player in self.players:
            InputManager.announce_player_turn(player)
            InputManager.announce_structure_placement(player, Settlement)
            self.place_vertex_structure(player, Settlement)
            InputManager.announce_structure_placement(player, Road)
            self.place_edge_structure(player, Road)

        distributions = Utils.nested_dict()

        for player in list(reversed(self.players)):
            InputManager.announce_player_turn(player)
            InputManager.announce_structure_placement(player, Settlement)
            x, y, vertex_dir = self.place_vertex_structure(player, Settlement)
            InputManager.announce_structure_placement(player, Road)
            self.place_edge_structure(player, Road)

            # Give initial resource cards
            resource_types = map(
                lambda tile: tile.resource_type,
                self.board.get_adjacent_tiles_to_vertex(x, y, vertex_dir)
            )

            for resource_type in resource_types:

                if not distributions[player][resource_type]:
                    distributions[player][resource_type] = 0

                distributions[player][resource_type] += Settlement.base_yield()

        self.board.distribute_resources(distributions)
        InputManager.announce_resource_distributions(distributions)

    def roll_dice(self):

        roll_value = self.dice.roll()
        InputManager.announce_roll_value(roll_value)

        # If a calamity value, handle calamity
        # Else
        distributions = self.board.distribute_resources_for_roll(roll_value)

        InputManager.announce_resource_distributions(distributions)

    def get_winning_player(self):
        """Get the player who is winning this game of Settlers of Catan."""

        return max(self.players, key=lambda player: player.points)

    def update_point_counts(self):
        print('update_point_counts not implemented.')

