import pygame
import random
from dataclasses import dataclass
from typing import List, Tuple

# Konstanten
BLOCKGROESSE = 30
SPIELFELD_BREITE = 10
SPIELFELD_HOEHE = 20
RAND = 1

# Farben
SCHWARZ = (0, 0, 0)
WEISS = (255, 255, 255)
GRAU = (128, 128, 128)
CYAN = (0, 255, 255)
GELB = (255, 255, 0)
MAGENTA = (255, 0, 255)
ROT = (255, 0, 0)
GRUEN = (0, 255, 0)
BLAU = (0, 0, 255)
ORANGE = (255, 165, 0)

@dataclass
class Tetromino:
    form: List[List[int]]
    farbe: Tuple[int, int, int]
    x: int
    y: int

class TetrisSpiel:
    def __init__(self):
        pygame.init()
        
        # Fenstergröße berechnen
        self.fenster_breite = BLOCKGROESSE * (SPIELFELD_BREITE + 6)
        self.fenster_hoehe = BLOCKGROESSE * SPIELFELD_HOEHE
        
        # Spielfenster erstellen
        self.fenster = pygame.display.set_mode((self.fenster_breite, self.fenster_hoehe))
        pygame.display.set_caption('Tetris')
        
        # Font initialisieren
        self.font = pygame.font.Font(None, 36)
        
        # Tetrominos definieren
        self.TETROMINOS = {
            'I': ([[1, 1, 1, 1]], CYAN),
            'O': ([[1, 1], [1, 1]], GELB),
            'T': ([[0, 1, 0], [1, 1, 1]], MAGENTA),
            'L': ([[0, 0, 1], [1, 1, 1]], ORANGE),
            'J': ([[1, 0, 0], [1, 1, 1]], BLAU),
            'S': ([[0, 1, 1], [1, 1, 0]], GRUEN),
            'Z': ([[1, 1, 0], [0, 1, 1]], ROT)
        }
        
        self.reset_spiel()

    def neuer_tetromino(self) -> Tetromino:
        form_name = random.choice(list(self.TETROMINOS.keys()))
        form, farbe = self.TETROMINOS[form_name]
        return Tetromino(
            form=form,
            farbe=farbe,
            x=SPIELFELD_BREITE // 2 - len(form[0]) // 2,
            y=0
        )

    def reset_spiel(self):
        self.spielfeld = [[0 for _ in range(SPIELFELD_BREITE)] for _ in range(SPIELFELD_HOEHE)]
        self.aktueller_tetromino = self.neuer_tetromino()
        self.naechster_tetromino = self.neuer_tetromino()
        self.score = 0
        self.game_over = False

    def tetromino_rotieren(self):
        alte_form = self.aktueller_tetromino.form
        # Neue Form durch Rotation erstellen
        neue_form = list(zip(*alte_form[::-1]))
        neue_form = [list(reihe) for reihe in neue_form]
        
        # Temporär die neue Form setzen und Kollision prüfen
        original_form = self.aktueller_tetromino.form
        self.aktueller_tetromino.form = neue_form
        if self.kollision_pruefen(self.aktueller_tetromino):
            self.aktueller_tetromino.form = original_form

    def kollision_pruefen(self, tetromino: Tetromino, x_offset=0, y_offset=0) -> bool:
        for y, reihe in enumerate(tetromino.form):
            for x, zelle in enumerate(reihe):
                if zelle:
                    abs_x = tetromino.x + x + x_offset
                    abs_y = tetromino.y + y + y_offset
                    
                    if (abs_x < 0 or 
                        abs_x >= SPIELFELD_BREITE or 
                        abs_y >= SPIELFELD_HOEHE or
                        (abs_y >= 0 and self.spielfeld[abs_y][abs_x])):
                        return True
        return False

    def tetromino_einfrieren(self):
        # Aktuellen Tetromino ins Spielfeld einfrieren
        for y, reihe in enumerate(self.aktueller_tetromino.form):
            for x, zelle in enumerate(reihe):
                if zelle:
                    abs_y = self.aktueller_tetromino.y + y
                    abs_x = self.aktueller_tetromino.x + x
                    if abs_y >= 0:  # Nur wenn der Block sichtbar ist
                        self.spielfeld[abs_y][abs_x] = self.aktueller_tetromino.farbe
        
        # Volle Reihen entfernen und Punkte vergeben
        self.reihen_entfernen()
        
        # Neuen Tetromino setzen
        self.aktueller_tetromino = self.naechster_tetromino
        self.naechster_tetromino = self.neuer_tetromino()
        
        # Game Over prüfen
        if self.kollision_pruefen(self.aktueller_tetromino):
            self.game_over = True

    def reihen_entfernen(self):
        volle_reihen = []
        for y in range(SPIELFELD_HOEHE):
            if all(self.spielfeld[y]):
                volle_reihen.append(y)
        
        for reihe in volle_reihen:
            del self.spielfeld[reihe]
            self.spielfeld.insert(0, [0 for _ in range(SPIELFELD_BREITE)])
            self.score += 100

    def zeichne_vorschau(self):
        vorschau_x = SPIELFELD_BREITE * BLOCKGROESSE + 30
        vorschau_y = 50
        
        # Vorschau-Text
        vorschau_text = self.font.render('Nächster:', True, WEISS)
        self.fenster.blit(vorschau_text, (vorschau_x, 10))
        
        # Nächsten Tetromino zeichnen
        for y, reihe in enumerate(self.naechster_tetromino.form):
            for x, zelle in enumerate(reihe):
                if zelle:
                    pygame.draw.rect(
                        self.fenster,
                        self.naechster_tetromino.farbe,
                        (vorschau_x + x * BLOCKGROESSE,
                         vorschau_y + y * BLOCKGROESSE,
                         BLOCKGROESSE - RAND,
                         BLOCKGROESSE - RAND)
                    )

    def zeichnen(self):
        self.fenster.fill(SCHWARZ)
        
        # Spielfeld zeichnen
        for y in range(SPIELFELD_HOEHE):
            for x in range(SPIELFELD_BREITE):
                if self.spielfeld[y][x]:
                    pygame.draw.rect(
                        self.fenster,
                        self.spielfeld[y][x],
                        (x * BLOCKGROESSE, y * BLOCKGROESSE,
                         BLOCKGROESSE - RAND, BLOCKGROESSE - RAND)
                    )
        
        # Aktuellen Tetromino zeichnen
        for y, reihe in enumerate(self.aktueller_tetromino.form):
            for x, zelle in enumerate(reihe):
                if zelle:
                    pygame.draw.rect(
                        self.fenster,
                        self.aktueller_tetromino.farbe,
                        ((self.aktueller_tetromino.x + x) * BLOCKGROESSE,
                         (self.aktueller_tetromino.y + y) * BLOCKGROESSE,
                         BLOCKGROESSE - RAND, BLOCKGROESSE - RAND)
                    )
        
        # Seitenbereich für Score und Vorschau
        sidebar_x = SPIELFELD_BREITE * BLOCKGROESSE + 20
        sidebar_width = 250  # Sidebar verbreitern
        sidebar_height = 400
        
        # Sidebar-Hintergrundfarbe ändern (z.B. hellblau)
        sidebar_background = pygame.Surface((sidebar_width, sidebar_height))
        sidebar_background.fill((173, 216, 230))  # Hellblau
        self.fenster.blit(sidebar_background, (sidebar_x, 0))
        
        # Score-Text
        score_label = self.font.render('SCORE', True, SCHWARZ)
        score_value = self.font.render(str(self.score), True, SCHWARZ)
        
        # Score positionieren
        self.fenster.blit(score_label, (sidebar_x + 10, 20))
        self.fenster.blit(score_value, (sidebar_x + 10, 60))
        
        # Abstand zwischen Score und Nächster
        self.fenster.blit(self.font.render('', True, SCHWARZ), (sidebar_x + 10, 100))  # Leerzeile für Abstand
        
        # "Nächster"-Text
        next_label = self.font.render('NÄCHSTER', True, SCHWARZ)
        self.fenster.blit(next_label, (sidebar_x + 10, 120))
        
        # Abstand zwischen Nächster und Vorschau
        self.fenster.blit(self.font.render('', True, SCHWARZ), (sidebar_x + 10, 160))  # Leerzeile für Abstand
        
        # Vorschau-Box
        vorschau_offset_x = sidebar_x + 10
        vorschau_offset_y = 180
        for y, reihe in enumerate(self.naechster_tetromino.form):
            for x, zelle in enumerate(reihe):
                if zelle:
                    pygame.draw.rect(
                        self.fenster,
                        self.naechster_tetromino.farbe,
                        (vorschau_offset_x + x * BLOCKGROESSE,
                         vorschau_offset_y + y * BLOCKGROESSE,
                         BLOCKGROESSE - RAND,
                         BLOCKGROESSE - RAND)
                    )
        
        # Rahmen um die Vorschau zeichnen
        pygame.draw.rect(self.fenster, SCHWARZ, (vorschau_offset_x - 2, vorschau_offset_y - 2, 
                                                   BLOCKGROESSE * len(self.naechster_tetromino.form[0]) + 4, 
                                                   BLOCKGROESSE * len(self.naechster_tetromino.form) + 4), 2)
        
        # Optional: Trennlinie zwischen Score und Vorschau
        pygame.draw.line(self.fenster, SCHWARZ, (sidebar_x, 110), (sidebar_x + sidebar_width, 110), 2)
        
        pygame.display.flip()

    def zeige_startbildschirm(self):
        self.fenster.fill(SCHWARZ)
        
        titel = self.font.render('TETRIS', True, WEISS)
        titel_rect = titel.get_rect(center=(self.fenster_breite/2, self.fenster_hoehe/3))
        self.fenster.blit(titel, titel_rect)
        
        start_text = self.font.render('Drücke LEERTASTE', True, WEISS)
        start_rect = start_text.get_rect(center=(self.fenster_breite/2, self.fenster_hoehe/2))
        self.fenster.blit(start_text, start_rect)
        
        pygame.display.flip()
        
        warten = True
        while warten:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        warten = False
                    elif event.key == pygame.K_ESCAPE:
                        return False
        return True

    def spiel_schleife(self):
        clock = pygame.time.Clock()
        fall_zeit = 0
        fall_geschwindigkeit = 500  # normale Fallgeschwindigkeit
        schnell_fallen_aktiviert = False  # Flag für schnelles Fallen
        schnell_fallen_dauer = 300  # Zeit in Millisekunden, nach der schnelles Fallen aktiviert wird
        schnell_fallen_timer = 0  # Timer für schnelles Fallen
        seitliche_bewegung_timer = 0  # Timer für seitliche Bewegung
        seitliche_bewegung_dauer = 100  # Zeit in Millisekunden für seitliche Bewegung (schneller)

        while not self.game_over:
            clock.tick(60)
            fall_zeit += clock.get_time()
            
            # Kontinuierliche Tasteneingaben prüfen
            keys = pygame.key.get_pressed()
            
            # Timer für seitliche Bewegung erhöhen
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                seitliche_bewegung_timer += clock.get_time()
            
            if keys[pygame.K_LEFT] and seitliche_bewegung_timer >= seitliche_bewegung_dauer:
                if not self.kollision_pruefen(self.aktueller_tetromino, x_offset=-1):
                    self.aktueller_tetromino.x -= 1
                seitliche_bewegung_timer = 0  # Timer zurücksetzen
            
            if keys[pygame.K_RIGHT] and seitliche_bewegung_timer >= seitliche_bewegung_dauer:
                if not self.kollision_pruefen(self.aktueller_tetromino, x_offset=1):
                    self.aktueller_tetromino.x += 1
                seitliche_bewegung_timer = 0  # Timer zurücksetzen
            
            if keys[pygame.K_DOWN]:
                # Timer für schnelles Fallen erhöhen
                schnell_fallen_timer += clock.get_time()
                if schnell_fallen_timer >= schnell_fallen_dauer:
                    schnell_fallen_aktiviert = True
                else:
                    schnell_fallen_aktiviert = False
                
                # Sofort nach unten bewegen, wenn schnell_fallen_aktiviert ist
                if schnell_fallen_aktiviert:
                    if not self.kollision_pruefen(self.aktueller_tetromino, y_offset=1):
                        self.aktueller_tetromino.y += 1
                        fall_zeit = 0  # Timer zurücksetzen
                else:
                    # Normales Fallen, wenn die Taste nicht lange genug gedrückt wird
                    if not self.kollision_pruefen(self.aktueller_tetromino, y_offset=1):
                        self.aktueller_tetromino.y += 1
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.tetromino_rotieren()
            
            # Normales Fallen
            if fall_zeit >= fall_geschwindigkeit:
                fall_zeit = 0
                if not self.kollision_pruefen(self.aktueller_tetromino, y_offset=1):
                    self.aktueller_tetromino.y += 1
                else:
                    self.tetromino_einfrieren()
            
            self.zeichnen()

    def hauptschleife(self):
        while True:
            if not self.zeige_startbildschirm():
                break
            
            self.spiel_schleife()
            
        pygame.quit()

if __name__ == "__main__":
    spiel = TetrisSpiel()
    spiel.hauptschleife()