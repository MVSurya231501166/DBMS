import pygame
import random
import math
import sqlite3

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-Based Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Database setup
conn = sqlite3.connect('game_results.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS players
             (name TEXT PRIMARY KEY, wins INTEGER, losses INTEGER)''')
conn.commit()

class Character:
    def __init__(self, name, x, y, color, image_path):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.level = 1
        self.x = x
        self.y = y
        self.color = color
        self.width = 50
        self.height = 100
        self.animation_offset = 0
        self.is_hit = False
        self.image = pygame.image.load(image_path)  # Load the character image
        self.image = pygame.transform.scale(self.image, (self.width, self.height))  # Scale the image

    def draw(self, screen):
        # Draw character image
        screen.blit(self.image, (self.x + self.animation_offset, self.y))
        
        # Health bar
        bar_width = 100
        bar_height = 10
        outline_rect = pygame.Rect(self.x - 25 + self.animation_offset, self.y - 60, bar_width, bar_height)
        fill_rect = pygame.Rect(self.x - 25 + self.animation_offset, self.y - 60, int(self.hp / self.max_hp * bar_width), bar_height)
        pygame.draw.rect(screen, RED, outline_rect)
        pygame.draw.rect(screen, GREEN, fill_rect)

        health_text = font.render(f"{self.name} HP: {self.hp}", True, WHITE)
        level_text = font.render(f"Level {self.level}", True, YELLOW)
        screen.blit(health_text, (self.x - 20 + self.animation_offset, self.y - 100))
        screen.blit(level_text, (self.x + self.animation_offset, self.y - 130))

        if self.is_hit:
            pygame.draw.rect(screen, RED, (self.x - 5 + self.animation_offset, self.y - 5, self.width + 10, self.height + 10), 3)

    def attack_animation(self, target):
        for i in range(20):
            self.animation_offset = math.sin(i * math.pi / 10) * 20
            target.is_hit = i > 10
            screen.fill(BLACK)
            self.draw(screen)
            target.draw(screen)
            draw_buttons()
            pygame.display.flip()
            pygame.time.delay(50)
        self.animation_offset = 0
        target.is_hit = False

    def heal_animation(self, other_character):
        for i in range(20):
            self.animation_offset = math.sin(i * math.pi / 10) * 10
            screen.fill(BLACK)
            self.draw(screen)
            other_character.draw(screen)
            draw_buttons()
            pygame.draw.circle(screen, GREEN, (self.x + self.width // 2, self.y + self.height // 2), i * 2, 2)
            pygame.display.flip()
            pygame.time.delay(50)
        self.animation_offset = 0

def draw_button(screen, text, x, y, width, height, color, text_color=BLACK):
    pygame.draw.rect(screen, color, (x, y, width, height))
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def draw_buttons():
    draw_button(screen, "Attack 1", 50, 500, 200, 50, BLUE, WHITE)
    draw_button(screen, "Attack 2", 300, 500, 200, 50, RED, WHITE)
    draw_button(screen, "Heal", 550, 500, 200, 50, GREEN)

def show_message(message, color=WHITE):
    text = big_font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(1000)

def get_user_input():
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 16, 200, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BLACK)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        prompt_text = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))

        pygame.display.flip()

    return text

def update_player_record(name, won):
    c.execute("SELECT * FROM players WHERE name=?", (name,))
    player = c.fetchone()
    if player:
        if won:
            c.execute("UPDATE players SET wins = wins + 1 WHERE name=?", (name,))
        else:
            c.execute("UPDATE players SET losses = losses + 1 WHERE name=?", (name,))
    else:
        if won:
            c.execute("INSERT INTO players VALUES (?, 1, 0)", (name,))
        else:
            c.execute("INSERT INTO players VALUES (?, 0, 1)", (name,))
    conn.commit()

def show_player_stats(name):
    c.execute("SELECT * FROM players WHERE name=?", (name,))
    player = c.fetchone()
    if player:
        stats_text = f"Player: {player[0]} | Wins: {player[1]} | Losses: {player[2]}"
    else:
        stats_text = f"New player: {name}"
   
    text = font.render(stats_text, True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, 30))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(3000)
# ... (previous initializations remain the same)

def draw_button(screen, text, x, y, width, height, color, text_color=BLACK):
    pygame.draw.rect(screen, color, (x, y, width, height))
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)
    return pygame.Rect(x, y, width, height)  # Return the button rect for click detection

def show_main_menu(player_name):
    screen.fill(BLACK)
    title = big_font.render(f"Welcome, {player_name}!", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    play_button = draw_button(screen, "Play", WIDTH // 2 - 100, 250, 200, 50, GREEN, WHITE)
    leaderboard_button = draw_button(screen, "Leaderboard", WIDTH // 2 - 100, 320, 200, 50, BLUE, WHITE)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return "play"
                elif leaderboard_button.collidepoint(event.pos):
                    return "leaderboard"

def show_leaderboard():
    screen.fill(BLACK)
    title = big_font.render("Leaderboard", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    c.execute("SELECT name, wins, losses FROM players ORDER BY CAST(wins AS FLOAT) / (wins + losses) DESC LIMIT 10")
    players = c.fetchall()

    y_offset = 120
    for i, player in enumerate(players, 1):
        name, wins, losses = player
        total_games = wins + losses
        win_percentage = (wins / total_games) * 100 if total_games > 0 else 0
        player_text = f"{i}. {name}: {win_percentage:.2f}% ({wins}/{total_games})"
        text_surface = font.render(player_text, True, WHITE)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))
        y_offset += 40

    back_button = draw_button(screen, "Back", WIDTH // 2 - 100, 500, 200, 50, RED, WHITE)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return "back"

def main():
    player_name = get_user_input()
    if not player_name:
        return

    while True:
        action = show_main_menu(player_name)

        if action == "quit":
            break
        elif action == "play":
            play_game(player_name)
        elif action == "leaderboard":
            if show_leaderboard() == "quit":
                break

    pygame.quit()
    conn.close()

def play_game(player_name):
    player = Character(player_name, 100, 400, BLUE, 'player.png')
    enemy = Character("Enemy", 650, 400, RED, 'enemy.png')
   
    clock = pygame.time.Clock()
    player_turn = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                mouse_pos = pygame.mouse.get_pos()
                if 50 <= mouse_pos[0] <= 250 and 500 <= mouse_pos[1] <= 550:
                    damage = 20
                    enemy.hp -= damage
                    player.attack_animation(enemy)
                    show_message(f"Player dealt {damage} damage!")
                    player_turn = False
                elif 300 <= mouse_pos[0] <= 500 and 500 <= mouse_pos[1] <= 550:
                    damage = random.randint(1, 60)
                    enemy.hp -= damage
                    player.attack_animation(enemy)
                    show_message(f"Player dealt {damage} damage!")
                    player_turn = False
                elif 550 <= mouse_pos[0] <= 750 and 500 <= mouse_pos[1] <= 550:
                    heal = random.randint(10, 30)
                    player.hp = min(player.max_hp, player.hp + heal)
                    player.heal_animation(enemy)
                    show_message(f"Player healed {heal} HP!")
                    player_turn = False

        if not player_turn:
            enemy_action = random.choice(["attack1", "attack2", "heal"])
            if enemy_action == "attack1":
                damage = 20
                player.hp -= damage
                enemy.attack_animation(player)
                show_message(f"Enemy dealt {damage} damage!")
            elif enemy_action == "attack2":
                damage = random.randint(1, 60)
                player.hp -= damage
                enemy.attack_animation(player)
                show_message(f"Enemy dealt {damage} damage!")
            else:
                heal = random.randint(10, 30)
                enemy.hp = min(enemy.max_hp, enemy.hp + heal)
                enemy.heal_animation(player)
                show_message(f"Enemy healed {heal} HP!")
            player_turn = True

        screen.fill(BLACK)
        player.draw(screen)
        enemy.draw(screen)
        draw_buttons()

        pygame.display.flip()
        clock.tick(60)

        if player.hp <= 0 or enemy.hp <= 0:
            winner = player_name if enemy.hp <= 0 else "Enemy"
            show_message(f"{winner} wins!", GREEN if winner == player_name else RED)
            update_player_record(player_name, winner == player_name)
            running = False

    pygame.time.delay(2000)  # Show the winner message for 2 seconds before returning to the main menu

if __name__ == "__main__":
    main()

'''def main():
    player_name = get_user_input()
    if not player_name:
        return

    show_player_stats(player_name)

    player = Character(player_name, 100, 400, BLUE, 'player.png')
    enemy = Character("Enemy", 650, 400, RED, 'enemy.png')
   
    clock = pygame.time.Clock()
    player_turn = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                mouse_pos = pygame.mouse.get_pos()
                if 50 <= mouse_pos[0] <= 250 and 500 <= mouse_pos[1] <= 550:
                    damage = 20
                    enemy.hp -= damage
                    player.attack_animation(enemy)
                    show_message(f"Player dealt {damage} damage!")
                    player_turn = False
                elif 300 <= mouse_pos[0] <= 500 and 500 <= mouse_pos[1] <= 550:
                    damage = random.randint(1, 60)
                    enemy.hp -= damage
                    player.attack_animation(enemy)
                    show_message(f"Player dealt {damage} damage!")
                    player_turn = False
                elif 550 <= mouse_pos[0] <= 750 and 500 <= mouse_pos[1] <= 550:
                    heal = random.randint(10, 30)
                    player.hp = min(player.max_hp, player.hp + heal)
                    player.heal_animation(enemy)
                    show_message(f"Player healed {heal} HP!")
                    player_turn = False

        if not player_turn:
            enemy_action = random.choice(["attack1", "attack2", "heal"])
            if enemy_action == "attack1":
                damage = 20
                player.hp -= damage
                enemy.attack_animation(player)
                show_message(f"Enemy dealt {damage} damage!")
            elif enemy_action == "attack2":
                damage = random.randint(1, 60)
                player.hp -= damage
                enemy.attack_animation(player)
                show_message(f"Enemy dealt {damage} damage!")
            else:
                heal = random.randint(10, 30)
                enemy.hp = min(enemy.max_hp, enemy.hp + heal)
                enemy.heal_animation(player)
                show_message(f"Enemy healed {heal} HP!")
            player_turn = True

        screen.fill(BLACK)
        player.draw(screen)
        enemy.draw(screen)
        draw_buttons()

        pygame.display.flip()
        clock.tick(60)

        if player.hp == 0 or enemy.hp == 0:
            winner = player_name if enemy.hp == 0 else "Enemy"
            show_message(f"{winner} wins!", GREEN if winner == player_name else RED)
            update_player_record(player_name, winner == player_name)
            show_player_stats(player_name)
            running = False

    pygame.quit()
    conn.close()

if __name__ == "__main__":
    main()'''
