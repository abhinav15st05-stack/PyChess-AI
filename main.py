"""
main.py — Chess AI Game
Fixes:
- AI move plays with smooth slide animation
- Artificial thinking delay so it feels natural
- Time control per player (5, 10, 15 min or unlimited)
"""

import pygame
import sys
import threading
import time
import math
import copy
from board import Board
from ai import ChessAI
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

# ─── Constants (Modern Premium Theme) ─────────────────────────────────────────
WINDOW_W     = 760
WINDOW_H     = 680
BOARD_SIZE   = 560
SQUARE_SIZE  = BOARD_SIZE // 8
BOARD_X      = 60
BOARD_Y      = 80
SIDEBAR_X    = BOARD_X + BOARD_SIZE + 20
SIDEBAR_W    = WINDOW_W - SIDEBAR_X - 10

# Pro Chess Board Colors
C_LIGHT      = (238, 238, 212)  
C_DARK       = (118, 150,  86)  
C_BG         = ( 22,  23,  26)  
C_PANEL      = ( 34,  36,  42)  
C_TEXT       = (240, 240, 240)
C_MUTED      = (150, 155, 165)
C_GREEN      = (118, 150,  86)
C_YELLOW     = (255, 215,   0)  
C_RED        = (235,  87,  87)  
C_BLUE       = ( 90, 130, 255)

PIECE_LABELS = {
    'King': 'K', 'Queen': 'Q', 'Rook': 'R',
    'Bishop': 'B', 'Knight': 'N', 'Pawn': 'P'
}

AI_MOVE_DONE  = pygame.USEREVENT + 1
ANIM_FPS      = 60
ANIM_DURATION = 0.35    # seconds — piece slide duration
AI_MIN_THINK  = 0.6     # seconds — minimum AI "think" time

TIME_OPTIONS  = [
    ("Unlimited", None),
    ("5 min",     5 * 60),
    ("10 min",    10 * 60),
    ("15 min",    15 * 60),
]


# ─── Menu Screen ──────────────────────────────────────────────────────────────

