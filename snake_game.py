import sys
import random
import json

import pygame
import pygame.font
from pygame.sprite import Sprite 

class SnakeHead():
    """Main class for player controlled head"""
    def __init__(self, snake_game):
        self.game = snake_game
        self.screen = self.game.screen
        self.screen_rect = self.screen.get_rect()
        self.size = self.game.snake_size
        self.color = (0, 255, 0)
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.position = [(0,0)]
        self.reset_direction()
        self.moving_right = True

    def rect_init(self):
        """Initializes some attributes during start of game loop"""
        self.grid = self.game.grid
        starting_point = int(len(self.grid) / 2)
        self.rect.center = self.grid[starting_point - 8]#completely bodged

    def reset_direction(self):
        """Resets all movement directions"""
        self.moving_up    = False
        self.moving_down  = False
        self.moving_right = False
        self.moving_left  = False

    def move(self):
        """Moves snake"""
        edge_x, edge_y = self.grid[-1]
        if self.moving_up and self.rect.top > 2*snake_game.snake_size:
            self.rect.y -= self.size
        if self.moving_down and self.rect.centery < edge_y:
            self.rect.y += self.size
        if self.moving_right and self.rect.centerx < edge_x:
            self.rect.x += self.size
        if self.moving_left and self.rect.left > 0:
            self.rect.x -= self.size
        
    def update_position(self): 
        """Creates position list to track movement"""
        p_slice = slice(0, self.game.body_count + 2)
        self.position.insert(0, self.rect.center)
        self.position = self.position[p_slice]
        pygame.draw.rect(self.screen, self.color, self.rect)

class SnakeBody(Sprite):
    """Class for the bodies of the snakes"""
    def __init__(self, snake_game, number):
        """Takes game instance and body number, creates green rect"""
        super().__init__()
        self.number = number
        self.screen = snake_game.screen
        self.screen_rect = self.screen.get_rect()
        self.size = snake_game.snake_size
        self.color = (0, 200, 0)
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, snake_game):
        """Draws to position in position list of the head"""
        self.rect.center = snake_game.snake.position[self.number + 1]
        pygame.draw.rect(self.screen, self.color, self.rect)

class Button():
    """Class of start button"""
    def __init__(self, game, msg):
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.width, self.height = 200, 50
        self.color = (0, 255, 0)
        self.txt_color = game.bg_color
        self.font = pygame.font.SysFont(None, 48)
        self.rect = pygame.Rect(0, 0 , self.width, self.height)
        self.rect.center = self.screen_rect.center
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """Turn msg to rendered image and center to button"""
        self.msg_image = self.font.render(
            msg, True, self.txt_color, self.color,
            )
        self.msg_rect = self.msg_image.get_rect()
        self.msg_rect.center = self.screen_rect.center

    def _draw_button(self):
        """Draws button and text to screen"""
        self.screen.fill(self.color, self.rect)
        self.screen.blit(self.msg_image, self.msg_rect)

