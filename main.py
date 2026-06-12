import pygame
import sys
import random
import textwrap

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 650
GRAPHIC_H = 350
CONSOLE_H = HEIGHT - GRAPHIC_H
MAX_CHARS_PER_LINE = 75  # Safe wrapping limit for an 800px wide window

# Retro 80s Colors
BLACK = (0, 0, 0)
TERM_GREEN = (50, 255, 50)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
BLUE = (0, 102, 204)
RED = (220, 20, 60)
ORANGE = (230, 90, 20)
YELLOW = (255, 215, 0)
ALLEY_BG = (20, 20, 35)
LOBBY_BG = (220, 220, 230)
SERVER_BG = (10, 20, 15)
LASER_RED = (255, 0, 0)
MAINFRAME_GLOW = (0, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chris vs InPhase: The Grand Infiltration")
font = pygame.font.SysFont("courier", 16, bold=True)

# --- ADVANCED GAME STATE ---
state = {
    'room': 'alley',
    'inventory': [],
    'searched_objects': set(),
    'vent_open': False,
    'lobby_door_unlocked': False,
    'laser_grid_active': True,
    'puzzle_solved': False,
    'target_resonance': random.randint(35, 55),
    'phases': [12, 18, 5, 22, 15, 9]
}

state['phases'][0] = state['target_resonance'] - (state['phases'][1] + state['phases'][2])

# --- COMPLEX ROOM ARCHITECTURE ---
rooms = {
    'alley': {
        'name': "Dark Alleyway (Level 1)",
        'desc': "You stand in a rain-slicked alley behind InPhase HQ. A heavy security door sits to the north. A dented trash bin rests in the corner.",
        'exits': {'north': 'lobby'}
    },
    'lobby': {
        'name': "Main Lobby (Level 2)",
        'desc': "A pristine, marble-floored reception area. To the north is an electronic blast door. On the wall, there is a closed ventilation shaft. The alley is back south.",
        'exits': {'south': 'alley', 'north': 'server_room', 'up': 'vent_shaft'}
    },
    'vent_shaft': {
        'name': "Maintenance Shaft (Level 3)",
        'desc': "A cramped, dusty air duct running above the facility floors. Dropping down leads into the Security Hub.",
        'exits': {'down': 'security_hub'}
    },
    'security_hub': {
        'name': "Security Control Room (Level 4)",
        'desc': "Monitors flicker with camera feeds. A primary control desk is littered with papers. A massive network switch hums against the wall. An exit door leads east.",
        'exits': {'east': 'hallway'}
    },
    'hallway': {
        'name': "Secure Corridor (Level 5)",
        'desc': "A fluorescent-lit hallway. To the west is the Security Hub. To the south is a secondary back entrance into the Main Lobby. A red laser grid blocks the path east.",
        'exits': {'west': 'security_hub', 'south': 'lobby', 'east': 'mainframe_core'}
    },
    'mainframe_core': {
        'name': "The InPhase Mainframe Core (Final Level)",
        'desc': "The heart of the beast. Towering server racks surround a central terminal glowing brightly. The security mainframe lock is engaged.",
        'exits': {'west': 'hallway'}
    }
}

# SCROLL SYSTEM VARIABLES
master_log = []  # Keeps EVERY line of text generated
scroll_offset = 0  # Tracks how far up the player has scrolled
current_input = ""


def print_to_console(text):
    """Splits text into wrapped lines and adds them to the master log."""
    global scroll_offset
    wrapped_lines = textwrap.wrap(text, width=MAX_CHARS_PER_LINE)
    for line in wrapped_lines:
        master_log.append(line)

    # Automatically snap scroll back to the bottom when new text arrives
    scroll_offset = 0


# Initialize the log with the starting room info
print_to_console("DM: Welcome back, Chris. Your mission to breach InPhase begins.")
print_to_console("DM: Type 'look' to view your surroundings.")


def parse_command(command):
    cmd = command.strip().lower()
    if not cmd:
        return

    print_to_console(f"> {cmd}")
    parts = cmd.split(maxsplit=2)
    verb = parts[0]
    noun = parts[1] if len(parts) > 1 else ""
    extra = parts[2] if len(parts) > 2 else ""

    # --- 1. GENERAL COMMANDS ---
    if verb in ['look', 'examine']:
        if not noun:
            print_to_console(rooms[state['room']]['desc'])
            if state['room'] == 'lobby' and not state['lobby_door_unlocked']:
                print_to_console("The blast door to the north is magnetically sealed.")
            if state['room'] == 'hallway' and state['laser_grid_active']:
                print_to_console("A cross-hatched laser grid completely covers the eastern passage.")
        elif noun == 'bin' and state['room'] == 'alley':
            print_to_console(
                "It's full of shredded corporate documents. Something metallic glints at the bottom. Try searching it.")
        elif noun == 'desk' and state['room'] == 'security_hub':
            print_to_console("The desk holds a terminal screen asking for a password, and a discarded keycard.")
        elif noun == 'switch' and state['room'] == 'security_hub':
            print_to_console("It routes power to the facility grids. Thick red cables run into the wall.")
        elif noun == 'terminal' and state['room'] == 'mainframe_core':
            print_to_console(f"InPhase Sub-System Lockout. Current Target Resonance: {state['target_resonance']} MHz.")
            print_to_console(f"Available frequency waves: {state['phases']}")
            print_to_console("Rule: Type 'align [num1] [num2] [num3]' to sync the frequency sums.")
        else:
            print_to_console(f"You don't see anything unusual about the {noun}.")

    elif verb in ['inventory', 'inv']:
        if not state['inventory']:
            print_to_console("Your inventory is currently empty.")
        else:
            print_to_console(f"Carrying: {', '.join(state['inventory'])}")

    # --- 2. SEARCH ENGINE ---
    elif verb == 'search':
        if noun == 'bin' and state['room'] == 'alley':
            if 'screwdriver' not in state['inventory'] and 'screwdriver' not in state['searched_objects']:
                print_to_console("You rummage through the bin and find a heavy-duty screwdriver!")
                state['inventory'].append('screwdriver')
            else:
                print_to_console("There's nothing else useful inside the bin.")
        elif noun == 'desk' and state['room'] == 'security_hub':
            if 'keycard' not in state['inventory'] and 'keycard' not in state['searched_objects']:
                print_to_console("You find a high-clearance InPhase Keycard tucked under a manual!")
                state['inventory'].append('keycard')
            else:
                print_to_console("The desk contains nothing but empty coffee cups now.")
        else:
            print_to_console("You don't find anything valuable there.")

    # --- 3. ITEM USE ENGINE ---
    elif verb == 'use':
        if noun == 'screwdriver':
            if 'screwdriver' in state['inventory'] and state['room'] == 'lobby':
                state['vent_open'] = True
                print_to_console("You unscrew the grates of the ventilation shaft! You can now climb 'up'.")
            else:
                print_to_console("You can't find a practical use for the screwdriver here.")
        elif noun == 'keycard':
            if 'keycard' in state['inventory'] and state['room'] == 'lobby':
                state['lobby_door_unlocked'] = True
                print_to_console("You swipe the keycard at the blast door. The heavy magnets disengage with a hiss!")
            else:
                print_to_console("There's nowhere to swipe a keycard here.")
        else:
            print_to_console("Use what? (Syntax: use [item_name])")

    # --- 4. ENVIRONMENT ACTIONS & PUZZLES ---
    elif verb == 'hack' or (verb == 'enter' and noun == 'switch'):
        if state['room'] == 'security_hub':
            if state['laser_grid_active']:
                state['laser_grid_active'] = False
                print_to_console(
                    "You interface with the primary network switch and override the laser grid power relays.")
            else:
                print_to_console("The laser grids are already offline.")
        else:
            print_to_console("There is nothing here vulnerable to basic network injection hacks.")

    elif verb == 'align':
        if state['room'] != 'mainframe_core':
            print_to_console("You need to be at the core terminal to run phase alignment vectors.")
            return
        try:
            nums = [int(noun), int(extra.split()[0]), int(extra.split()[1])]
            if all(n in state['phases'] for n in nums) and len(set(nums)) == 3:
                if sum(nums) == state['target_resonance']:
                    state['puzzle_solved'] = True
                    print_to_console("==================================================")
                    print_to_console("SUCCESS! PHASES MATCH. INPHASE SYSTEM DEFANGED.")
                    print_to_console("MISSION COMPLETE. CRITICAL CORE DOWNLOADED. YOU WIN!")
                    print_to_console("==================================================")
                else:
                    print_to_console(
                        f"Alignment Error: Wave sum is {sum(nums)} MHz. Target is {state['target_resonance']} MHz.")
            else:
                print_to_console("Invalid wave parameters chosen from the matrix pool.")
        except (ValueError, IndexError):
            print_to_console("Syntax error. Use: align [num1] [num2] [num3]")

    # --- 5. MOVEMENT PARSER ---
    elif verb in ['go', 'walk', 'move', 'climb']:
        direction = noun if noun else verb
        if direction in ['up', 'down', 'north', 'south', 'east', 'west']:
            if direction in rooms[state['room']]['exits']:
                target = rooms[state['room']]['exits'][direction]

                if state['room'] == 'lobby' and direction == 'up' and not state['vent_open']:
                    print_to_console("The ventilation grill is bolted tightly shut. You need a tool to open it.")
                    return
                if state['room'] == 'lobby' and direction == 'north' and not state['lobby_door_unlocked']:
                    print_to_console("The electronic blast door refuses to budge. It requires authorization.")
                    return
                if state['room'] == 'hallway' and direction == 'east' and state['laser_grid_active']:
                    print_to_console("ZAP! The laser grid triggers a defense matrix. You are forced back.")
                    return

                state['room'] = target
                print_to_console(f"--- Entering {rooms[state['room']]['name']} ---")
                print_to_console(rooms[state['room']]['desc'])
            else:
                print_to_console("You hit a wall. You cannot head in that direction.")
        else:
            print_to_console("Go where? (e.g., go north, go south, go up)")
    else:
        print_to_console("Unknown protocol command string. Type 'look' to scan the environment.")


# --- GRAPHICS ENGINE ---
def draw_ginger_portrait(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, 90, 110), border_radius=4)
    pygame.draw.rect(screen, (255, 218, 185), (x + 15, y + 25, 60, 60), border_radius=8)
    pygame.draw.ellipse(screen, ORANGE, (x + 10, y + 5, 70, 35))
    pygame.draw.rect(screen, BLACK, (x + 30, y + 45, 8, 8))
    pygame.draw.rect(screen, BLACK, (x + 52, y + 45, 8, 8))
    pygame.draw.rect(screen, RED, (x + 20, y + 85, 50, 25), border_radius=4)


