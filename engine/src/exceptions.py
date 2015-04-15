class NotEnoughResourcesException(Exception):
    """Raise when a trader lacks enough resources cards for a transaction.

    E.g. when a player doesn't have enough resource cards to buy a structure,
    or when a bank runs out of resources.

    Attributes:
        See Exception.

    Args:
        trading_entity (TradingEntity): The entity that lacked resources.

        resource_type (ResourceType): The type of resource the entity lacked.
    """

    def __init__(self, trading_entity, resource_type):
        self.msg = '{0} does not have enough {1} cards!'.format(
            trading_entity.__class__.__name__, resource_type)


class NotEnoughStructuresException(Exception):
    """Raise when a player tries to build a structure despite having none left.

    Args:
        player (Player): The player that tried to build a structure.

        structure_cls (class): The class of structure the player attempted to
          build despite having run out.
    """

    def __init__(self, player, structure_cls):
        self.msg = '{0} does not have a {1} in stock.'.format(
            player.name, structure_cls.__name__.lower())


class NotEnoughDevelopmentCardsException(Exception):
    """Raise when a player tries to buy a development card when none left."""

    def __init__(self):
        self.msg = 'No development cards remaining.'


class InvalidBaseStructureException(Exception):
    """Raise when one tries to build an invalid upgrade or extension structure.

    Upgrade and extension structures need to be built off an appropriate base
    structure of a predetermined class. If the wrong class base structure is
    attempted, we should raise this error.
    """

    def __init__(self, base_structure, augmenting_structure):
        self.msg = '{0} must have base structure {1}, but given {2}!'.format(
            augmenting_structure.__class__.__name__,
            augmenting_structure.base_structure.__class__.__name__,
            base_structure.__class__.__name__
        )
