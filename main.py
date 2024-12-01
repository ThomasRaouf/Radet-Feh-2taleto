import sys, math, time, pygame

pygame.init()

WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Radet Feh 2taleto")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()

intro_text = """
By the students of October STEM School 11th District


Team 31

Code: Thomas Raouf
Soundtracks: David Amgad
Illustrations: Marwan Shaaban & Marwan Mahmoud


This minigame was created for the "Hackclub Counterspell Giza" game jam in 
about 4.5 hours with no prior game coding experience (so please excuse any bugs! XD). 
It includes only one demo level.


How to play:

Point at where you want to shoot the bullets 
(which will act as a thrust to move the player) and left-click.
Your goal is to reach the victory point, 
represented by a green square in the bottom-right corner of the screen.



CLICK ANYWHERE TO CONTINUE
"""

# Text Rendering
def render_text(text, font, color, x, y):
    lines = text.split("\n")
    total_height = sum([font.get_height() for line in lines])
    current_height = y - total_height // 2
    for line in lines:
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x - text_surface.get_width() // 2, current_height))
        current_height += font.get_height()

def fade_screen(fade_in=True):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    alpha = 0 if fade_in else 255
    increment = 5 if fade_in else -5
    
    while (fade_in and alpha < 255) or (not fade_in and alpha > 0):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)
        alpha += increment

