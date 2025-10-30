import pygame
import os
import sys

pygame.init()
pygame.font.init()

# Window
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Creepy Pasta Adventure")

# Colors and font
BG_COLOR = (15, 15, 20)
TEXT_COLOR = (230, 230, 230)
INPUT_BG = (30, 30, 35)
CURSOR_COLOR = (230, 230, 230)
FONT = pygame.font.SysFont("consolas", 20)
TITLE_FONT = pygame.font.SysFont("consolas", 30, bold=True)

# Save file
SAVE_FILE = "save_file.txt"

# Characters
character_name = "Garland"
protagonist_name = "Angel"
ghost_name = "Ghost"

# --- Helper to resolve paths inside .exe ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# --- Sound file mapping (organized in assets/sounds/) ---
SOUND_FILES = {
    "ghost": "assets/Ghost Speak Get Out - QuickSounds.com.mp3",
    "phasmophobia": "assets/Phasmophobia - QuickSounds.com.mp3",
    "blood_splat": "assets/BloodSplat - QuickSounds.com.mp3",
    "window_break": "assets/window-breaking-105533.mp3",
    "rip_blood_breach": "assets/RipBlood - QuickSounds.com.mp3",
    "ghost_breath": "assets/Ghostly Breath - QuickSounds.com.mp3",
    "whisper_flashes": "assets/Whisper Ghost - QuickSounds.com.mp3",
    "syringe_inject": "assets/SyringeInject - QuickSounds.com.mp3",
    "voice_isee_you": "assets/Voice I See you - QuickSounds.com.mp3",
}

# --- Initialize mixer ---
pygame.mixer.init()

# --- Load sounds safely ---
sounds = {}
for key, relative_path in SOUND_FILES.items():
    full_path = resource_path(relative_path)
    if os.path.exists(full_path):
        try:
            sounds[key] = pygame.mixer.Sound(full_path)
        except Exception as e:
            print(f"[sound load error] {relative_path}: {e}")
            sounds[key] = None
    else:
        print(f"[sound missing] {relative_path} not found")
        sounds[key] = None

# --- Sound play helpers ---
def play_sound(key, volume=1.0):
    s = sounds.get(key)
    if s:
        try:
            s.set_volume(max(0.0, min(1.0, volume)))
            s.play()
        except Exception as e:
            print(f"[sound play error] {key}: {e}")
    else:
        print(f"[sound missing] {key}")

# --- Specific triggers ---
def play_ghost_sound(): play_sound("ghost")
def play_phasmophobia(): play_sound("phasmophobia")
def play_BloodSplat(): play_sound("blood_splat")
def play_windowBreaking(): play_sound("window_break")
def play_RipBloodBreach(): play_sound("rip_blood_breach")
def play_GhostlyBreath(): play_sound("ghost_breath")
def play_WhisperGhostFlashes(): play_sound("whisper_flashes")
def play_SyringeInjectBloodPump(): play_sound("syringe_inject")
def play_VoiceISeeYou(): play_sound("voice_isee_you")