class MenuScreen:
    def __init__(self, screen):
        self.screen      = screen
        self.title_font  = pygame.font.SysFont("helvetica", 32, bold=True)
        self.option_font = pygame.font.SysFont("helvetica", 18, bold=True)
        self.label_font  = pygame.font.SysFont("helvetica", 14)
        self.selected_time = 1   # Default: 5 min
        self.selected_depth = 1  # Default: depth 3

        self.time_options  = TIME_OPTIONS
        self.depth_options = [("Easy (depth 2)", 2), ("Medium (depth 3)", 3), ("Hard (depth 4)", 4)]

    def draw_button(self, label, rect, selected, color=C_BLUE):
        bg = color if selected else C_PANEL
        border = color if selected else (80, 80, 80)
        pygame.draw.rect(self.screen, bg,     rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)
        
        text_color = C_BG if (selected and color == C_GREEN) else C_TEXT
        
        surf = self.option_font.render(label, True, text_color)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.screen.fill(C_BG)

            # Title
            t = self.title_font.render("Chess AI", True, C_TEXT)
            self.screen.blit(t, t.get_rect(centerx=WINDOW_W//2, top=40))
            sub = self.label_font.render("Minimax + Alpha-Beta Pruning", True, C_MUTED)
            self.screen.blit(sub, sub.get_rect(centerx=WINDOW_W//2, top=80))

            # Time control section
            tc_label = self.option_font.render("Time Control", True, C_MUTED)
            self.screen.blit(tc_label, (WINDOW_W//2 - 160, 140))

            time_rects = []
            for i, (label, _) in enumerate(self.time_options):
                r = pygame.Rect(WINDOW_W//2 - 160 + i * 82, 170, 78, 44)
                time_rects.append(r)
                self.draw_button(label, r, i == self.selected_time, C_BLUE)

            # AI difficulty section
            diff_label = self.option_font.render("AI Difficulty", True, C_MUTED)
            self.screen.blit(diff_label, (WINDOW_W//2 - 215, 240)) 
            depth_rects = []
            for i, (label, _) in enumerate(self.depth_options):
                r = pygame.Rect(WINDOW_W//2 - 215 + i * 150, 270, 140, 44)
                depth_rects.append(r)
                self.draw_button(label, r, i == self.selected_depth, C_GREEN)
           
            start_rect = pygame.Rect(WINDOW_W//2 - 100, 360, 200, 52)
            self.draw_button("Start Game", start_rect, True, C_GREEN)

            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for i, r in enumerate(time_rects):
                        if r.collidepoint(mx, my):
                            self.selected_time = i
                    for i, r in enumerate(depth_rects):
                        if r.collidepoint(mx, my):
                            self.selected_depth = i
                    if start_rect.collidepoint(mx, my):
                        _, time_limit = self.time_options[self.selected_time]
                        _, depth      = self.depth_options[self.selected_depth]
                        return time_limit, depth


# ─── Animation Helper ─────────────────────────────────────────────────────────

class MoveAnimation:
    """Handles smooth sliding animation from source to destination square."""
    def __init__(self, piece, from_pos, to_pos):
        self.piece    = piece
        self.from_pos = from_pos   # (row, col)
        self.to_pos   = to_pos
        self.progress = 0.0        # 0.0 → 1.0
        self.done     = False
        
        self.restart_btn_rect = pygame.Rect(SIDEBAR_X, BOARD_Y + 280, SIDEBAR_W, 36)
        self.resign_btn_rect  = pygame.Rect(SIDEBAR_X, BOARD_Y + 325, SIDEBAR_W, 36)
        self.restart_requested = False

    def update(self, dt):
        self.progress += dt / ANIM_DURATION
        if self.progress >= 1.0:
            self.progress = 1.0
            self.done     = True

    def get_pixel_pos(self):
        """Current pixel position of the animating piece."""
        fr, fc = self.from_pos
        tr, tc = self.to_pos
        
        t = self.progress
        t = t * t * (3 - 2 * t)
        px = BOARD_X + (fc + (tc - fc) * t) * SQUARE_SIZE + SQUARE_SIZE // 2
        py = BOARD_Y + (fr + (tr - fr) * t) * SQUARE_SIZE + SQUARE_SIZE // 2
        return int(px), int(py)


# ─── Main Game ────────────────────────────────────────────────────────────────

class ChessGame:
    def __init__(self, screen, time_limit, ai_depth):
        self.screen       = screen
        self.time_limit   = time_limit
        self.board        = Board()
        self.ai           = ChessAI(depth=ai_depth)

        self.selected     = None
        self.legal_moves  = []
        self.ai_thinking  = False
        self.ai_best_move = None
        self.game_over    = False
        self.status_msg   = "Your turn  (White)"
        self.move_count   = 0
        self.dot_count    = 0
        self.dot_timer    = 0

        # Timers
        self.white_time   = time_limit
        self.black_time   = time_limit
        self.last_tick    = time.time()
        self.active_timer = 'white'

        self.animation    = None

        # Fonts
        self.piece_font   = pygame.font.SysFont("avenir, helvetica", 28, bold=True)
        self.label_font   = pygame.font.SysFont("avenir, helvetica", 14)
        self.status_font  = pygame.font.SysFont("avenir, helvetica", 17, bold=True)
        self.info_font    = pygame.font.SysFont("avenir, helvetica", 13)
        self.timer_font   = pygame.font.SysFont("courier", 20, bold=True)
        self.big_font     = pygame.font.SysFont("avenir, helvetica", 18, bold=True)

        self.restart_btn_rect = pygame.Rect(SIDEBAR_X, BOARD_Y + 280, SIDEBAR_W, 36)
        self.resign_btn_rect  = pygame.Rect(SIDEBAR_X, BOARD_Y + 325, SIDEBAR_W, 36)
        self.restart_requested = False
        self.promoting_pos = None

    # ─── Timer ────────────────────────────────────────────────────────────────

    def update_timer(self, dt):
        if self.game_over or self.time_limit is None:
            return
        if self.active_timer == 'white' and not self.ai_thinking:
            self.white_time -= dt
            if self.white_time <= 0:
                self.white_time = 0
                self.status_msg = "Time's up! Black (AI) wins!"
                self.game_over  = True
        elif self.active_timer == 'black' and self.ai_thinking:
            self.black_time -= dt
            if self.black_time <= 0:
                self.black_time = 0
                self.status_msg = "Time's up! White (You) wins!"
                self.game_over  = True

    def fmt_time(self, secs):
        if secs is None:
            return "--:--"
        secs = max(0, int(secs))
        return f"{secs // 60:02d}:{secs % 60:02d}"

    # ─── Drawing ──────────────────────────────────────────────────────────────

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                x = BOARD_X + col * SQUARE_SIZE
                y = BOARD_Y + row * SQUARE_SIZE
                color = C_LIGHT if (row + col) % 2 == 0 else C_DARK
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

                # King in Check - Red Glow
                piece = self.board.grid[row][col]
                if isinstance(piece, King) and self.board.is_in_check(piece.color):
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    s.fill((235, 87, 87, 160)) 
                    self.screen.blit(s, (x, y))

                # Selected Square Highlight - Gold Glow
                if self.selected == (row, col):
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    s.fill((255, 215, 0, 100)) 
                    self.screen.blit(s, (x, y))

                # Legal Moves - Pro dots
                if (row, col) in self.legal_moves:
                    cx = x + SQUARE_SIZE // 2
                    cy = y + SQUARE_SIZE // 2
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    
                    if self.board.grid[row][col] is not None:
                        pygame.draw.circle(s, (0, 0, 0, 50), (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE // 2 - 2, 5)
                    else:
                        pygame.draw.circle(s, (0, 0, 0, 50), (SQUARE_SIZE//2, SQUARE_SIZE//2), 12)
                    self.screen.blit(s, (x, y))

        # Premium sleek border around the board
        pygame.draw.rect(self.screen, (10, 10, 10), (BOARD_X - 2, BOARD_Y - 2, BOARD_SIZE + 4, BOARD_SIZE + 4), 2)

    def draw_piece_at(self, piece, cx, cy):
        """Draws a premium minimalist circular badge with a drop shadow."""
        piece_name = piece.__class__.__name__
        r = SQUARE_SIZE // 2 - 12
        
        # 3D Drop Shadow
        shadow = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 60), (SQUARE_SIZE//2, SQUARE_SIZE//2 + 3), r)
        self.screen.blit(shadow, (cx - SQUARE_SIZE//2, cy - SQUARE_SIZE//2))

        # Premium Badge Colors
        fill   = (250, 250, 250) if piece.color == 'white' else (45, 45, 48)
        border = (200, 200, 200) if piece.color == 'white' else (25, 25, 25)
        text_c = (30,  30,  30)  if piece.color == 'white' else (240, 240, 240)

        pygame.draw.circle(self.screen, fill, (cx, cy), r)
        pygame.draw.circle(self.screen, border, (cx, cy), r, 2)

        label = PIECE_LABELS.get(piece_name, '?')
        lsurf = self.piece_font.render(label, True, text_c)
        self.screen.blit(lsurf, lsurf.get_rect(center=(cx, cy + 2)))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.grid[row][col]
                if piece is None:
                    continue
                
                # Skip the animating piece (drawn separately)
                if (self.animation and not self.animation.done and
                        self.animation.to_pos == (row, col)):
                    continue
                cx = BOARD_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                cy = BOARD_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
                self.draw_piece_at(piece, cx, cy)

        # Draw the animating piece on top
        if self.animation and not self.animation.done:
            cx, cy = self.animation.get_pixel_pos()
            self.draw_piece_at(self.animation.piece, cx, cy)

    def draw_labels(self):
        files = 'abcdefgh'
        for i in range(8):
            x  = BOARD_X + i * SQUARE_SIZE + SQUARE_SIZE // 2
            ls = self.label_font.render(files[i], True, C_MUTED)
            self.screen.blit(ls, ls.get_rect(centerx=x, top=BOARD_Y + BOARD_SIZE + 4))

            y2 = BOARD_Y + i * SQUARE_SIZE + SQUARE_SIZE // 2
            rs = self.label_font.render(str(8 - i), True, C_MUTED)
            self.screen.blit(rs, rs.get_rect(right=BOARD_X - 4, centery=y2))

    def draw_sidebar(self):
        sx = SIDEBAR_X

        # Black timer
        black_active = self.ai_thinking and not self.game_over
        bc = C_RED if (self.black_time is not None and self.black_time < 30) else (C_YELLOW if black_active else C_PANEL)
        brect = pygame.Rect(sx, BOARD_Y, SIDEBAR_W, 70)
        pygame.draw.rect(self.screen, bc if black_active else C_PANEL, brect, border_radius=10)
        pygame.draw.rect(self.screen, bc, brect, 2, border_radius=10)

        bl = self.label_font.render("BLACK (AI)", True, C_MUTED)
        self.screen.blit(bl, bl.get_rect(centerx=brect.centerx, top=brect.top + 8))
        bt = self.timer_font.render(self.fmt_time(self.black_time), True, C_TEXT)
        self.screen.blit(bt, bt.get_rect(centerx=brect.centerx, centery=brect.centery + 8))

        # Status / info
        mid_y = BOARD_Y + 90
        if self.ai_thinking:
            dots  = "." * (self.dot_count + 1)
            smsg  = f"Thinking{dots}"
            scolor = C_YELLOW
        else:
            smsg  = self.status_msg
            scolor = C_GREEN if not self.game_over else C_RED

        words = smsg.split()
        line, lines = "", []
        for w in words:
            test = (line + " " + w).strip()
            if self.big_font.size(test)[0] < SIDEBAR_W:
                line = test
            else:
                lines.append(line); line = w
        lines.append(line)

        for i, ln in enumerate(lines):
            s = self.big_font.render(ln, True, scolor)
            self.screen.blit(s, s.get_rect(centerx=sx + SIDEBAR_W//2, top=mid_y + i*28))

        # Info
        info_y = mid_y + len(lines) * 28 + 16
        for label, val in [
            ("Move", str(self.move_count)),
            ("Depth", str(self.ai.depth)),
            ("Nodes", str(self.ai.nodes_searched)),
        ]:
            ls = self.info_font.render(label, True, C_MUTED)
            vs = self.info_font.render(val,   True, C_TEXT)
            self.screen.blit(ls, (sx, info_y))
            self.screen.blit(vs, vs.get_rect(right=sx + SIDEBAR_W, centery=info_y + 7))
            info_y += 22

        # White timer
        white_active = not self.ai_thinking and not self.game_over
        wc = C_RED if (self.white_time is not None and self.white_time < 30) else (C_GREEN if white_active else C_PANEL)
        wrect = pygame.Rect(sx, BOARD_Y + BOARD_SIZE - 70, SIDEBAR_W, 70)
        pygame.draw.rect(self.screen, wc if white_active else C_PANEL, wrect, border_radius=10)
        pygame.draw.rect(self.screen, wc, wrect, 2, border_radius=10)

        wl = self.label_font.render("WHITE (You)", True, C_MUTED)
        self.screen.blit(wl, wl.get_rect(centerx=wrect.centerx, top=wrect.top + 8))
        wt = self.timer_font.render(self.fmt_time(self.white_time), True, C_TEXT)
        self.screen.blit(wt, wt.get_rect(centerx=wrect.centerx, centery=wrect.centery + 8))
        
        # Restart Button
        pygame.draw.rect(self.screen, C_PANEL, self.restart_btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, C_MUTED, self.restart_btn_rect, 1, border_radius=6)
        rst_surf = self.label_font.render("Restart Game", True, C_TEXT)
        self.screen.blit(rst_surf, rst_surf.get_rect(center=self.restart_btn_rect.center))

        # Resign Button
        pygame.draw.rect(self.screen, C_PANEL, self.resign_btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, C_RED, self.resign_btn_rect, 1, border_radius=6)
        rsg_surf = self.label_font.render("Resign", True, C_RED)
        self.screen.blit(rsg_surf, rsg_surf.get_rect(center=self.resign_btn_rect.center))

        hint = self.label_font.render("R = Restart  |  M = Menu", True, C_MUTED)
        self.screen.blit(hint, hint.get_rect(centerx=sx + SIDEBAR_W//2, bottom=BOARD_Y + BOARD_SIZE))

    def draw(self):
        self.screen.fill(C_BG)
        self.draw_board()
        self.draw_pieces()
        self.draw_labels()
        self.draw_sidebar()
        self.draw_promotion_menu()
        pygame.display.flip()

    def draw_promotion_menu(self):
        if not self.promoting_pos:
            return
            
        menu_w, menu_h = 240, 60
        mx = BOARD_X + (BOARD_SIZE - menu_w) // 2
        my = BOARD_Y + (BOARD_SIZE - menu_h) // 2
        
        rect = pygame.Rect(mx, my, menu_w, menu_h)
        pygame.draw.rect(self.screen, C_PANEL, rect, border_radius=8)
        pygame.draw.rect(self.screen, C_GREEN, rect, 2, border_radius=8)
        
        self.promo_rects = []
        pieces = [Queen, Rook, Bishop, Knight]
        labels = ['Q', 'R', 'B', 'N']
        
        for i, (PieceClass, lbl) in enumerate(zip(pieces, labels)):
            bx = mx + 10 + i * 55
            by = my + 10
            r = pygame.Rect(bx, by, 45, 40)
            self.promo_rects.append((r, PieceClass))
            
            mouse_pos = pygame.mouse.get_pos()
            bg_color = C_GREEN if r.collidepoint(mouse_pos) else C_BG
            
            pygame.draw.rect(self.screen, bg_color, r, border_radius=4)
            s = self.piece_font.render(lbl, True, C_TEXT)
            self.screen.blit(s, s.get_rect(center=r.center))

    # ─── Input ────────────────────────────────────────────────────────────────

    def handle_click(self, mx, my):
        # Promotion Menu Check
        if self.promoting_pos:
            if hasattr(self, 'promo_rects'):
                for rect, PieceClass in self.promo_rects:
                    if rect.collidepoint(mx, my):
                        r, c = self.promoting_pos
                        self.board.grid[r][c] = PieceClass('white')
                        self.promoting_pos = None
                        self.trigger_ai()
                        return
            return 
            
        # Sidebar Buttons Check
        if self.restart_btn_rect.collidepoint(mx, my):
            self.restart_requested = True
            return

        if self.resign_btn_rect.collidepoint(mx, my) and not self.game_over:
            self.status_msg = "You Resigned! AI wins!"
            self.game_over  = True
            return

        # Game Over and Animation Check
        if self.game_over or self.ai_thinking or (self.animation and not self.animation.done):
            return
        if self.board.current_turn != 'white':
            return

        col = (mx - BOARD_X) // SQUARE_SIZE
        row = (my - BOARD_Y) // SQUARE_SIZE

        if not (0 <= row < 8 and 0 <= col < 8):
            self.selected = None; self.legal_moves = []; return

        clicked = self.board.grid[row][col]

        if self.selected and (row, col) in self.legal_moves:
            self.execute_player_move(self.selected, (row, col))
            return

        if clicked and clicked.color == 'white':
            self.selected    = (row, col)
            self.legal_moves = self.board.get_legal_moves(row, col)
        else:
            self.selected = None; self.legal_moves = []

    def execute_player_move(self, from_pos, to_pos):
        piece = self.board.grid[from_pos[0]][from_pos[1]]
        is_pawn = isinstance(piece, Pawn)
        
        self.board.make_move(from_pos, to_pos)
        self.move_count   += 1
        self.selected      = None
        self.legal_moves   = []
        
        # Pawn Promotion Check
        if is_pawn and to_pos[0] == 0:
            self.promoting_pos = to_pos
            self.status_msg = "Choose Promotion!"
            return  
            
        self.trigger_ai()

    def trigger_ai(self):
        """Initializes AI move logic, decoupled to handle post-promotion triggers."""
        self.active_timer  = 'black'

        if self.check_game_over():
            return

        self.ai_thinking   = True
        self.ai_best_move  = None
        self.status_msg    = "Thinking"
        ai_start           = time.time()

        board_copy = copy.deepcopy(self.board)

        def ai_worker():
            move = self.ai.get_best_move(board_copy)
            elapsed = time.time() - ai_start
            remaining = AI_MIN_THINK - elapsed
            if remaining > 0:
                time.sleep(remaining)
            self.ai_best_move = move
            pygame.event.post(pygame.event.Event(AI_MOVE_DONE))

        threading.Thread(target=ai_worker, daemon=True).start()


    def handle_ai_done(self):
        self.ai_thinking  = False
        self.active_timer = 'white'

        if self.ai_best_move:
            from_pos, to_pos = self.ai_best_move
            piece = self.board.grid[from_pos[0]][from_pos[1]]
            self.animation = MoveAnimation(piece, from_pos, to_pos)
            self.board.make_move(from_pos, to_pos)
            self.move_count += 1

        if not self.check_game_over():
            self.status_msg = "Your turn"

    def check_game_over(self):
        nc = self.board.current_turn
        if self.board.is_checkmate(nc):
            winner = 'AI wins!' if nc == 'white' else 'You win!'
            self.status_msg = f"Checkmate! {winner}"
            self.game_over  = True; return True
        if self.board.is_stalemate(nc):
            self.status_msg = "Stalemate! Draw!"
            self.game_over  = True; return True
        if self.board.is_in_check(nc):
            who = "Your" if nc == 'white' else "AI"
            self.status_msg = f"Check! {who} king!"
        return False

    # ─── Main Loop ────────────────────────────────────────────────────────────

    def run(self):
        clock = pygame.time.Clock()
        print("Chess AI ready! You = White, AI = Black. R=restart, M=menu")
        self.restart_requested = False 

        while True:
            if self.restart_requested:
                return 'restart'

            dt = clock.tick(ANIM_FPS) / 1000.0

            if self.animation and not self.animation.done:
                self.animation.update(dt)

            self.update_timer(dt)

            if self.ai_thinking:
                self.dot_timer += dt
                if self.dot_timer > 0.4:
                    self.dot_count = (self.dot_count + 1) % 3
                    self.dot_timer = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(*event.pos)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return 'restart'
                    if event.key == pygame.K_m:
                        return 'menu'

                if event.type == AI_MOVE_DONE:
                    self.handle_ai_done()

            self.draw()


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Chess AI")

    time_limit, depth = MenuScreen(screen).run()

    while True:
        game   = ChessGame(screen, time_limit, depth)
        result = game.run()
        if result == 'menu':
            time_limit, depth = MenuScreen(screen).run()

if __name__ == "__main__":
    main()