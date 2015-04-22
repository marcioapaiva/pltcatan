from types import MethodType
from engine.src.exceptions import *

from engine.src.lib.utils import Utils
from engine.src.resource_type import ResourceType


def get_import_value(dot_notation_str, var_name, prefix='engine.src.config.'):
    mod = __import__(prefix + dot_notation_str, globals(), locals(), [var_name], -1)
    value = getattr(mod, var_name)
    return value

config = {
    # Game
    'game' : {
        'points_to_win': 10,
        'default_player_count': 3
    },
    'board' : {
        'default_tile_count': 19,
        'default_radius': 3,
    },
    # Cards
    'card' : {
        # Development Cards
        'development': {
            'default': {
                'count': 0,
                'name': 'Development Card',
                'description': 'Development card default description.',
                'draw_card': Utils.noop,
                'play_card': Utils.noop,
                'cost': {
                    ResourceType.GRAIN: 1,
                    ResourceType.ORE: 1,
                    ResourceType.WOOL: 1
                },
            },
            # Non-Progress Cards
            'knight': {
                'count': 14,
                'name': 'Knight Card',
                'description': ('Move the robber to a new tile. Steal 1 '
                                'resource from the owner of a structure '
                                'adjacent to the new tile.'),
                'draw_card': get_import_value('card.development.knight', 'draw_card'),
                'play_card': get_import_value('card.development.knight', 'play_card'),
            },
            'victory_point': {
                'count': 5,
                'name': 'Victory Point Card',
                'description': ('Gives you one victory point. Must remain '
                                'hidden until used to win the game.'),
                'draw_card':
                    get_import_value('card.development.victory_point', 'draw_card'),
                'play_card':
                    get_import_value('card.development.victory_point', 'play_card'),
            },
            # Progress Cards
            'monopoly': {
                'count': 2,
                'name': 'Monopoly Card',
                'description': ('If you play this card, you must name 1 type '
                                'of resource. All the other players must give '
                                'you all of the Resource Cards of this type '
                                'that they have in their hands. If an opponent '
                                'does not have a Resource Card of the '
                                'specified type, he does not have to give you '
                                'anything.'),
                'draw_card': get_import_value('card.development.monopoly', 'draw_card'),
                'play_card': get_import_value('card.development.monopoly', 'play_card'),
            },
            'road_building': {
                'count': 2,
                'name': 'Road Building Card',
                'description': ('If you play this card, you may immediately '
                                'place 2 free roads on the board (according to '
                                'normal building rules)'),
                'draw_card':
                    get_import_value('card.development.road_building', 'draw_card'),
                'play_card':
                    get_import_value('card.development.road_building', 'play_card'),
            },
            'year_of_plenty': {
                'count': 2,
                'name': 'Year of Plenty Card',
                'description': ('If you play this card you may immediately '
                                'take any 2 Resource Cards from the supply '
                                'stacks. You may use these cards to build in '
                                'the same turn.'),
                'draw_card':
                    get_import_value('card.development.year_of_plenty', 'draw_card'),
                'play_card':
                    get_import_value('card.development.year_of_plenty', 'play_card'),
            }
        }
    },
    # Structures
    'structure': {
        'player_built': {
            'default': {
                'name': None,
                'cost': {
                    ResourceType.LUMBER: 0,
                    ResourceType.BRICK: 0,
                    ResourceType.WOOL: 0,
                    ResourceType.GRAIN: 0,
                    ResourceType.ORE: 0
                },
                'count': 0,
                'point_value': 0,
                'base_yield': 1,
                # TODO: Rename vars to reflect that they should be structure names?
                'extends': None,
                'upgrades': None
            },
            # Edge Structures
            'road': {
                'name': 'Road',
                'cost': {
                    ResourceType.LUMBER: 1,
                    ResourceType.BRICK: 1,
                },
                'count': 15,
                'point_value': 0,
                'base_yield': 0,
                'extends': None,
                'upgrades': None
            },
            # Vertex Structures
            'settlement': {
                'name': 'Settlement',
                'cost': {
                    ResourceType.LUMBER: 1,
                    ResourceType.BRICK: 1,
                    ResourceType.WOOL: 1,
                    ResourceType.GRAIN: 1
                },
                'count': 5,
                'point_value': 1,
                'base_yield': 1,
                'extends': None,
                'upgrades': None
            },
            'city': {
                'name': 'City',
                'cost': {
                    ResourceType.GRAIN: 2,
                    ResourceType.ORE: 3,
                },
                'count': 5,
                'point_value': 1,
                'base_yield': 2,
                'extends': None,
                'upgrades': 'Settlement'
            }
        }
    }
}


class Config(object):

    @classmethod
    def init_from_config(cls, obj, config_path):
        property_dict = Config.get(config_path)

        Utils.init_from_dict(obj, property_dict)

    @classmethod
    def pluck(cls, config_path, prop):


        target_dict = Config.get(config_path)
        return Utils.pluck(target_dict, prop, True)

    @classmethod
    def get(cls, dot_notation_str):
        """Get a value from the main config dict given a dot notation string.

        E.g. if caller wants config['game']['points_to_win'], they can pass in
        as their dot_notation_str 'game.points_to_win'.
        """

        keys = dot_notation_str.split('.')

        def get_recursive(dct, keys):
            key = keys.pop(0)
            val = None

            # Get the value of the key if it's in the dict.
            if key in dct:
                val = dct.get(key)
            else:
                raise NoConfigValueDefinedException(dot_notation_str)

            # If we still have keys left, the property we want is nested
            # somewhere inside the value we fetched.
            if keys:
                if val:
                    return get_recursive(val, keys)
                else:
                    raise NoConfigValueDefinedException(dot_notation_str)
            # If we have no keys left, we've found the target value.
            else:
                return val

        value = get_recursive(Config.config, keys)

        # Remove default value from dictionary type return value.
        if type(value) is dict:
            value = {k: value[k] for k in value.keys() if k != 'default'}

        return value

    config = config
