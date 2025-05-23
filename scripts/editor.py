import sys

import pygame

from scripts.utils import *
from scripts.tilemap import tile_map
from scripts.constants import *
from scripts.mapManager import map_manager
from scripts.gameStateManager import game_state_manager

class Editor:
    def __init__(self, display):

        self.display = display
        #self.display.set_caption('editor')
        self.bgIMG = load_image('background.png', scale=DISPLAY_SIZE) 

        self.resetEditor()

        self.buttons = []
        prev_text = Text('', pos = (50, 50), size=UIsize(3))
        prev_button = Button(prev_text, (0 ,255, 0), button_type='prev', image=load_image('UI/buttons/back.png', (UIsize(3), UIsize(3))) )
        self.buttons.append(prev_button)

        instruction_text = 'SAVE - O\nDELETE - RIGHT CLICK\nPLACE - LEFT CLICK\nMOVE - W,A,S,D\nSWITCH TILE - SCROLL WHEEL (HOLD SHIFT TO SWITCH TILE VARIANT)\nZOOM IN - UP\nZOOM OUT - DOWN\nGRID - G\nAUTOTILE - T'
        self.instructions = Text(instruction_text, pos = vh(1, 80), size=UIsize(1), centered=False, color=(255, 255, 255))

    def resetEditor(self):
        self.scroll = [0, 0]
        self.setZoom(10)
        self.movement = [False, False, False, False]
        
        self.popup = None
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

        self.tileMenuPos = DISPLAY_SIZE[1]
        self.tileMenuOpen = False

    def reload_assets(self):
        IMGscale = (tile_map.tile_size, tile_map.tile_size)
        tile_assets = {
            'decor': load_images('tiles/decor', scale=IMGscale),
            'grass': load_images('tiles/grass', scale=IMGscale),
            'stone': load_images('tiles/stone', scale=IMGscale),
            'portal': load_images('tiles/portal', scale=(IMGscale[0], IMGscale[1]*2)),
            'spike': load_images('tiles/spike', scale=IMGscale),
            'finish':load_images('tiles/finish', scale=(IMGscale[0], IMGscale[1]*2)),
            'orb': load_images('tiles/orb', scale=IMGscale),
        }

        spawner_assets = tile_assets.copy()
        spawner_assets['spawner'] = load_image('extra/spawner.png', scale=IMGscale)
        tile_map.setAssets(spawner_assets)
        
        return tile_assets
    
    def setZoom(self, zoom):
        self.zoom = int(zoom)
        new_tile_size = int(TILE_SIZE * self.zoom // 10)
        self.scroll[0] = (self.scroll[0] + DISPLAY_SIZE[0]//2) // tile_map.tile_size * new_tile_size - DISPLAY_SIZE[0]//2
        self.scroll[1] = (self.scroll[1] + DISPLAY_SIZE[1]//2) // tile_map.tile_size * new_tile_size - DISPLAY_SIZE[1]//2
        tile_map.tile_size = new_tile_size
        self.assets = self.reload_assets()
    
    def deleteGridBlock(self, tile_pos):
        tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
        if tile_loc in tile_map.tilemap:
            tile = tile_map.tilemap[tile_loc]
            if tile['type'].split()[0] in {'portal', 'finish'}:
                if tile['type'].split()[1] == 'up':
                    if str(tile_pos[0]) + ';' + str(tile_pos[1]+1) in tile_map.tilemap:
                        del tile_map.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1]+1)]
                else:
                    if str(tile_pos[0]) + ';' + str(tile_pos[1]-1) in tile_map.tilemap:
                        del tile_map.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1]-1)]
            del tile_map.tilemap[tile_loc]

    def placeGridBlock(self, tile_pos, tile_type):
        self.deleteGridBlock(tile_pos)
        tile_map.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': tile_type, 'variant': self.tile_variant, 'pos': tile_pos}

    def canPlaceTile(self, mpos):
        return mpos[1] < self.tileMenuPos

    def drawTileMenu(self, mouse_pressed, mouse_released):
        tile_menu = pygame.Surface((DISPLAY_SIZE[0], EDITOR_TILE_MENU_SIZE), pygame.SRCALPHA)
        tile_menu.fill((0, 0, 20, 256*0.5))

        variant_buttons = []
        for idx, variant_img in enumerate(self.assets[self.tile_list[self.tile_group]]):
            variant_img = variant_img.copy()
            variant_img = pygame.transform.scale(variant_img, (TILE_SIZE, variant_img.get_height() * TILE_SIZE // variant_img.get_width()))
            variant_pos = (DISPLAY_SIZE[0]//(TILE_MENU_COLUMNS+1) * (idx % TILE_MENU_COLUMNS + 1), EDITOR_TILE_MENU_SIZE // (TILE_MENU_ROWS+1) * (idx // TILE_MENU_COLUMNS + 1))
            variant_txt = Text('', variant_pos, size=UIsize(1))
            variant_buttons.append(Button(variant_txt, (0, 0, 0), button_type=str(idx), image=variant_img, mouse_offset=(0, EDITOR_TILE_MENU_SIZE - DISPLAY_SIZE[1])))

        variants_radio = radionButton(variant_buttons, opacity_facor=256*0.7)
        variant_clicked = variants_radio.update(mouse_pressed, mouse_released)
        if variant_clicked is not None: self.tile_variant = int(variant_clicked)
        variants_radio.chosen = self.tile_variant
        variants_radio.blit(tile_menu)

        self.display.blit(tile_menu, (0, self.tileMenuPos))

    def run(self):
            self.display.blit(self.bgIMG, (0, 0))
            
            self.scroll[0] += (self.movement[1] - self.movement[0]) * (EDITOR_SCROLL_FAST if self.shift else EDITOR_SCROLL)
            self.scroll[1] += (self.movement[3] - self.movement[2]) * (EDITOR_SCROLL_FAST if self.shift else EDITOR_SCROLL)
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            if self.tileMenuOpen:
                self.tileMenuPos += ((DISPLAY_SIZE[1] - EDITOR_TILE_MENU_SIZE) - self.tileMenuPos) * 0.3
            else: self.tileMenuPos += (DISPLAY_SIZE[1] - self.tileMenuPos) * 0.3
            
            tile_map.render(self.display, offset=render_scroll)
            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            self.instructions.blit(self.display)
            
            mpos = pygame.mouse.get_pos()
            tile_pos = (int((mpos[0] + self.scroll[0]) // tile_map.tile_size), int((mpos[1] + self.scroll[1]) // tile_map.tile_size))
            
            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * tile_map.tile_size - self.scroll[0], tile_pos[1] * tile_map.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)
            
            if self.clicking and self.ongrid and self.canPlaceTile(mpos):
                tile_type = self.tile_list[self.tile_group]
                
                if tile_type in {'portal', 'finish'}:
                    self.placeGridBlock(tile_pos, tile_type + ' up')
                    self.placeGridBlock((tile_pos[0], tile_pos[1]+1), tile_type + ' down')
                else:
                    self.placeGridBlock(tile_pos, tile_type)

            if self.right_clicking:

                self.deleteGridBlock(tile_pos)
                    
                for tile in tile_map.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] * tile_map.tile_size - self.scroll[0], tile['pos'][1] * tile_map.tile_size - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        tile_map.offgrid_tiles.remove(tile)
            
            self.display.blit(current_tile_img, vh(95, 2))

            mouse_pressed = False
            mouse_released = False
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pressed = True
                        self.clicking = True
                        if not self.ongrid and self.canPlaceTile(mpos):
                            tile_type = self.tile_list[self.tile_group]
                            if (tile_type not in PHYSICS_TILES and tile_type not in INTERACTIVE_TILES):
                                tile_pos = ((mpos[0] + self.scroll[0]) / tile_map.tile_size, (mpos[1] + self.scroll[1]) / tile_map.tile_size)
                                tile_map.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_released = True
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        tile_map.autotile()
                    if event.key == pygame.K_o:
                        path = map_manager.getMapPath()
                        tile_map.save(path)
                        self.popup = Popup("Level Saved!")
                    if event.key == pygame.K_p:
                        self.tileMenuOpen = not self.tileMenuOpen
                    if event.key in {pygame.K_LSHIFT, pygame.K_RSHIFT}:
                        self.shift = True
                    if event.key == pygame.K_UP:
                        if self.zoom < 20:
                            self.setZoom(self.zoom + 1)
                    if event.key == pygame.K_DOWN:
                        if self.zoom > 1:
                            self.setZoom(self.zoom - 1)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key in {pygame.K_LSHIFT, pygame.K_RSHIFT}:
                        self.shift = False


            for button in self.buttons:
                button.update(mouse_pressed, mouse_released)
                if button.is_clicked():
                    if button.type == 'prev':
                        self.resetEditor()
                        game_state_manager.returnToPrevState()
                button.blit(self.display)

            self.drawTileMenu(mouse_pressed, mouse_released)

            if self.popup is not None and not self.popup.is_done():
                self.popup.update()
                self.popup.draw(self.display)