def intro_screen():
    screen.fill(BLACK)

    # Fade In
    fade_screen(fade_in=True)

    # Render the intro text
    render_text(intro_text, font, WHITE, WIDTH // 2, HEIGHT // 2)

    pygame.display.flip()

    # Wait for a click to continue
    waiting_for_click = True
    while waiting_for_click:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Fade Out and then exit the intro screen
                fade_screen(fade_in=False)
                waiting_for_click = False

shoot_sound = pygame.mixer.Sound("assets/shot.mp3")  
damage_sound = pygame.mixer.Sound("assets/damage.mp3")  
main_menu_music = "assets/main music.mp3"  
gameover_music = "assets/gameover.mp3"  
congrats_music = "assets/congrats.mp3"  

player_size = 40
player_pos = [50, 50]
player_velocity = [0, 0]
player_health = 100

player_skin = pygame.image.load("assets/player.png")
player_skin = pygame.transform.scale(player_skin, (player_size, player_size))

bullets = []
bullet_speed = 10
bullet_radius = 5


walls = [
    pygame.Rect(0, 0, 1200, 20),  
    pygame.Rect(0, 0, 20, 900),   
    pygame.Rect(1180, 0, 20, 900), 
    pygame.Rect(0, 880, 1200, 20), 

    pygame.Rect(200, 100, 400, 20),  
    pygame.Rect(200, 250, 400, 20),  
    pygame.Rect(600, 150, 20, 200),  
    pygame.Rect(800, 250, 20, 200),  
    pygame.Rect(400, 400, 400, 20),  
    pygame.Rect(300, 500, 20, 200),  
    pygame.Rect(600, 600, 200, 20),  
    pygame.Rect(200, 700, 400, 20),  
    pygame.Rect(400, 750, 20, 150),  

    pygame.Rect(500, 700, 100, 20),  
    pygame.Rect(700, 400, 100, 20),  
    pygame.Rect(900, 200, 20, 100),  
]

exit_rect = pygame.Rect(1100, 800, 100, 100)

game_logo = pygame.image.load("assets/logo.png")  
game_logo = pygame.transform.scale(game_logo, (800, 240))  
start_logo = pygame.image.load("assets/start.png")
exit_logo = pygame.image.load("assets/exit.png")
gameover_logo = pygame.image.load("assets/gameover.png")
congrats_logo = pygame.image.load("assets/congrats.png")

button_size = (200, 80)
start_logo = pygame.transform.scale(start_logo, button_size)
exit_logo = pygame.transform.scale(exit_logo, button_size)
replay_logo = pygame.image.load("assets/replay.png")  
replay_logo = pygame.transform.scale(replay_logo, (200, 80))  



def draw_player():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player_center = (player_pos[0] + player_size / 2, player_pos[1] + player_size / 2)
    dx, dy = mouse_x - player_center[0], mouse_y - player_center[1]
    angle = math.degrees(math.atan2(dy, dx))
    rotated_player = pygame.transform.rotate(player_skin, -angle)
    rotated_rect = rotated_player.get_rect(center=player_center)
    screen.blit(rotated_player, rotated_rect.topleft)


def draw_bullets():
    for bullet in bullets:
        pygame.draw.circle(screen, RED, (int(bullet["pos"][0]), int(bullet["pos"][1])), bullet_radius)


def draw_maze():
    for wall in walls:
        pygame.draw.rect(screen, WHITE, wall)
    pygame.draw.rect(screen, GREEN, exit_rect)


def constrain_player():
    player_pos[0] = max(20, min(player_pos[0], WIDTH - player_size - 20))
    player_pos[1] = max(20, min(player_pos[1], HEIGHT - player_size - 20))


def reflect_bullet(bullet):
    bullet_rect = pygame.Rect(
        bullet["pos"][0] - bullet_radius,
        bullet["pos"][1] - bullet_radius,
        bullet_radius * 2,
        bullet_radius * 2,
    )
    for wall in walls:
        if bullet_rect.colliderect(wall):
            overlap_left = abs(bullet_rect.left - wall.right)
            overlap_right = abs(bullet_rect.right - wall.left)
            overlap_top = abs(bullet_rect.top - wall.bottom)
            overlap_bottom = abs(bullet_rect.bottom - wall.top)

            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            if min_overlap == overlap_left or min_overlap == overlap_right:
                bullet["dir"][0] = -bullet["dir"][0]
            if min_overlap == overlap_top or min_overlap == overlap_bottom:
                bullet["dir"][1] = -bullet["dir"][1]
            break


def display_end_options(screen, message_logo, replay_logo, exit_logo):
    running = True

    button_size = (200, 80)
    replay_button_rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 100, *button_size)
    exit_button_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 100, *button_size)

    while running:
        screen.fill(BLACK)

        screen.blit(
            message_logo,
            (WIDTH // 2 - message_logo.get_width() // 2, HEIGHT // 2 - message_logo.get_height() // 2 - 100),
        )

        screen.blit(replay_logo, (replay_button_rect.x, replay_button_rect.y))

        screen.blit(exit_logo, (exit_button_rect.x, exit_button_rect.y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button_rect.collidepoint(event.pos):
                    return "replay"  
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def handle_player_repulsion():
    player_velocity[0] *= 0.9
    player_velocity[1] *= 0.9
    player_pos[0] += player_velocity[0]
    player_pos[1] += player_velocity[1]
    constrain_player()

def handle_player_collision():
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    for wall in walls:
        if player_rect.colliderect(wall):  
            player_velocity[0] = 0  
            player_velocity[1] = 0 

def move_player():
    step_x = player_velocity[0]
    step_y = player_velocity[1]

    if step_x != 0:
        next_rect_x = pygame.Rect(player_pos[0] + step_x, player_pos[1], player_size, player_size)
        if not any(next_rect_x.colliderect(wall) for wall in walls):
            player_pos[0] += step_x

    if step_y != 0:
        next_rect_y = pygame.Rect(player_pos[0], player_pos[1] + step_y, player_size, player_size)
        if not any(next_rect_y.colliderect(wall) for wall in walls):
            player_pos[1] += step_y
 




def move_bullet(bullet):
    bullet["pos"][0] += bullet["dir"][0] * bullet_speed
    bullet["pos"][1] += bullet["dir"][1] * bullet_speed

    if bullet["pos"][0] < 0 or bullet["pos"][0] > WIDTH or bullet["pos"][1] < 0 or bullet["pos"][1] > HEIGHT:
        return True  
    return False


def check_bullet_collision():
    global player_health
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(
            bullet["pos"][0] - bullet_radius,
            bullet["pos"][1] - bullet_radius,
            bullet_radius * 2,
            bullet_radius * 2,
        )
        if bullet_rect.colliderect(player_rect):
            damage_sound.play()
            player_health -= 100
            bullets.remove(bullet)


def opening_screen():
    pygame.mixer.music.load(main_menu_music)
    pygame.mixer.music.play(-1)
    running = True
    while running:
        screen.fill(BLACK)
        screen.blit(game_logo, (WIDTH // 2 - game_logo.get_width() // 2, 50))
        screen.blit(start_logo, (WIDTH // 2 - start_logo.get_width() // 2, HEIGHT // 2))
        screen.blit(exit_logo, (WIDTH // 2 - exit_logo.get_width() // 2, HEIGHT // 2 + 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_button_rect = pygame.Rect(WIDTH // 2 - start_logo.get_width() // 2, HEIGHT // 2, *button_size)
                exit_button_rect = pygame.Rect(WIDTH // 2 - exit_logo.get_width() // 2, HEIGHT // 2 + 100, *button_size)
                if start_button_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return "start"
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def game_over_screen():
    pygame.mixer.music.load(gameover_music)
    pygame.mixer.music.play()

    button_size = (200, 80)
    replay_button_rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 100, *button_size)
    exit_button_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 100, *button_size)

    while True:
        screen.fill(BLACK)

        screen.blit(gameover_logo, (WIDTH // 2 - gameover_logo.get_width() // 2, HEIGHT // 2 - gameover_logo.get_height() // 2 - 100))

        screen.blit(replay_logo, (replay_button_rect.x, replay_button_rect.y))  
        screen.blit(exit_logo, (exit_button_rect.x, exit_button_rect.y))      
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button_rect.collidepoint(event.pos):  
                    reset_game()
                    return
                elif exit_button_rect.collidepoint(event.pos):  
                    pygame.quit()
                    sys.exit()


font = pygame.font.Font(None, 36)  

def draw_health():
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(health_text, (20, 20))

def congrats_screen():
    pygame.mixer.music.load(congrats_music)
    pygame.mixer.music.play()

    button_size = (200, 80)
    replay_button_rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 100, *button_size)
    exit_button_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 100, *button_size)

    while True:
        screen.fill(BLACK)

        logo_width, logo_height = congrats_logo.get_width(), congrats_logo.get_height()
        new_logo_size = (logo_width // 2, logo_height // 2)  
        resized_congrats_logo = pygame.transform.scale(congrats_logo, new_logo_size)
        screen.blit(resized_congrats_logo, (WIDTH // 2 - resized_congrats_logo.get_width() // 2, HEIGHT // 2 - resized_congrats_logo.get_height() // 2 - 100))

        screen.blit(replay_logo, (replay_button_rect.x, replay_button_rect.y))  
        screen.blit(exit_logo, (exit_button_rect.x, exit_button_rect.y))      

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_button_rect.collidepoint(event.pos):  
                    reset_game()
                    return
                elif exit_button_rect.collidepoint(event.pos):  
                    pygame.quit()
                    sys.exit()


def reset_game():
    global player_health, player_pos, player_velocity, bullets
    player_health = 100
    player_pos = [50, 50]
    player_velocity = [0, 0]
    bullets = []

def game_loop():
    global player_health, player_pos, bullets, player_velocity
    running = True
    while running:
        screen.fill(BLACK)
        draw_maze()
        draw_player()
        draw_bullets()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                shoot_sound.play()  
                mouse_x, mouse_y = pygame.mouse.get_pos()
                player_center = (player_pos[0] + player_size / 2, player_pos[1] + player_size / 2)
                dx, dy = mouse_x - player_center[0], mouse_y - player_center[1]
                distance = math.hypot(dx, dy)
                if distance != 0:
                    bullet_dx, bullet_dy = dx / distance, dy / distance
                    spawn_offset = 10
                    bullets.append({
                        "pos": [
                            player_center[0] + bullet_dx * spawn_offset,
                            player_center[1] + bullet_dy * spawn_offset,
                        ],
                        "dir": [bullet_dx, bullet_dy],
                        "immune_time": 10,  
                        "time_created": time.time(),  
                    })
                    repulsion_strength = 15
                    player_velocity[0] -= bullet_dx * repulsion_strength
                    player_velocity[1] -= bullet_dy * repulsion_strength

        for bullet in bullets[:]:
            if move_bullet(bullet):  
                bullets.remove(bullet)

            reflect_bullet(bullet)

            if time.time() - bullet["time_created"] >= 5:
                bullets.remove(bullet)

        handle_player_repulsion()
        handle_player_collision()
        check_bullet_collision()

        if player_health <= 0:
            game_over_screen()
        elif exit_rect.colliderect(pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)):
            congrats_screen()

        pygame.display.flip()
        clock.tick(60)

intro_screen()

if opening_screen() == "start":
    game_loop()

pygame.quit()
sys.exit()