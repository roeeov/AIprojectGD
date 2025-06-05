from scripts.constants import *
from collections import deque
from scripts.tilemap import tile_map
import numpy as np
import pygame
import math

class Player:

    def __init__(self, game):
        self.game = game
        self.trail = deque()
        self.action = ''
        self._initialize()  # Call the method that initializes everything

    def _initialize(self):
        """Set the initial state of the player."""
        checkpointInfo = self.game.getCheckpoint()
        self.pos = checkpointInfo['pos'].copy()
        self.game.scroll = checkpointInfo['scroll'].copy()
        self.Yvelocity = checkpointInfo['velocity']
        self.collisions = {'up': False, 'down': False, 'right': False}
        self.hitbox_collisions = {'up': False, 'down': False, 'right': False}
        self.input = {'hold': False, 'click': False, 'buffer': False}
        self.orb_clicked = False
        self.grounded = False
        self.death = False # is the player dead
        self.finishLevel = False # did the player reach the finish
        self.respawn = False # is death animation over and need to respawn
        self.gravityDirection = checkpointInfo['gravity']
        self.portal_grace_period = 2
        self.gamemode = ''
        self.setGameMode(checkpointInfo['gamemode'])

        self.air_time = 5
        self.total_rotation = 0  # Track total rotation during a jump

    def reset(self):
        """Reset the player to its initial state."""
        self.trail.clear()
        self._initialize()


    def update(self, upPressed):

        self.checkDeath()

        if self.death:
            self.set_action('death')
            self.animation.update()
            if self.animation.done: self.respawn = True 
            return

        self.input['click'] = upPressed and not self.input['hold']
        self.input['hold'] = upPressed
        if self.input['click']:  self.input['buffer'] = True
        if not self.input['hold']: self.input['buffer'] = False
        self.orb_clicked = False

        self.collisions = {'up': False, 'down': False, 'right': False}
        self.hitbox_collisions = {'up': False, 'down': False, 'right': False}

        if self.death: frame_movement = (0, 0)
        else: frame_movement = (PLAYER_SPEED, self.Yvelocity)
        
        # Check for collisions and update player position
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        hitbox = self.hitbox_rect()
        for rect in tile_map.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                #entity_rect.right = rect.left
                self.collisions['right'] = True
                if hitbox.colliderect(rect):
                    self.hitbox_collisions['right'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        hitbox = self.hitbox_rect()
        for rect in tile_map.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                    if hitbox.colliderect(rect):
                        self.hitbox_collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                    if hitbox.colliderect(rect):
                        self.hitbox_collisions['up'] = True
                if not self.collisions['right'] and not self.gamemode == 'wave':
                    self.pos[1] = entity_rect.y

           # Only check for interactive objects if not in grace period
        if self.portal_grace_period > 0:
            self.portal_grace_period -= 1
        else:
            # Check for portals and other interactive objects
            entity_rect = self.rect()
            hitbox = self.hitbox_rect()
            for rect, (type, variant) in tile_map.interactive_rects_around(self.pos):
                if hitbox.colliderect(rect):
                    match type:
                        case 'portal':
                            game_mode = GAMEMODES[variant]
                            self.setGameMode(game_mode)
                        case 'spike':
                            if not self.game.noclip: self.death = True
                        case 'finish':
                            self.finishLevel = True
                if entity_rect.colliderect(rect):
                    match type:
                        case 'orb':
                            if (self.input['buffer'] or self.input['click']) and not self.orb_clicked:
                                if ORBS[variant] in {'blue', 'green'}: 
                                    self.gravityDirection = {'down': 'up', 'up': 'down'}[self.gravityDirection]
                                if self.gamemode != 'wave':
                                    self.Yvelocity = {'down': -1, 'up': 1}[self.gravityDirection] * ORB_JUMP[ORBS[variant]][self.gamemode]

                                self.input['buffer'] = False
                                self.orb_clicked = True
                                self.air_time = 5
                                self.grounded = False
            

        self.updateVelocity()

        self.air_time += 1
        # Check if we just landed
        just_landed = False
        if (self.collisions['down'] and self.gravityDirection == 'down' or self.collisions['up'] and self.gravityDirection == 'up') and not self.orb_clicked:
            if self.air_time > 4:  # We were in the air but now we're not
                just_landed = True
            self.air_time = 0
        # Check if the player is on the ground
        self.grounded = self.air_time <= 4
   
        if not self.finishLevel and not self.death:
            self.updateVisuals(just_landed)

    def render(self, surf, offset=(0, 0)):

        # Draw the wave trail
        original_img = self.game.assets['trail']
        rotated_img = pygame.transform.rotate(original_img, 45)
        
        length = len(self.trail) - 2
        for idx, pos in enumerate(np.array(self.trail)):
            if idx < length:
                rotated_rect = rotated_img.get_rect(center=(pos[0] - offset[0], pos[1] - offset[1]))
                surf.blit(rotated_img, rotated_rect)

        # Get the original image
        original_img = self.animation.img()
        # Rotate the image around its center
        rotated_img = pygame.transform.rotate(original_img, -round(self.deg))
        # Flip the image verticly if needed
        flipped_img = pygame.transform.flip(rotated_img, False, self.gravityDirection == 'up')
        # Get the rectangle of the rotated image
        img_rect = rotated_img.get_rect(center=(self.pos[0] + self.size[0] // 2 - offset[0],
                                                self.pos[1] + self.size[1] // 2 - offset[1]))
        # Draw the rotated image
        surf.blit(flipped_img, img_rect)


        checkpoint_img = self.game.assets['checkpoint']   
        for checkpoint in np.array(self.game.checkPoints):
            checkpoint_rect = checkpoint_img.get_rect(center=(checkpoint['pos'][0] - offset[0], checkpoint['pos'][1] - offset[1]))
            surf.blit(checkpoint_img, checkpoint_rect)

        if DRAW_PLAYER_HITBOX:
            colrect = self.rect()
            colrect.center=(self.pos[0] + self.size[0] // 2 - offset[0],
                                                    self.pos[1] + self.size[1] // 2 - offset[1])
            pygame.draw.rect(surf, (0, 0, 255), colrect)
        
            colrect = self.hitbox_rect()
            colrect.center=(self.pos[0] + self.size[0] // 2 - offset[0],
                                                    self.pos[1] + self.size[1] // 2 - offset[1])
            pygame.draw.rect(surf, (0, 255, 0), colrect)


    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def hitbox_rect(self):
        return pygame.Rect(self.pos[0] + self.size[0]*(1-PLAYER_HITBOX)//2,
                           self.pos[1] + self.size[1]*(1-PLAYER_HITBOX)//2,
                           self.size[0]*PLAYER_HITBOX, self.size[1]*PLAYER_HITBOX)

    def setGameMode(self, gamemode):
        if self.gamemode == gamemode:
            return
        self.gamemode = gamemode
        self.size = PLAYERS_SIZE[self.gamemode]
        self.collisions = {'up': False, 'down': False, 'right': False}
        self.hitbox_collisions = {'up': False, 'down': False, 'right': False}
        self.deg = 0
        self.action = ''
        self.set_action('run')

    def set_action(self, action):
        if action == 'jump' and self.gamemode not in GROUND_GAMEMODES: action = 'run'
        if action != self.action:
            self.action = action
            self.animation = self.game.assets['player/' + self.gamemode + '/' + self.action].copy()

    def checkDeath(self):
        if not self.game.noclip:
            if self.hitbox_collisions['right']: 
                self.death = True
            if self.gamemode == 'wave':
                if self.hitbox_collisions['up'] or self.hitbox_collisions['down']:
                    self.death = True

    def updateVelocity(self):

        match self.gamemode:

            case 'cube':

                if self.gravityDirection == 'down':
                    gravity = GRAVITY['cube']
                    jumpVel = -PLAYER_VELOCITY['cube']
                else:
                    gravity = -GRAVITY['cube']
                    jumpVel = PLAYER_VELOCITY['cube']
                if not self.orb_clicked:
                    if self.input['hold'] and self.grounded:
                        self.input['buffer'] = False
                        self.air_time = 5
                        self.Yvelocity = jumpVel
                        
                    if (self.collisions['down'] or self.collisions['up']) and not self.collisions['right']:
                        self.Yvelocity = 0
                    else:
                        self.Yvelocity = max(-MAX_VELOCITY['cube'], min(self.Yvelocity + gravity, MAX_VELOCITY['cube']))

            case 'wave':

                self.input['buffer'] = False

                self.Yvelocity = PLAYER_VELOCITY['wave']
                self.Yvelocity *= {True: -1, False: 1}[self.input['hold']]
                self.Yvelocity *= {'down': 1, 'up': -1}[self.gravityDirection]

            case 'ball':

                gravity = GRAVITY['ball'] * {'down': 1, 'up': -1}[self.gravityDirection]

                if not self.orb_clicked:
                    if (self.collisions['down'] or self.collisions['up']) and not self.collisions['right']:
                        self.Yvelocity = 0
                    else:
                        self.Yvelocity = max(-MAX_VELOCITY['ball'], min(self.Yvelocity + gravity, MAX_VELOCITY['ball']))

                    if self.input['buffer'] and self.grounded:
                        self.input['buffer'] = False
                        self.air_time = 5
                        self.gravityDirection = {'down': 'up', 'up': 'down'}[self.gravityDirection]
                        self.Yvelocity = PLAYER_VELOCITY['ball'] * {'down': 1, 'up': -1}[self.gravityDirection]

            case 'ship':
                
                if not self.orb_clicked:
                    if (self.collisions['down'] or self.collisions['up']) and not self.collisions['right']:
                        self.Yvelocity = 0
                    else:   
                        self.Yvelocity = math.sin(self.deg * math.pi / 180 * {'down': 1, 'up': -1}[self.gravityDirection]) * PLAYER_VELOCITY['ship']
                

    # change player rotation (deg) and set the player action (run, jump)
    def updateVisuals(self, just_landed):

        match self.gamemode:

            case 'cube':
                if not self.grounded:
                    self.set_action('jump')

                    # Calculate rotation to complete 360 degrees during jump
                    if self.Yvelocity < 0:  # First half of jump (going up)
                        target_rotation = 180
                    else:  # Second half of jump (falling down)
                        target_rotation = 360
                                
                    # Smoothly rotate toward target but faster
                    degrees_left = target_rotation - self.total_rotation
                    rotation_step = min(5, degrees_left / 5 + 2)   # Modified for faster rotation
                    self.total_rotation += rotation_step
                    self.deg += rotation_step

                else: 
                    self.set_action('run')
                    # Reset rotation tracking when grounded
                    if just_landed:
                        self.deg = round(self.deg % 360 / 90) * 90  # Snap to nearest full rotation
                        self.total_rotation = 0

            case 'wave':
                if self.input['hold']:
                    self.deg += (-45-self.deg) * 0.4
                else:
                    self.deg += (45-self.deg) * 0.4

                self.trail.append((self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))
                if len(self.trail) > 73: self.trail.popleft()

            case 'ball':
                self.deg += 5
                if self.grounded:
                    self.set_action('run')
                else:
                    self.set_action('jump')

            case 'ship':
                # if self.input['hold']:
                #     self.deg += (-45-self.deg) * 0.04
                # else:
                #     self.deg += (45-self.deg) * 0.04
                # if self.Yvelocity == 0: self.deg *= 0.1  # Slow down rotation when not moving
                if self.Yvelocity == 0:
                    self.deg *= 0.1  # Slow down rotation when not moving
                    self.deg = round(self.deg)

                deltaDeg = abs(self.deg) * 0.01 + 1.5 # Adjust rotation speed
                if self.input['hold']:
                    self.deg -= deltaDeg
                else:
                    self.deg += deltaDeg
                self.deg = min(max(self.deg, -40), 40)
            
        self.animation.update()