def draw_level_visuals():
    room = state['room']
    pygame.draw.rect(screen, GREY, (10, 10, WIDTH - 20, GRAPHIC_H - 20), 4)

    if room == 'alley':
        screen.fill(ALLEY_BG, (14, 14, WIDTH - 28, GRAPHIC_H - 28))
        for i in range(15):
            pygame.draw.line(screen, (50, 50, 70), (15, 40 + i * 20), (WIDTH - 15, 40 + i * 20), 2)
        pygame.draw.rect(screen, GREY, (350, 120, 110, 210))
        pygame.draw.rect(screen, BLACK, (360, 130, 90, 190))
        pygame.draw.circle(screen, RED, (375, 220), 6)
        pygame.draw.rect(screen, (70, 80, 75), (100, 220, 80, 110))
        pygame.draw.line(screen, BLACK, (100, 240), (180, 240), 3)

    elif room == 'lobby':
        screen.fill(LOBBY_BG, (14, 14, WIDTH - 28, GRAPHIC_H - 28))
        door_color = BLACK if state['lobby_door_unlocked'] else GREY
        pygame.draw.rect(screen, door_color, (300, 100, 200, 230))
        if not state['lobby_door_unlocked']:
            pygame.draw.line(screen, YELLOW, (300, 215), (500, 215), 6)
        vent_color = BLACK if state['vent_open'] else (60, 60, 60)
        pygame.draw.rect(screen, vent_color, (50, 60, 90, 60))
        if not state['vent_open']:
            for i in range(5):
                pygame.draw.line(screen, WHITE, (55 + i * 16, 60), (55 + i * 16, 120), 2)

    elif room == 'vent_shaft':
        screen.fill(BLACK, (14, 14, WIDTH - 28, GRAPHIC_H - 28))
        pygame.draw.line(screen, GREY, (14, 14), (250, 150), 3)
        pygame.draw.line(screen, GREY, (WIDTH - 14, 14), (550, 150), 3)
        pygame.draw.line(screen, GREY, (14, GRAPHIC_H - 14), (250, 250), 3)
        pygame.draw.line(screen, GREY, (WIDTH - 14, GRAPHIC_H - 14), (550, 250), 3)
        pygame.draw.rect(screen, GREY, (250, 150, 300, 100), 2)

    elif room == 'security_hub':
        screen.fill((30, 35, 45), (14, 14, WIDTH - 28, GRAPHIC_H - 28))
        pygame.draw.rect(screen, (20, 20, 20), (80, 80, 140, 250))
        switch_led = TERM_GREEN if not state['laser_grid_active'] else RED
        pygame.draw.circle(screen, switch_led, (150, 150), 12)
        pygame.draw.rect(screen, (50, 55, 60), (320, 200, 250, 130))
        pygame.draw.rect(screen, BLACK, (380, 120, 130, 80))
        pygame.draw.rect(screen, BLUE, (390, 130, 110, 60))

    elif room == 'hallway':
        screen.fill((40, 40, 45), (14, 14, WIDTH - 28, GRAPHIC_H - 28))
        pygame.draw.polygon(screen, (20, 20, 25), [(14, 336), (250, 250), (550, 250), (WIDTH - 14, 336)])
        if state['laser_grid_active']:
            for i in range(6):
                pygame.draw.line(screen, RED, (500 + i * 15, 100), (450 + i * 35, 330), 3)
                pygame.draw.line(screen, RED, (450, 120 + i * 25), (650, 180 + i * 15), 3)

    elif room == 'mainframe_core':
        screen.fill(BLACK, (14, 14, WIDTH - 28, GRAPHIC_H - 28))
        pygame.draw.rect(screen, (15, 15, 25), (280, 40, 240, 290))
        core_color = TERM_GREEN if state['puzzle_solved'] else BLUE
        for i in range(8):
            pygame.draw.line(screen, core_color, (300, 60 + i * 30), (500, 60 + i * 30), 4)
            if not state['puzzle_solved'] and random.random() > 0.4:
                pygame.draw.circle(screen, WHITE, (320 + i * 20, 60 + i * 30), 5)

    draw_ginger_portrait(WIDTH - 115, 20)


