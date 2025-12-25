import tkinter as tk
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

DISPLAY_SIZE = (screen_width, screen_height)
#DISPLAY_SIZE = (1920, 1080)
FPS = 60

TILE_SIZE = DISPLAY_SIZE[0] * 3 // 80

PLAYER_SPEED = 10.4 * TILE_SIZE / 60
PLAYER_HITBOX = 0.7 # precent


PLAYER_POS = [0.5, 0.5]

# Needs to be changed for every new gamemode added
GRAVITY = {'cube': (1.06 / 48) * TILE_SIZE, 'ball': (0.7 / 48) * TILE_SIZE}   # Downward acceleration per frame
GAMEMODES= ('ball', 'cube', 'wave', 'ship')
GROUND_GAMEMODES = {'cube', 'ball'}
PLAYERS_SIZE = {'cube': (TILE_SIZE*9.5//10, TILE_SIZE*9.5//10), 'wave': (TILE_SIZE//2, TILE_SIZE//2), 'ball': (TILE_SIZE*9.5//10, TILE_SIZE*9.5//10), 'ship': (TILE_SIZE*14//10 * 0.5, TILE_SIZE*14//10 * 0.5)}
PLAYERS_IMAGE_SIZE = {
        'cube': PLAYERS_SIZE['cube'],
        'wave': (PLAYERS_SIZE['wave'][0]*1.4, PLAYERS_SIZE['wave'][1]*1.4),
        'ball': PLAYERS_SIZE['ball'],
        'ship': (PLAYERS_SIZE['ship'][0]/0.6, PLAYERS_SIZE['ship'][1]/0.6),
    }
PLAYER_VELOCITY = {'cube': (16 / 48) * TILE_SIZE, 'wave': PLAYER_SPEED, 'ball': (2/ 48) * TILE_SIZE, 'ship': (16 / 48) * TILE_SIZE}
MAX_VELOCITY = {'cube': (16 / 48) * TILE_SIZE, 'ball': (16 / 48) * TILE_SIZE, 'ship': (16 / 48) * TILE_SIZE}
# Ship tuning: fraction of steering applied each frame and damping to smooth movement
SHIP_STEER_FACTOR = 0.12  # apply ~12% of steering 'desired' per frame (tune for feel)
SHIP_DRAG = 0.02  # velocity is multiplied by (1 - SHIP_DRAG) each frame to add gentle damping
SHIP_IMPULSE_DECAY = 0.12  # per-frame decay fraction for residual ship impulse from orbs
ORB_AIR_MULTIPLIER = 0.75  # fraction of orb velocity applied when used in-air (non-ship)
ORB_JUMP = {'yellow': {'cube': (16 / 48) * TILE_SIZE, 'ball': (10.5/ 48) * TILE_SIZE, 'ship': (2 / 48) * TILE_SIZE},
            'green': {'cube': (16 / 48) * TILE_SIZE, 'ball': (10.5 / 48) * TILE_SIZE, 'ship': (2 / 48) * TILE_SIZE},
            'blue': {'cube': -(8 / 48) * TILE_SIZE, 'ball': -(6 / 48) * TILE_SIZE, 'ship': (10.5 / 48) * TILE_SIZE}}

PHYSICS_TILES = {'grass', 'stone', 'sand', 'pinkgrass'}
INTERACTIVE_TILES = {'portal', 'spike', 'finish', 'orb'}
AUTOTILE_TYPES = {'grass', 'stone', 'pinkgrass'}
ORBS = ('blue', 'green', 'yellow')
SPIKE_SIZE = (0.4, 0.6) # precent
FONT = 'data/fonts/PixelifySans-VariableFont_wght.ttf'

TILE_TYPE_MAP = {
    0: PHYSICS_TILES,
    1: {'spike'},
    2: {'finish'},
    # Add other tile types and their variants as needed
}

EDITOR_SCROLL = (8 / 48) * TILE_SIZE
EDITOR_SCROLL_FAST = (40 / 48) * TILE_SIZE
LEVEL_SELECTOR_SCROLL = DISPLAY_SIZE[0] * 6 // 100 // 3
EDITOR_TILE_MENU_SIZE = DISPLAY_SIZE[1] // 3
TILE_MENU_COLUMNS = 6
TILE_MENU_ROWS = 2

DIFFICULTIES = ('easy', 'normal', 'hard', 'harder', 'insane', 'demon')
SORTING = ('difficulty', 'recent')


#debugging
DRAW_PLAYER_HITBOX = False
SHOW_BUTTON_HITBOX = False
SHOW_SPIKE_HITBOX = False
SHOW_FPS_COUNTER = False
