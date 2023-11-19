import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class SoilLayer:
    def __init__ (self, all_sprites):

        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surfs = import_folder_dict('../graphics/soil/')
        self.water_surfs = import_folder('../graphics/soil_water/')

        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):

                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')

                pos = soil_sprite.rect.topleft
                surf = choice(self.water_surfs)
                # create water sprite
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

    def remove_water(self):

        # destroy water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        # clean up the grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:

                    # tile options
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]

                    tile_type = 'o'

                    # all sides
                    if all((t,b,r,l)): tile_type = 'x'

                    # horizontal tiles
                    if l and not any((t,b,r)): tile_type = 'r'
                    if r and not any((t,b,l)): tile_type = 'l'
                    if r and l and not any((t,b)): tile_type = 'lr'

                    # vertical tiles
                    if t and not any((b,r,l)): tile_type = 'b'
                    if b and not any((t,r,l)): tile_type = 't'
                    if t and b and not any((r,l)): tile_type = 'tb'

                    # corner tiles
                    if t and l and not any((b,r)): tile_type = 'br'
                    if t and r and not any((b,l)): tile_type = 'bl'
                    if b and l and not any((t,r)): tile_type = 'tr'
                    if b and r and not any((t,l)): tile_type = 'tl'

                    # t shaped tiles
                    if all((t,b,r)) and not l: tile_type = 'tbr'
                    if all((t,b,l)) and not r: tile_type = 'tbl'
                    if all((t,r,l)) and not b: tile_type = 'lrb'
                    if all((b,r,l)) and not t: tile_type = 'lrt'

                    SoilTile(
                        pos = (index_col * TILE_SIZE, index_row * TILE_SIZE),
                        surf = self.soil_surfs[tile_type],
                        groups = [self.all_sprites, self.soil_sprites])