# --- SYSTEM LOOPS ---
clock = pygame.time.Clock()
running = True

while running:
    # 1. CAPTURE INPUTS & SCROLL EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel scroll up
                if scroll_offset < len(master_log) - 10:
                    scroll_offset += 1
            elif event.button == 5:  # Mouse wheel scroll down
                if scroll_offset > 0:
                    scroll_offset -= 1

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                if scroll_offset < len(master_log) - 10:
                    scroll_offset = min(len(master_log) - 10, scroll_offset + 3)
            elif event.key == pygame.K_PAGEDOWN:
                if scroll_offset > 0:
                    scroll_offset = max(0, scroll_offset - 3)
            elif event.key == pygame.K_RETURN:
                parse_command(current_input)
                current_input = ""
            elif event.key == pygame.K_BACKSPACE:
                current_input = current_input[:-1]
            else:
                if event.unicode.isprintable():
                    current_input += event.unicode

    # 2. DRAW ROOM RENDER TILES
    screen.fill(BLACK)
    draw_level_visuals()

    # 3. DRAW SCROLLABLE CONSOLE WINDOW
    pygame.draw.rect(screen, BLACK, (0, GRAPHIC_H, WIDTH, CONSOLE_H))
    pygame.draw.line(screen, TERM_GREEN, (0, GRAPHIC_H), (WIDTH, GRAPHIC_H), 3)

    # Calculate exactly which lines of text to render based on scroll positions
    max_visible_lines = 11
    # If scroll_offset is 0, we look at the very end of our log
    start_idx = max(0, len(master_log) - max_visible_lines - scroll_offset)
    end_idx = max(0, len(master_log) - scroll_offset)
    visible_lines = master_log[start_idx:end_idx]

    y_pos = GRAPHIC_H + 15
    for line in visible_lines:
        rendered_line = font.render(line, True, TERM_GREEN)
        screen.blit(rendered_line, (25, y_pos))
        y_pos += 20

    # Draw a little scroll indicator if player has scrolled upwards
    if scroll_offset > 0:
        indicator = font.render(f"[SCROLLED UP - {scroll_offset} LINES]", True, YELLOW)
        screen.blit(indicator, (WIDTH - 250, GRAPHIC_H + 15))

    # Input text line trace prompt
    prompt_surface = font.render(f"CHRIS@INPHASE_LAPTOP:~# {current_input}_", True, WHITE)
    pygame.draw.rect(screen, BLACK, (0, HEIGHT - 45, WIDTH, 45))  # Prevents overlapping text collisions
    screen.blit(prompt_surface, (25, HEIGHT - 35))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()