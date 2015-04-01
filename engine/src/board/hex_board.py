# -*- coding: utf-8 -*-

from ..tile.hex_tile import HexTile
from ..direction.edge_direction import EdgeDirection
from .board import Board


class HexBoard(Board):
    """A horizontal hextile board, such as that used in Settlers of Catan.

    Hextiles are referred to using axial coordinates.
        See below for more on axial hex coordinates.
            http://devmag.org.za/2013/08/31/geometry-with-hex-coordinates/
            www.redblobgames.com/grids/hexagons

    Attributes:
        radius (int): The number of tiles between the center tile and the edge
          of the board, including the center tile itself. Should be >= 1.

        tiles (dict): A dictionary of tiles, indexed using axial coordinates
        
    Args:
        radius (int): The number of tiles between the center tile and the edge
          of the board, including the center tile itself. Should be >= 1.
    """

    MIN_BOARD_RADIUS = 1

    def __init__(self, radius, tile_cls=HexTile):

        if radius < HexBoard.MIN_BOARD_RADIUS:
            message = ("Specified radius does not meet the minimum "
                       "board tile radius {0}").format(HexBoard.MIN_BOARD_RADIUS)
            raise ValueError(message)

        self.radius = radius

        self.tile_cls = tile_cls

        self.tiles = {}
        self._create_tiles()

    def _create_tiles(self):
        """Generates a dictionary of tiles, indexed by axial coordinates.

        See how coordinates are generated in _add_new_tile_with_coords()
        """

        for x, y in self.iter_tile_coords():
            self._add_new_tile_with_coords(x, y)


    def _add_new_tile_with_coords(self, x, y):
        """Add a brand new tile to the board at the given axial coordinates."""

        if x not in self.tiles:
            self.tiles[x] = {}

        tile = self.tile_cls(x, y)

        # A new tile will have its own brand new vertices and edges,
        # but we don't want new edges if that edge has already been defined
        # by a neighbor. Here we sync such shared vertices and edges.
        tile = self._sync_tile_vertices_and_edges(tile)

        self.tiles[x][y] = tile

    def _sync_tile_vertices_and_edges(self, tile):
        """Synchronize shared vertices and edges across tiles.

        New tile objects will create their own vertices and edges. When tiles
        share edges and vertices with existing tiles on the board, however,
        we want them to point to the same shared vertex or edge objects,
        instead of each having their own. This method enforces this for the
        given tile.

        Args:
            tile (Tile): The tile whose vertices and edges we want to make
              sure point to the same vertex and edge objects as that of its
              existing neighbors with whom it shares a common vertex or edge.

        Returns:
            tile: Same as given tile object, with updated vertex and edge
              objects.
        """

        neighboring_tiles = self.get_neighboring_tiles(tile)

        # print "Given tile: {0}\nNeighboring tiles: {1}\n\n".format(
            # tile, neighboring_tiles)

        for (direction, neighbor_tile) in neighboring_tiles.iteritems():
            tile.update_common_edge_and_vertices(direction, neighbor_tile)

        return tile

    def get_tile_with_coords(self, x, y):
        """Get the tile at the given coordinates, or None if no tile exists."""

        if x in self.tiles and y in self.tiles[x]:
            return self.tiles[x][y]

        return None

    def get_neighboring_tile(self, tile, edge_direction):
        """Get the tile neighboring the given tile in the given direction.

        Args:
            tile (Tile): The tile for which we'd like to find the neighbor.

            direction (EdgeDirection): hextiles have 6 edges and thus
              neighbors in 6 different directions.

        Returns:
            Tile. None if the tile has no valid neighbor in that direction.

        TODO: enforce that direction is actually in EdgeDirection
        """

        x = tile.x + edge_direction[0]
        y = tile.y + edge_direction[1]

        return self.get_tile_with_coords(x, y)

    def get_neighboring_tiles(self, tile):
        """Get all six neighboring tiles for the given hextile.

        Args:
            tile (Tile): The tile whose neighbors we want to return.

        Returns:
            dict. Keys are directions and values are tiles that neighbor the
              given tile in that direction.
        """

        neighboring_tiles = {}

        for direction in EdgeDirection:
            neighbor_tile = self.get_neighboring_tile(tile, direction)

            if neighbor_tile:
                neighboring_tiles[direction] = neighbor_tile

        return neighboring_tiles

    def iter_tiles(self):
        """Iterate over the tiles in this board.

        The order is that described in iter_tile_coords.
        """

        for x, y in self.iter_tile_coords():
            yield self.get_tile_with_coords(x, y)

    def iter_tile_coords(self):
        """Iterate over axial coordinates for each tile in the board.

        This is a generator function that will yield the coordinates to the
        caller each time after they are computed.

        We can consider a hextile board a series of concentric rings where the
        radius counts the number of concentric rings that compose the board.
        When generating coordinates, we traverse each such ring one at a time,
        starting from the innermost ring (i.e. the single center tile)
        that has ring_index 0 to the outermost ring (i.e. the ring consisting
        of tiles on the edge of the board) that has ring_index radius - 1.

        When traversing a ring, we start from the westernmost tile of that ring
        and continue around the ring in a clockwise fashion. We stop at the tile
        directly before the easternmost ring. We can do this because, every time
        we find a tile's coordinates in the ring, we can also find the
        coordinates of the tile mirror opposite it in the ring by simply
        flipping the axial coordinates.
        """

        # Yield coordinates for the center tile.
        yield 0, 0

        for ring_index in range(self.radius):
            # We start yielding coordinates from the westernmost tile.
            x = -1 * ring_index
            y = 0

            # First we scale the northwest side of the ring.
            # This is equivalent to moving along the y-axis of the board.
            while y != ring_index:
                yield x, y
                yield y, x
                y += 1

            # Then we scale the northern side of the ring.
            # This is equivalent to moving along the x-axis of the board.
            while x != 0:
                yield x, y
                yield y, x
                x += 1

            # Finally we scale the northeast side of the ring.
            # This is equivalent to moving along the z-axis of the board.
            while x != ring_index or y != 0:
                yield x, y
                yield y, x
                x += 1
                y -= 1



