from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import random

# Configuration for the LED matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2  # For two displays
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.brightness = 50  # Reduce brightness to reduce power load
options.pwm_bits = 11  # Increase PWM bits for smoother gradients
options.pwm_lsb_nanoseconds = 120  # Adjust PWM timing to reduce flicker
matrix = RGBMatrix(options=options)

# Game variables
player_x = 64
player_y = 26  # Player position higher to avoid being cut off
player_width = 3  # Smaller player width
player_direction = 1  # Direction: 1 = right, -1 = left
player_projectiles = []

bases = [(16, 24), (48, 24), (80, 24), (112, 24)]  # Move bases higher
base_health = {base: 3 for base in bases}  # Each base can take 3 hits

invaders = []
invader_width = 3
invader_height = 2
rows = 4  # 4 rows of invaders
cols = 10
invader_direction = 1  # Moving right initially
invader_speed = 0.1
invader_projectiles = []
score = 0
lives = 3
fire_chance = 0.01  # Chance for an invader to fire a projectile
player_fire_chance = 0.05  # Chance for the player to shoot
frame_delay = 0.05

# Create invaders in compact formation, scaled down
def reset_invaders():
    global invaders
    invaders = []
    for row in range(rows):
        for col in range(cols):
            invaders.append((col * (invader_width + 2) + 6, row * (invader_height + 2) + 2))

reset_invaders()

# Set up text color and smaller font
font = graphics.Font()
font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/4x6.bdf")  # Adjust path to your font file
text_color = graphics.Color(0, 255, 0)

def draw_player():
    for i in range(player_width):
        matrix.SetPixel(player_x + i, player_y, 0, 255, 0)  # Green player

def draw_bases():
    for base, health in base_health.items():
        for i in range(health):
            matrix.SetPixel(base[0] + i, base[1], 0, 255, 0)  # Green base segments

def draw_invaders():
    colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0)]  # Different colors per row
    for index, invader in enumerate(invaders):
        row = index // cols
        color = colors[row]
        for x in range(invader_width):
            for y in range(invader_height):
                matrix.SetPixel(invader[0] + x, invader[1] + y, *color)

def draw_projectiles():
    for proj in invader_projectiles:
        matrix.SetPixel(proj[0], proj[1], 255, 255, 255)  # White projectile
    for proj in player_projectiles:
        matrix.SetPixel(proj[0], proj[1], 255, 0, 0)  # Red projectile for player

def move_invaders():
    global invader_direction, invaders
    move_down = False

    # Check if invaders hit the edge and change direction
    for invader in invaders:
        if invader[0] <= 0 and invader_direction == -1:
            invader_direction = 1
            move_down = True
            break
        if invader[0] + invader_width >= 127 and invader_direction == 1:
            invader_direction = -1
            move_down = True
            break

    # Move invaders down if necessary and adjust their position
    for i in range(len(invaders)):
        x, y = invaders[i]
        x += invader_direction
        if move_down:
            y += invader_height  # Move down
        if y + invader_height >= 24:  # Check if invaders reach the bases level
            reset_invaders()
            break
        invaders[i] = (x, y)

def move_projectiles():
    # Move invader projectiles down
    for i in range(len(invader_projectiles)):
        x, y = invader_projectiles[i]
        invader_projectiles[i] = (x, y + 1)
    # Remove projectiles out of bounds
    invader_projectiles[:] = [proj for proj in invader_projectiles if proj[1] <= 31]

    # Move player projectiles up (always vertical)
    for i in range(len(player_projectiles)):
        x, y = player_projectiles[i]
        player_projectiles[i] = (x, y - 1)
    # Remove player projectiles out of bounds
    player_projectiles[:] = [proj for proj in player_projectiles if proj[1] >= 0]

def move_player():
    global player_x, player_direction

    # Move player left or right
    player_x += player_direction

    # Randomly change direction 20% of the time
    if random.random() < 0.2:
        player_direction *= -1

    # Keep player within screen boundaries
    if player_x <= 0:
        player_x = 0
        player_direction = 1
    elif player_x >= 125:
        player_x = 125
        player_direction = -1

def check_collisions():
    global score
    # Check for collisions between projectiles and bases
    for proj in invader_projectiles:
        for base, health in base_health.items():
            if base[0] <= proj[0] < base[0] + health and proj[1] == base[1]:
                invader_projectiles.remove(proj)
                base_health[base] -= 1  # Decrease base health
                break

    # Check for collisions between player projectiles and invaders
    for proj in player_projectiles:
        for invader in invaders:
            if invader[0] <= proj[0] < invader[0] + invader_width and invader[1] <= proj[1] < invader[1] + invader_height:
                player_projectiles.remove(proj)
                invaders.remove(invader)
                score += 10
                break

def invader_fire():
    # Only allow one invader to shoot at a time
    if len(invader_projectiles) < 1:
        shooter = random.choice(invaders)
        invader_projectiles.append((shooter[0] + invader_width // 2, shooter[1] + invader_height))

def player_fire():
    # Player shoots vertically (no angle)
    if random.random() < player_fire_chance:
        player_projectiles.append((player_x + player_width // 2, player_y - 1))

try:
    while True:
        # Update only the necessary parts of the screen
        matrix.Fill(0, 0, 0)  # Clear screen without flicker

        # Draw game elements
        draw_player()
        draw_bases()
        draw_invaders()
        draw_projectiles()

        # Move game elements
        move_invaders()
        move_projectiles()
        move_player()

        # Check for collisions
        check_collisions()

        # Invaders shoot randomly (one at a time)
        invader_fire()

        # Player shoots randomly
        player_fire()

        # Display score and lives
        graphics.DrawText(matrix, font, 1, 5, text_color, f"SCORE {score}")
        graphics.DrawText(matrix, font, 100, 5, text_color, f"LIVES {lives}")

        # Delay for frame rate control
        time.sleep(frame_delay)

except KeyboardInterrupt:
    matrix.Clear()
