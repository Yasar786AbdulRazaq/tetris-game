import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
COLS, ROWS = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
COLORS = [(0, 255, 255), (255, 165, 0), (0, 255, 0),
          (255, 0, 0), (128, 0, 128), (255, 255, 0), (0, 0, 255)]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]


def rotate(shape):
    return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for i in range(ROWS):
        for j in range(COLS):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotated(self):
        return rotate(self.shape)


def draw_grid(surface, grid):
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    for i in range(ROWS):
        pygame.draw.line(surface, GREY, (0, i * BLOCK_SIZE), (WIDTH, i * BLOCK_SIZE))
    for j in range(COLS):
        pygame.draw.line(surface, GREY, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, HEIGHT))


def valid_space(shape, grid, offset):
    off_x, off_y = offset
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if i + off_y >= len(grid) or j + off_x >= len(grid[0]) or j + off_x < 0 or grid[i + off_y][j + off_x] != BLACK:
                    return False
    return True


def clear_rows(grid, locked):
    cleared = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            cleared += 1
            index = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if cleared > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < index:
                new_key = (x, y + cleared)
                locked[new_key] = locked.pop(key)
    return cleared


def draw_window(surface, grid, score=0, next_shape=None):
    surface.fill(BLACK)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', True, WHITE)
    surface.blit(label, (10, 10))

    if next_shape:
        font = pygame.font.SysFont('comicsans', 24)
        label = font.render('Next:', True, WHITE)
        surface.blit(label, (WIDTH - 100, 10))
        for i, row in enumerate(next_shape.shape):
            for j, val in enumerate(row):
                if val:
                    pygame.draw.rect(surface, next_shape.color,
                                     (WIDTH - 100 + j * BLOCK_SIZE, 40 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    draw_grid(surface, grid)
    pygame.display.update()


def draw_start_screen(win):
    win.fill(BLACK)
    font = pygame.font.SysFont('comicsans', 48)
    label = font.render("Press Any Key to Start", True, WHITE)
    win.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height() // 2))
    pygame.display.update()
    wait_for_key()


def draw_game_over(win, score):
    win.fill(BLACK)
    font = pygame.font.SysFont('comicsans', 48)
    label = font.render("Game Over", True, WHITE)
    win.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - label.get_height()))
    font2 = pygame.font.SysFont('comicsans', 32)
    label2 = font2.render(f"Score: {score}", True, WHITE)
    win.blit(label2, (WIDTH // 2 - label2.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.update()
    pygame.time.wait(2000)


def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                return


def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = Piece(COLS // 2 - 2, 0, random.choice(SHAPES))
    next_piece = Piece(COLS // 2 - 2, 0, random.choice(SHAPES))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.4
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                current_piece.y -= 1
                for i, row in enumerate(current_piece.shape):
                    for j, cell in enumerate(row):
                        if cell:
                            locked_positions[(current_piece.x + j, current_piece.y + i)] = current_piece.color
                current_piece = next_piece
                next_piece = Piece(COLS // 2 - 2, 0, random.choice(SHAPES))
                score += clear_rows(grid, locked_positions) * 10

                if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                    draw_game_over(win, score)
                    run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.shape = current_piece.rotated()
                    if not valid_space(current_piece.shape, grid, (current_piece.x, current_piece.y)):
                        current_piece.shape = rotate(rotate(rotate(current_piece.shape)))

        for i, row in enumerate(current_piece.shape):
            for j, val in enumerate(row):
                if val:
                    grid[current_piece.y + i][current_piece.x + j] = current_piece.color

        draw_window(win, grid, score, next_piece)


# Start Game
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris - Built by Yasar")
draw_start_screen(win)
main(win)
pygame.quit()