class SnakeGame():
    """General game class"""
    def __init__(self):
        
        pygame.init()
        #settings
        self.snake_size = 30#multiple of 2 
        self.screen_width = 600
        self.screen_height = 450 + 2*self.snake_size
        self.bg_color = (0,0,0)
        self.game_active = False
        #creates display
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            )
        pygame.display.set_caption("Snake")
        #entity init
        self.create_grid()
        self.button = Button(self, 'Play')
        self.bodies = pygame.sprite.Group()
        #apple init
        self.apple_image = pygame.image.load("images/apple.bmp")
        self.apple_rect = self.apple_image.get_rect()
        #highscore init
        self.filename = 'high_score.json'
        with open(self.filename, 'r') as f:
            try:
                self.highscore = int(json.load(f))
            except json.decoder.JSONDecodeError:#if json is null object     
                self.highscore = 0

    def create_grid(self):
        """Creates a list of centerpoints with snake_size spacing""" 
        self.grid=[]
        sq_size = self.snake_size
        width   = self.screen_width 
        height  = self.screen_height - 2*self.snake_size#leaves scoreboard space
        n_columns = width // sq_size
        n_rows    = height // sq_size
        for n_column in range(n_columns):
            for n_row in range(n_rows):
                center_x = int(sq_size / 2) + n_column * sq_size
                center_y = int(sq_size / 2) + (n_row + 2) * sq_size
                self.grid.append((center_x, center_y))

    def reset_stats(self):
        """Used for death"""
        self.body_count = 0
        self.score = -1
        self.game_speed = 200#for incremental use 316 as a good speed
        self.apple_eaten = True
        self.game_active = True
        self.snake = SnakeHead(self)

    def update_highscore(self):
        """Dumps highscore to json"""
        with open(self.filename, 'w') as f:
            json.dump(self.highscore, f)

    def check_keydown_events(self, event):
        """Movement/quit imputs. Movement resets direction"""
        if event.key == pygame.K_UP and not self.snake.moving_down:
                self.snake.reset_direction()
                self.snake.moving_up = True
        elif event.key == pygame.K_DOWN and not self.snake.moving_up:
                self.snake.reset_direction()
                self.snake.moving_down = True
        elif event.key == pygame.K_RIGHT and not self.snake.moving_left:
                self.snake.reset_direction()
                self.snake.moving_right = True
        elif event.key == pygame.K_LEFT and not self.snake.moving_right:
                self.snake.reset_direction()
                self.snake.moving_left = True
        elif event.key == pygame.K_q:
            self.update_highscore()
            sys.exit()
        else:
            self.event_q = True

    def _check_button(self, mouse_pos):
        """Checks if mouse position collides with button"""
        if self.button.rect.collidepoint(mouse_pos):
            self.reset_stats()
            self.bodies.empty()
            self.snake.rect_init()

    def check_events(self):
        """Checks last item in event queue"""
        self.event_q = True
        #this flag is used to only process one input from the event queue, since
        #you could change direction twice during the same 'frame'allowing you to
        #turn 180 and kill yourself if you spammed buttons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.update_highscore()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.event_q:
                    self.event_q = False
                    self.check_keydown_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_button(mouse_pos)

    def check_snake_collisions(self):
        """
        If pos[0]==pos[1] the snake must have hit a wall, if pos[0] is in the 
        list of positions it crossed over itself.
        """
        position = self.snake.position
        if position[0] == position[1] or position[0] in position[1:-1]:
            self.game_active = False

    def generate_apple(self):
        """Generates random apple position not occupied by snake"""    
        s_pos = self.snake.position.copy()
        g_pos = self.grid.copy()
        for pos in s_pos:
            if pos in g_pos:
                g_pos.remove(pos)
        rand = random.randrange(len(g_pos))
        self.apple_position = g_pos[rand]
        self.apple_eaten = False
        self.score += 1
        if self.score > self.highscore:
            self.highscore = self.score
        #self.game_speed *= 0.975 uncomment this for incremental speed (meh)

    def draw_apple(self, position):
        """Blits to screen"""
        self.apple_rect.center = position
        self.screen.blit(self.apple_image, self.apple_rect)

    def add_bodies(self):
        """Adds body to group"""
        new_body = SnakeBody(self, self.body_count)
        self.bodies.add(new_body)
        self.body_count += 1

    def update_snake(self):
        """
        Snake rect moves, checks collisions, moves bodies.
        """
        self.snake.move()
        self.snake.update_position()
        self.check_snake_collisions()
        if self.snake.position[0] == self.apple_position:
            self.add_bodies()
            self.apple_eaten = True
        self.bodies.update(self)

    def update_entities(self):
        """Minor refactor"""
        self.draw_apple(self.apple_position)
        self.update_snake()

    def update_score(self, score_str, right=None, left=None):
        """Renders input score to top of the screen at x position"""
        font = pygame.font.SysFont(None, 2*self.snake_size)
        score_image = font.render(
            score_str, True, (0,100,0), self.sb_color
            )
        score_rect = score_image.get_rect()
        if right: #I know this is an EXTREMELY lazy fix
            score_rect.right = right
        else:
            score_rect.left = left
        score_rect.top = 10
        self.screen.blit(score_image, score_rect)

    def update_scoreboard(self):
        """Draws top white rect, score and highscore"""
        self.sb_color = (255,255,255)
        board_rect = pygame.Rect(
            0, 0, self.screen_width, 2*self.snake_size,
            )
        pygame.draw.rect(self.screen, self.sb_color, board_rect)
        high_left = 10
        score_str = f"Highscore: {self.highscore}"
        self.update_score(score_str, left=high_left)
        if self.game_active:
            score_right = self.screen_width - 10 
            score_str = f"Score: {self.score}"
            self.update_score(score_str, right=score_right)

    def update_screen(self):
        """Fills screen, draws apple and runs update_snake"""
        self.screen.fill(self.bg_color)
        if self.game_active == False:
            self.button._draw_button()

    def run_game(self):
        """Runs game loop"""
        while True:
            self.check_events()
            self.update_screen()
            if self.game_active:
                if self.apple_eaten:
                    self.generate_apple()
                self.update_entities()
            self.update_scoreboard()
            pygame.display.flip()
            if self.game_active:
                pygame.time.delay(int(self.game_speed))

if __name__ == "__main__":
    snake_game = SnakeGame()
    snake_game.run_game()