# --- Save / Load ---
def save_game(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write(state)
    append_log("✅ Game saved.")

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            state = f.read().strip()
        append_log("🔄 Game loaded.")
        return state
    else:
        append_log("⚠️ No saved game found.")
        return None

# --- Logging / Rendering utilities ---
log_lines = []  # list of strings to show in the text area (newest last)
input_text = ""
cursor_visible = True
cursor_timer = 0.0
CURSOR_BLINK = 0.5

def append_log(text):
    # Split long lines for display width
    max_chars = 90
    while len(text) > 0:
        if len(text) <= max_chars:
            log_lines.append(text)
            break
        else:
            log_lines.append(text[:max_chars])
            text = text[max_chars:]
    # limit lines to keep memory low
    while len(log_lines) > 200:
        log_lines.pop(0)

def clear_log():
    log_lines.clear()

def draw_ui():
    SCREEN.fill(BG_COLOR)
    # Title
    title_surf = TITLE_FONT.render("Creepy Pasta Adventure", True, TEXT_COLOR)
    SCREEN.blit(title_surf, (20, 12))

    # Text area (scroll from bottom)
    area_rect = pygame.Rect(20, 60, WIDTH - 40, HEIGHT - 160)
    pygame.draw.rect(SCREEN, (10, 10, 14), area_rect)
    # draw lines from bottom up
    line_h = FONT.get_linesize()
    lines_to_draw = (area_rect.h - 10) // line_h
    start = max(0, len(log_lines) - lines_to_draw)
    y = area_rect.y + 6
    for i in range(start, len(log_lines)):
        line = log_lines[i]
        surf = FONT.render(line, True, TEXT_COLOR)
        SCREEN.blit(surf, (area_rect.x + 6, y))
        y += line_h

    # Input box
    input_rect = pygame.Rect(20, HEIGHT - 80, WIDTH - 40, 48)
    pygame.draw.rect(SCREEN, INPUT_BG, input_rect, border_radius=6)
    # Prompt
    prompt_surf = FONT.render("> " + input_text, True, TEXT_COLOR)
    SCREEN.blit(prompt_surf, (input_rect.x + 8, input_rect.y + 12))
    # cursor
    global cursor_visible
    if cursor_visible:
        cursor_x = input_rect.x + 10 + prompt_surf.get_width()
        pygame.draw.rect(SCREEN, CURSOR_COLOR, (cursor_x, input_rect.y + 12, 2, FONT.get_height()))
    # hint
    hint = FONT.render("Type answers and press Enter. Type 'exit' to quit.", True, (120, 120, 120))
    SCREEN.blit(hint, (20, HEIGHT - 28))

    pygame.display.flip()

# --- Input handling wrapper for scene code ---
# Scenes will call request_input(prompt_text, callback)
waiting_callback = None
waiting_prompt = None

def request_input(prompt, callback):
    global waiting_callback, waiting_prompt, input_text
    waiting_callback = callback
    waiting_prompt = prompt
    input_text = ""
    append_log(prompt)

def submit_input(text):
    global waiting_callback, waiting_prompt
    if waiting_callback:
        cb = waiting_callback
        waiting_callback = None
        waiting_prompt = None
        append_log("> " + text)
        cb(text)
    else:
        append_log("> " + text)
        append_log("[No action bound to input]")

# --- Scenes ---
def new_game():
    clear_log()
    append_log("Starting new game...")
    intro_scene()

def intro_scene():
    append_log("You arrived at a new neighborhood.")
    append_log("CONGRATS!!!!! You got a new job within this area")
    append_log(f"Man, today is a great day, {protagonist_name}")
    append_log("Behind his house was a forest full of dark black trees, bats, wolves, and other anomalies.")
    append_log("Although he's frightened, he wants to turn back but stumbles upon a stranger.")
    append_log("Choose an option (type number or text):")
    append_log("1. OUCH!!!! Who are you")
    append_log("2. WHAT THE FUCK, MAN!!! WHY ARE YOU IN MY WAY!!!!")
    append_log("3. I DIDN'T SEE YOU HERE!!!!!")

    def on_choice(val):
        v = val.strip().lower()
        if v == "1" or v.startswith("ouch"):
            append_log(f"My name is {character_name}")
            request_input("Garland: (reply)", lambda r: garland_reply_goodmorning(r))
        elif v == "2" or "why are you in my way" in v:
            append_log("THAT'S RUDE!!!!! DO YOU HAVE ANY MANNERS!!!!")
            append_log(f"{protagonist_name}: OKAY!!! I'm a little vexed. Excuse my manners. What's your name?")
            append_log(f"My name is {character_name}")
            request_input("Garland: (hello/goodbye/other)", lambda r: garland_reply_hellogoodbye(r))
        elif v == "3" or "didn't see you" in v:
            append_log(f"OHHH!!!!! Excuse my manners. My name is {character_name}")
            request_input("Garland: (my bad?)", lambda r: garland_reply_mybad(r))
        else:
            append_log("Invalid choice. Proceeding anyway...")
            save_game("after_garland")
            ghost_encounter()

    request_input("Make your selection:", on_choice)

def garland_reply_goodmorning(reply):
    if reply.strip().lower().startswith("good morning"):
        append_log(f"How you doing, {protagonist_name}?")
        append_log("Nice house you got there.")
    else:
        append_log("Garland nods silently.")
    save_game("after_garland")
    ghost_encounter()

def garland_reply_hellogoodbye(reply):
    r = reply.strip().lower()
    if r == "hello":
        append_log(f"Nice to meet you, {protagonist_name}")
    elif r == "goodbye":
        append_log(f"Goodbye, {protagonist_name}")
    else:
        append_log(f"Sorry, {protagonist_name}")
    save_game("after_garland")
    ghost_encounter()

def garland_reply_mybad(reply):
    if reply.strip().lower().startswith("my bad"):
        append_log(f"My name is {character_name}")
        append_log("What's your name?")
        request_input("You (say: my name is ...)", lambda r: name_reply(r))
    else:
        append_log("Garland shrugs.")
        save_game("after_garland")
        ghost_encounter()

def name_reply(text):
    if text.strip().lower().startswith("my name is"):
        append_log("I'm sorry for bumping into you.")
    else:
        append_log(f"Nice to meet you, {text.strip()}.")
    save_game("after_garland")
    ghost_encounter()

def ghost_encounter():
    append_log("\nAfter meeting Garland, Angel decides to go to his new home.")
    append_log("After entering the house, he decides to cook some delicious food for dinner.")
    append_log("During cooking, he hears a strange sound...")
    play_ghost_sound()
    append_log("He sprints to the window and is startled to see a ghost waiting for him.")
    append_log("What would you like to do?")
    append_log("1. Throw candle at the ghost")
    append_log("2. Ask the ghost a question")
    append_log("3. Await the ghost's decision")

    def on_choice(val):
        v = val.strip().lower()
        if v == "1" or "throw candle" in v:
            append_log(f"The {ghost_name} begins to attack!")
            play_phasmophobia()
            append_log("Choose your next move:")
            append_log("1. He'll attack the ghost")
            append_log("2. Start to run away")
            append_log("3. Head to the forest")
            request_input("Next move:", ghost_next_move)
        elif v == "2" or "ask" in v:
            append_log(f"The {ghost_name} responds...")
            play_ghost_sound()
            append_log("It whispers cryptic things and then fades.")
            forest_encounter()
        elif v == "3" or "await" in v:
            append_log(f"The {ghost_name} prepares to attack.")
            play_phasmophobia()
            append_log("You avoided the attack.")
            play_windowBreaking()
            append_log("You jump out the window.")
            forest_encounter()
        else:
            append_log("You died.")
            play_RipBloodBreach()

    request_input("Make your choice:", on_choice)

def ghost_next_move(val):
    v = val.strip().lower()
    if v == "1" or "attack" in v:
        append_log("Angel lies in a pool of his own blood.")
        play_BloodSplat()
        append_log("RIP!!!!!")
    elif v == "2" or "run" in v:
        append_log("He jumps out the window and runs into the forest.")
        play_windowBreaking()
        forest_encounter()
    elif v == "3" or "forest" in v:
        append_log("The ghost stops him.")
        play_phasmophobia()
        append_log("He passed away.")
    else:
        append_log("You died.")

def forest_encounter():
    append_log("\nAfter running into the forest with watery eyes...")
    append_log(f"{protagonist_name} discovers a tall individual with stark black hair and blue eyes.")
    append_log(f"{protagonist_name} realizes it is {character_name}.")
    append_log("He decides to talk to them about a strange phenomenon he saw at the house.")
    append_log("1. Hey, there's a ghost chasing after me")
    append_log("2. I just got away from the ghost")
    append_log("3. Did you see the ghost")

    def on_choice(val):
        v = val.strip().lower()
        if v == "1" or "ghost chasing" in v:
            append_log("1. A GHOST!!!!!")
            append_log("2. I just got away from the ghost too.")
            append_log("3. Are you alright, and a ghost chasing after you?")
            request_input("Garland chooses:", garland_follows)
        elif v == "2" or "got away" in v:
            append_log(f"{character_name} says: Let's book it!")
            play_BloodSplat()
            append_log("Garland passed away.")
        elif v == "3" or "did you see" in v:
            append_log(f"{character_name} says: That ghost has been haunting me for weeks.")
            append_log("We need to leave before he—")
            play_SyringeInjectBloodPump()
            play_WhisperGhostFlashes()
            play_VoiceISeeYou()
            play_BloodSplat()
            append_log("Garland passed away.")
        else:
            append_log("TO BE CONTINUED!!!!!")

    request_input("Make your choice:", on_choice)

def garland_follows(val):
    v = val.strip().lower()
    if v == "1" or "a ghost" in v:
        append_log("Are you okay? I recall a ghost chasing me earlier.")
        append_log("Do you need a helping hand before the ghost—")
        play_GhostlyBreath()
        append_log("Let's get out of here.")
        play_BloodSplat()
        append_log("Garland passed away.")
    elif v == "2" or "i just got away" in v:
        append_log("Was the ghost at your house?")
        request_input("You (yes/no):", lambda r: garland_helper_answer(r))
    elif v == "3" or "did you see" in v:
        append_log("Let's run for it!")
        play_BloodSplat()
        append_log("Garland passed away.")
    else:
        append_log("Confusion spreads. TO BE CONTINUED!!!!!")

def garland_helper_answer(val):
    if val.strip().lower().startswith("y"):
        append_log("Okay, we need to get going then.")
        append_log("SHIT!!!! Hopefully we can escape before he—")
        play_WhisperGhostFlashes()
        append_log("Garland passed away.")
    else:
        append_log("You decide to move carefully through the trees.")

# --- Main menu and runner ---
def main_menu_scene():
    clear_log()
    append_log("Welcome to Creepy Pasta Adventure")
    append_log("1. New Game")
    append_log("2. Load Game")
    request_input("Select 1 or 2:", main_menu_choice)

def main_menu_choice(val):
    v = val.strip().lower()
    if v == "1" or v.startswith("new"):
        new_game()
    elif v == "2" or v.startswith("load"):
        state = load_game()
        if state == "after_garland":
            ghost_encounter()
        else:
            append_log("No valid save found. Starting new game...")
            new_game()
    else:
        append_log("Invalid selection. Type 1 or 2 or 'exit' to quit.")
        request_input("Select 1 or 2:", main_menu_choice)

# --- Main game loop ---
clock = pygame.time.Clock()
running = True

main_menu_scene()

while running:
    dt = clock.tick(30) / 1000.0
    cursor_timer += dt
    if cursor_timer >= CURSOR_BLINK:
        cursor_timer = 0.0
        cursor_visible = not cursor_visible

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                text = input_text.strip()
                input_text = ""
                if text.lower() == "exit":
                    running = False
                else:
                    submit_input(text)
            elif event.key == pygame.K_ESCAPE:
                running = False
            else:
                # ignore control characters; add printable
                if event.unicode and ord(event.unicode) >= 32:
                    input_text += event.unicode

    draw_ui()

pygame.quit()
sys.exit(0)