import os

import pygame
from scripts.constants import *
BASE_IMG_PATH = 'data/images/'

def load_image(path, scale = None, remove_color = (0, 0, 0)):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    if remove_color is not None: img.set_colorkey(remove_color)
    if scale is not None:
        img = pygame.transform.scale(img, scale)
    return img

def load_images(path, scale = None, remove_color = (0, 0, 0)):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name, scale, remove_color))
    return images

def load_assets():
    IMGscale = (TILE_SIZE, TILE_SIZE)
    return {
            'decor': load_images('tiles/decor', scale=IMGscale),
            'grass': load_images('tiles/grass', scale=IMGscale),
            'stone': load_images('tiles/stone', scale=IMGscale),
            'portal': load_images('tiles/portal', scale=(IMGscale[0], IMGscale[1]*2)),
            'spike': load_images('tiles/spike', scale=IMGscale),
            'finish':load_images('tiles/finish', scale=(IMGscale[0], IMGscale[1]*2)),
            'orb': load_images('tiles/orb', scale=IMGscale),
            'background': load_image('background.png', scale=DISPLAY_SIZE),
            'clouds': load_images('clouds'),
            'trail': load_image('player/trail/trail.png', scale=(PLAYERS_IMAGE_SIZE['wave'][0]*0.4, PLAYERS_IMAGE_SIZE['wave'][1]*0.4))
        }

