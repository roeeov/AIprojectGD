import json
import numpy as np
import pygame
from scripts.constants import *

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOR_OFFSETS = np.array([(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)])
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, assets=None, tile_size=16):

        self.assets = assets
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def setAssets(self, assets):
        self.assets = assets
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def save(self, path):
        f = open(path, 'r')
        info_data = json.load(f)['info']
        f.close()
        f = open(path, 'w')
        json.dump({'info': info_data, 'tilemap': self.tilemap, 'offgrid': self.offgrid_tiles}, f, indent=4)
        f.close()
        
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        
        self.tilemap = map_data['tilemap']
        self.offgrid_tiles = map_data['offgrid']
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    

    def interactive_rects_around(self, pos):
        tiles = []
        for tile in self.tiles_around(pos):
            if tile['type'].split()[0] in INTERACTIVE_TILES:
                match tile['type'].split()[0]:
                    case 'portal' | 'finish':
                        tiles.append((pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size), (tile['type'].split()[0], tile['variant'])))
                    case 'spike':
                        # Calculate the centered spike hitbox exactly like in render method
                        colrect = pygame.Rect(
                            self.tile_size * tile['pos'][0], 
                            self.tile_size * tile['pos'][1], 
                            int(self.tile_size*SPIKE_SIZE[0]), 
                            int(self.tile_size*SPIKE_SIZE[1])
                        )
                        # Center the rect within the tile
                        colrect.center = (
                            self.tile_size * tile['pos'][0] + self.tile_size//2, 
                            self.tile_size * tile['pos'][1] + self.tile_size//2
                        )
                        tiles.append((colrect, (tile['type'], tile['variant'])))
                    case 'orb':
                        tiles.append((pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size), (tile['type'], tile['variant'])))
        return tiles
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] not in {'portal down', 'finish down'}:
                        surf.blit(self.assets[tile['type'].split()[0]][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
                    if SHOW_SPIKE_HITBOX and tile['type'] == 'spike':
                        colrect = pygame.Rect(
                            self.tile_size * tile['pos'][0], 
                            self.tile_size * tile['pos'][1], 
                            int(self.tile_size*SPIKE_SIZE[0]), 
                            int(self.tile_size*SPIKE_SIZE[1])
                        )
                        colrect.center = (tile['pos'][0] * self.tile_size - offset[0] + self.tile_size//2, 
                                        tile['pos'][1] * self.tile_size - offset[1] + self.tile_size//2)
                        pygame.draw.rect(surf, (255, 0, 0), colrect)


tile_map = Tilemap(tile_size=TILE_SIZE)