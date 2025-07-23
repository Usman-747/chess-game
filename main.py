import pygame
import chess
import sys  # Import sys to use sys.exit()

# Initialize
pygame.init()
WIDTH, HEIGHT = 640, 640
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Load pieces image
PIECES = {}
for color in ['w', 'b']:
    for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
        img = pygame.image.load(f'assets/pieces/{color}{piece}.png')
        PIECES[color + piece] = pygame.transform.scale(img, (80, 80))

# Colors
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)

# Highlight colors
SELECTED_COLOR = (246, 246, 105)
MOVE_COLOR = (106, 246, 105)

# Board setup
board = chess.Board()  # White always moves first by default
SQUARE_SIZE = WIDTH // 8  # Fixed variable name

def draw_board(win):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(win, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def highlight_squares(win, selected_square, moves):
    if selected_square is not None:
        col = chess.square_file(selected_square)
        row = 7 - chess.square_rank(selected_square)
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(120)
        s.fill(SELECTED_COLOR)
        win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    for move in moves:
        to_square = move.to_square
        col = chess.square_file(to_square)
        row = 7 - chess.square_rank(to_square)
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(120)
        s.fill(MOVE_COLOR)
        win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def draw_pieces(win, board):       
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            key = ('w' if piece.color else 'b') + piece.symbol().lower()
            win.blit(PIECES[key], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def get_timer_settings_gui(win):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    input_active = False
    timer_text = ''
    use_timer = None
    clock = pygame.time.Clock()
    while use_timer is None:
        win.fill((200, 200, 200))
        title = font.render("Chess Game Setup", True, (0,0,0))
        win.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        prompt = small_font.render("Play with timer?", True, (0,0,0))
        win.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 180))
        yes_rect = pygame.Rect(WIDTH//2 - 120, 240, 100, 50)
        no_rect = pygame.Rect(WIDTH//2 + 20, 240, 100, 50)
        pygame.draw.rect(win, (100,200,100), yes_rect)
        pygame.draw.rect(win, (200,100,100), no_rect)
        yes_text = small_font.render("Yes", True, (0,0,0))
        no_text = small_font.render("No", True, (0,0,0))
        win.blit(yes_text, (yes_rect.x + 20, yes_rect.y + 10))
        win.blit(no_text, (no_rect.x + 20, no_rect.y + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_rect.collidepoint(event.pos):
                    use_timer = True
                elif no_rect.collidepoint(event.pos):
                    use_timer = False
        clock.tick(30)
    timer_seconds = None
    if use_timer:
        input_active = True
        while timer_seconds is None:
            win.fill((200, 200, 200))
            title = font.render("Set Timer (minutes)", True, (0,0,0))
            win.blit(title, (WIDTH//2 - title.get_width()//2, 80))
            box_rect = pygame.Rect(WIDTH//2 - 60, 180, 120, 50)
            pygame.draw.rect(win, (255,255,255), box_rect, 0)
            pygame.draw.rect(win, (0,0,0), box_rect, 2)
            input_text = small_font.render(timer_text or "5", True, (0,0,0))
            win.blit(input_text, (box_rect.x + 10, box_rect.y + 10))
            info = small_font.render("Press Enter to confirm", True, (0,0,0))
            win.blit(info, (WIDTH//2 - info.get_width()//2, 250))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            mins = int(timer_text) if timer_text else 5
                            timer_seconds = mins * 60
                        except Exception:
                            timer_seconds = 5 * 60
                    elif event.key == pygame.K_BACKSPACE:
                        timer_text = timer_text[:-1]
                    elif event.unicode.isdigit():
                        timer_text += event.unicode
            clock.tick(30)
    return use_timer, timer_seconds

def format_time(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02}:{s:02}"

def draw_timers(win, white_time, black_time):
    font = pygame.font.SysFont(None, 36)
    white_text = font.render(f"White: {format_time(white_time)}", True, (0,0,0))
    black_text = font.render(f"Black: {format_time(black_time)}", True, (0,0,0))
    win.blit(white_text, (10, 10))
    win.blit(black_text, (10, HEIGHT - 40))

def promotion_dialog(win, color):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    options = [('q', 'Queen'), ('r', 'Rook'), ('b', 'Bishop'), ('n', 'Knight')]
    rects = []
    for i, (key, name) in enumerate(options):
        rects.append(pygame.Rect(WIDTH//2 - 160 + i*90, HEIGHT//2 - 40, 80, 80))
    while True:
        win.fill((220,220,220))
        title = font.render("Pawn Promotion", True, (0,0,0))
        win.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for i, (key, name) in enumerate(options):
            pygame.draw.rect(win, (240,217,181) if i%2==0 else (181,136,99), rects[i])
            label = small_font.render(name, True, (0,0,0))
            win.blit(label, (rects[i].x + 5, rects[i].y + 25))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        return options[i][0]
        pygame.time.Clock().tick(30)

def main():
    use_timer, timer_seconds = get_timer_settings_gui(WIN)
    run = True
    clock = pygame.time.Clock()
    selected_square = None
    possible_moves = []
    white_time = timer_seconds if use_timer else None
    black_time = timer_seconds if use_timer else None
    last_tick = pygame.time.get_ticks()

    winner = None
    reason = None
    while run:
        draw_board(WIN)
        highlight_squares(WIN, selected_square, possible_moves)
        draw_pieces(WIN, board)
        if use_timer:
            draw_timers(WIN, white_time, black_time)
        pygame.display.flip()
        dt = clock.tick(60)

        if use_timer and not board.is_game_over():
            now = pygame.time.get_ticks()
            elapsed = (now - last_tick) / 1000.0
            last_tick = now
            # Only decrement the timer for the player whose turn it is
            if board.turn:  # True for White's turn
                white_time -= elapsed
                if white_time <= 0:
                    winner = "Black"
                    reason = "White ran out of time!"
                    run = False
            else:  # False for Black's turn
                black_time -= elapsed
                if black_time <= 0:
                    winner = "White"
                    reason = "Black ran out of time!"
                    run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = 7 - (y // SQUARE_SIZE)
                clicked_square = chess.square(col, row)

                if selected_square is None:
                    piece = board.piece_at(clicked_square)
                    if piece and piece.color == board.turn:
                        selected_square = clicked_square
                        possible_moves = [move for move in board.legal_moves if move.from_square == selected_square]
                else:
                    move = chess.Move(selected_square, clicked_square)
                    # Check for pawn promotion
                    piece = board.piece_at(selected_square)
                    is_pawn = piece and piece.piece_type == chess.PAWN
                    last_rank = (board.turn and chess.square_rank(clicked_square) == 7) or (not board.turn and chess.square_rank(clicked_square) == 0)
                    if is_pawn and last_rank:
                        promo = promotion_dialog(WIN, board.turn)
                        promo_map = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
                        move = chess.Move(selected_square, clicked_square, promo_map[promo])
                        if move in board.legal_moves:
                            board.push(move)
                    else:
                        if move in board.legal_moves:
                            board.push(move)
                    selected_square = None
                    possible_moves = []
        # Check for checkmate/stalemate
        if board.is_game_over():
            result = board.result()
            if board.is_checkmate():
                winner = "White" if board.turn == chess.BLACK else "Black"
                reason = "Checkmate!"
            elif board.is_stalemate():
                winner = None
                reason = "Stalemate!"
            elif board.is_insufficient_material():
                winner = None
                reason = "Draw by insufficient material!"
            elif board.is_seventyfive_moves():
                winner = None
                reason = "Draw by 75-move rule!"
            elif board.is_fivefold_repetition():
                winner = None
                reason = "Draw by fivefold repetition!"
            else:
                winner = None
                reason = "Draw!"
            run = False

    # Show winner message box
    font = pygame.font.SysFont(None, 64)
    small_font = pygame.font.SysFont(None, 36)
    WIN.fill((220,220,220))
    if winner:
        msg = f"{winner} wins!"
    else:
        msg = "Draw!"
    msg_text = font.render(msg, True, (0,0,0))
    WIN.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, HEIGHT//2 - 80))
    if reason:
        reason_text = small_font.render(reason, True, (0,0,0))
        WIN.blit(reason_text, (WIDTH//2 - reason_text.get_width()//2, HEIGHT//2))
    info_text = small_font.render("Press any key or close window to exit", True, (0,0,0))
    WIN.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT//2 + 60))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    pygame.quit()
    sys.exit()  # Exit the program

if __name__ == "__main__":
    main()