def vh(width_precent, height_precent):
    return (width_precent * DISPLAY_SIZE[0] // 100, height_precent * DISPLAY_SIZE[1] // 100)

def UIsize(size):
    return int(DISPLAY_SIZE[0] * size // 100)
        

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    

class Text():
    def __init__(self, text, pos, color = (0,0,0), size = 50, font = FONT):
        font = pygame.font.Font(font, size)
        self.text = font.render(text, True, color)
        self.text_rect = self.text.get_rect(center=pos)

    def blit(self, display):
        display.blit(self.text, self.text_rect)



class InputBox:
    def __init__(self, pos, width, height, box_type, placeholder='', placeholderColor = (99, 99, 99), 
                 textColor = (0, 0, 0), activeColor = (44, 88, 245), inactiveColor = (0, 0, 0)):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = pos
        self.colors = {'text': textColor, 'frame': inactiveColor, 'active': activeColor, 'inactive': inactiveColor, 'placeholder': placeholderColor}
        self.text = ''
        self.placeholder = placeholder
        self.font = pygame.font.Font(FONT, 36)
        self.txt_surface = self.font.render(
                    self.text if self.text else self.placeholder, True, self.colors['text'] if self.text else self.colors['placeholder'])
        self.active = False
        self.type = box_type

    def handle_event(self, event):
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active if the box is clicked
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.colors['frame'] = self.colors['active'] if self.active else self.colors['inactive']

        output = ''
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    output = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(
                    self.text if self.text else self.placeholder, True, self.colors['text'] if self.text else self.colors['placeholder'])

        return output

    def update(self):
        # Resize the box if the text is too long
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)
        # Blit the rect
        pygame.draw.rect(screen, self.colors['frame'], self.rect, 2)

class radionButton:
    def __init__(self, buttonList):
        self.buttons = buttonList
        self.chosen = -1

    def update(self, mouse_pressed, mouse_released):
        for idx, button in enumerate(self.buttons):
            button.update(mouse_pressed, mouse_released)
            if button.is_clicked():
                self.chosen = idx

        return self.buttons[self.chosen].type if self.chosen != -1 else None
    
    def blit(self, surf):
        for idx, button in enumerate(self.buttons):
            opacity = 255 if idx == self.chosen else 255//2
            button.blit(surf, opacity=opacity)

    

class Button:
    def __init__(self, text='', background_color=(255, 255, 255), button_type='', hover=True, scale_factor=1.2, x=None, y=None, image=None):
        self.text = text
        self.background_color = background_color
        self.type = button_type
        self.hover_enabled = hover
        self.scale_factor = scale_factor
        self.image = image
        
        # Set up rectangles
        self.rect = self.text.text_rect.copy()
        self.padding = 10
        
        # Store position
        self.original_x = x if x is not None else self.rect.x
        self.original_y = y if y is not None else self.rect.y
        self.offset_x, self.offset_y = 0, 0
        
        # Set initial position if specified
        if x is not None or y is not None:
            self.set_offset(self.offset_x, self.offset_y)
        
        # Create clickable area with padding
        self.hover_rect = pygame.Rect(
            self.rect.x - self.padding,
            self.rect.y - self.padding,
            self.rect.width + (self.padding * 2),
            self.rect.height + (self.padding * 2)
        )
        
        # Store original surfaces
        self.original_text_surface = self.text.text
        
        # Scale background image if provided
        if self.image:
            self.original_image = pygame.transform.scale(
                self.image, 
                (self.image.get_width(), self.image.get_height())
            )
        else:
            self.original_image = None
        
        # Pre-calculate hover elements
        self._setup_hover_elements()
        
        # Track mouse state
        self.mouse_pressed = False
        self.mouse_released = False
        self.mouse_pos = pygame.mouse.get_pos()

    def set_offset(self, offset_x, offset_y):
        """Set the position offset of the button"""
        # Store the new offset
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # Calculate absolute positions based on original position plus offset
        absolute_x = self.original_x + self.offset_x
        absolute_y = self.original_y + self.offset_y
        
        # Update text rect position (not adding to existing position to avoid accumulation)
        self.rect.x = absolute_x
        self.rect.y = absolute_y
        
        # Update hover rect position using the text rect's position plus padding
        self.hover_rect.x = self.rect.x - self.padding
        self.hover_rect.y = self.rect.y - self.padding
        
        # Update scaled hover rect if it exists
        if hasattr(self, 'scaled_hover_rect'):
            # Center the scaled hover rect around the same center as the regular hover rect
            center_x, center_y = self.hover_rect.center
            self.scaled_hover_rect.center = (center_x, center_y)

    def set_image(self, image):
        """Set or change the button's background image"""
        self.image = image
        if self.image:
            # Scale to the hover_rect size
            self.original_image = pygame.transform.scale(
                self.image, 
                (self.image.get_width(), self.image.get_height())
            )
            
            # Also create the scaled version for hover state
            self.scaled_image = pygame.transform.scale(
                self.image,
                (self.image.get_width() * self.scale_factor, self.image.get_height() * self.scale_factor)
            )
        else:
            self.original_image = None
            self.scaled_image = None

    def _setup_hover_elements(self):
        # Create scaled text surface
        scaled_width = int(self.original_text_surface.get_width() * self.scale_factor)
        scaled_height = int(self.original_text_surface.get_height() * self.scale_factor)
        self.scaled_text_surface = pygame.transform.scale(
            self.original_text_surface, 
            (scaled_width, scaled_height)
        )
        
        # Create scaled hover rectangle
        center_x, center_y = self.hover_rect.center
        hover_width = int(self.hover_rect.width * self.scale_factor)
        hover_height = int(self.hover_rect.height * self.scale_factor)
        self.scaled_hover_rect = pygame.Rect(
            center_x - hover_width // 2,
            center_y - hover_height // 2,
            hover_width,
            hover_height
        )
        
        # Scale background image for hover state if available
        if self.image:
            self.scaled_image = pygame.transform.scale(
                self.image,
                (self.image.get_width() * self.scale_factor, self.image.get_height() * self.scale_factor)
            )
        else:
            self.scaled_image = None

    def update(self, mouse_pressed=None, mouse_released=None):
        self.mouse_pos = pygame.mouse.get_pos()
        if mouse_pressed is not None:
            self.mouse_pressed = mouse_pressed
        if mouse_released is not None:
            self.mouse_released = mouse_released
        
    def is_hovered(self):
        if self.image:
            # Create image rect with proper center position
            if self.hover_enabled and self.hover_rect.collidepoint(self.mouse_pos):
                # Use scaled image position when hovering
                image_rect = self.scaled_image.get_rect(center=self.scaled_hover_rect.center)
            else:
                # Use normal image position
                image_rect = self.original_image.get_rect(center=self.hover_rect.center)
            return self.hover_rect.collidepoint(self.mouse_pos) or image_rect.collidepoint(self.mouse_pos)
        else: 
            return self.hover_rect.collidepoint(self.mouse_pos)

    def is_clicked(self):
        return self.is_hovered() and self.mouse_released

    def blit(self, display, opacity=255):
        """
        Draw the button to the display with the specified opacity.
        
        Args:
            display: The display surface to draw on
            opacity: Opacity value (0-255, default=255 for fully opaque)
        """
        self.update()
        hovering = self.is_hovered() and self.hover_enabled
        
        rect_to_draw = self.scaled_hover_rect if hovering else self.hover_rect
        
        # Apply opacity to images and text
        if opacity < 255:
            # Draw background (either image or color)
            if hovering and self.scaled_image:
                # Create a copy of the scaled image with alpha
                temp_image = self.scaled_image.copy().convert_alpha()
                temp_image.fill((255, 255, 255, opacity), None, pygame.BLEND_RGBA_MULT)
                
                # Center the scaled image on the scaled hover rect
                scaled_image_rect = temp_image.get_rect(center=self.scaled_hover_rect.center)
                display.blit(temp_image, scaled_image_rect)
            elif self.original_image:
                # Create a copy of the original image with alpha
                temp_image = self.original_image.copy().convert_alpha()
                temp_image.fill((255, 255, 255, opacity), None, pygame.BLEND_RGBA_MULT)
                
                # Center the original image on the hover rect
                original_image_rect = temp_image.get_rect(center=self.hover_rect.center)
                display.blit(temp_image, original_image_rect)
            else:
                # For color background, create a transparent surface
                bg_surface = pygame.Surface(rect_to_draw.size, pygame.SRCALPHA)
                bg_color = (*self.background_color[:3], opacity)  # Add alpha to RGB color
                bg_surface.fill(bg_color)
                display.blit(bg_surface, rect_to_draw)
            
            # Draw text with opacity
            if hovering:
                # Create a copy of the scaled text with alpha
                temp_text = self.scaled_text_surface.copy().convert_alpha()
                temp_text.fill((255, 255, 255, opacity), None, pygame.BLEND_RGBA_MULT)
                
                scaled_text_rect = temp_text.get_rect(center=self.scaled_hover_rect.center)
                display.blit(temp_text, scaled_text_rect)
            else:
                # Create a copy of the original text with alpha
                temp_text = self.original_text_surface.copy().convert_alpha()
                temp_text.fill((255, 255, 255, opacity), None, pygame.BLEND_RGBA_MULT)
                
                display.blit(temp_text, self.rect)
        else:
            # Original behavior for full opacity
            if hovering and self.scaled_image:
                scaled_image_rect = self.scaled_image.get_rect(center=self.scaled_hover_rect.center)
                display.blit(self.scaled_image, scaled_image_rect)
            elif self.original_image:
                original_image_rect = self.original_image.get_rect(center=self.hover_rect.center)
                display.blit(self.original_image, original_image_rect)
            else:
                pygame.draw.rect(display, self.background_color, rect_to_draw)
            
            # Draw text
            if hovering:
                scaled_text_rect = self.scaled_text_surface.get_rect(center=self.scaled_hover_rect.center)
                display.blit(self.scaled_text_surface, scaled_text_rect)
            else:
                display.blit(self.original_text_surface, self.rect)
        
        # Debug visualization
        if SHOW_BUTTON_HITBOX:
            pygame.draw.rect(display, (255, 0, 0), self.hover_rect, 1)
            pygame.draw.circle(display, (0, 255, 0), self.mouse_pos, 3)