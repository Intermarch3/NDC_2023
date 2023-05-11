import pyxel

class Jeu:
    def __init__(self, Map, Player):
        """
        initialise les variable de la class Jeu

        Args:
            Map (class Map)
            Player (class Player)
        """
        pyxel.init(128, 128, title="NDC 2023")
        pyxel.load("2.pyxres")
        self.map = Map
        self.player = Player
        pyxel.run(self.update, self.draw)
    
    
    def update(self):
        """
        met a jour la partie
        """
        self.map.update(self.player)
        self.player.update(self.map)
    
    
    def draw(self):
        """
        affiche la partie
        """
        pyxel.cls(0)
        self.map.draw(self.player)
        self.player.draw()



class Map:
    def __init__(self):
        """
        initialise la map
        """
        self.x = 0
        self.y = 160
        self.etage_max = 0
    
    
    def TP (self,player):
        """
        gere l'affichage de la map quand on monte et descend

        Args:
            player (class Player)
        """
        if player.y < 0 and player.dy < 0:
            self.y += -16
            player.y = 120
            self.etage_max += 1
        if player.y > 128 and player.dy > 0:
            self.y += 16
            player.y = 0
            self.etage_max -= 1
    
    
    def update(self,player):
        self.TP(player)
    
    
    def draw(self, player):
        """
        affiche la map et les textes
        """
        if self.y == 5:
            pyxel.text(110 // 2, 128 // 2, "Vous avez finit le jeu !!!", 7)
        pyxel.bltm(0, 0, 0, self.x * 8, self.y * 8, 128, 128, 2)
        pyxel.text(0, 1, "jumps : " + str(int(player.number_of_jump)), 7)
        pyxel.text(84, 1, "Etage :" + str(self.etage_max), 7)



class Player:
    def __init__(self):
        """
        initialise les variable du joueur
        """
        self.x = 128 // 2
        self.y = 128 // 2
        self.dx = 0
        self.dy = 0
        self.gravity = 0.4
        self.ice_slide_coef = 0.075
        self.speed = 0
        self.jump_force = 4
        self.on_floor = False
        self.sprite = [24, 16]
        self.sprite_saut = [56, 16]
        self.jump_state = 0
        self.on_floor = False
        self.in_jump = True
        #liste des bloc de sol, plafond et mur
        self.floor_block = [(0, 1), (1, 1), (2, 1), (0, 5), (1, 5), (3, 5), (0, 6), (2, 5), (4, 5), (5, 5), (6, 5), (5, 6), (6, 6), (7, 6), (9, 6),(8,5),(9,5),(10,5)]
        self.sealing_block = [(0, 3), (1, 3), (2, 3), (0, 5), (1, 5), (2, 5), (3, 5), (0, 8), (4, 5), (5, 5), (6, 5), (5, 8), (6, 8), (7, 8), (9, 6), (8,5),(10,5)]
        self.side_block = [(0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (0, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 7), (7, 8), (7, 9), (9, 6),(8,5),(9,5),(10,5)]
        self.can_TP = True
        self.on_ice = False
        self.number_of_jump = 0
    
    
    def collision(self,map):
        """
        gere les collisions du joueur

        Args:
            map (class Map):
        """
        if self.on_floor == False :
            #bas
            for i in self.floor_block:
                for j in range(2):
                    if pyxel.tilemap(0).pget(self.x / 8 + map.x, self.y // 8 + 1 + map.y) == i:
                        if pyxel.tilemap(0).pget(self.x / 8 + map.x, self.y // 8 + 1 + map.y) in [(5, 6), (6, 6), (7, 6), (5, 7), (6, 7), (7, 7), (5, 8), (6, 8), (7, 8)]:
                            self.on_ice = True
                        else:
                            self.on_ice = False
                        self.on_floor = True
                        self.y = self.y // 8 * 8
            #haut
            for i in self.sealing_block:
                if pyxel.tilemap(0).pget(self.x / 8 + map.x, (self.y - 2) // 8 + map.y) == i:
                    self.dy = 1
            #gauche et droite
            if self.dx > 0:
                dir = 1
            else:
                dir = -1
            for i in self.side_block:
                if pyxel.tilemap(0).pget(self.x // 8 + dir + map.x, self.y // 8 + map.y) == i:
                    self.dx = -self.dx

    def tp(self):
        """
        gere quand le joueur monte ou descend d'etage dans la map
        """
        if self.on_floor == True:
            self.can_TP = True
        if self.x + 8 > 128 and self.can_TP == True:
            self.x = 0
            self.can_TP = False
        elif self.x < 0:
            self.x = 120
            self.can_TP = False 
    
    
    def update(self,map):
        """
        actualise le joueur

        Args:
            map (class Map)
        """
        #gravite
        if self.on_floor == False:
            self.dy = min(self.dy + self.gravity, 8)
        else:
            if self.on_ice:
                self.dx = max(abs(self.dx) - self.ice_slide_coef, 0) * self.dir
                self.on_floor = False
                self.on_ice = False
            else:
                self.dx = 0
            self.dy = 0
        #ajout force
        self.y += self.dy
        self.x += self.dx
        self.collision(map)
        #gestion du saut
        if pyxel.btn(pyxel.KEY_SPACE):
            if self.jump_state == 1:
                self.jump_force += 0.25
            elif self.jump_state == 0:
                self.jump_state += 1
                self.jump_force = 1
        else:
            if self.jump_state == 1:
                if self.on_floor:
                    if pyxel.btn(pyxel.KEY_RIGHT):
                        self.dir = 1
                    elif pyxel.btn(pyxel.KEY_LEFT):
                        self.dir = -1
                    else:
                        self.dir = 0
                    self.dy = min(self.jump_force, 8) * -1
                    self.jump_state = 0
                    self.on_floor = False
                    self.dx += 1 * self.dir
                    self.number_of_jump += 1
        self.tp()
    
    
    def draw(self):
        """
        affiche le joueur
        """
        if self.on_floor:
            sprite = self.sprite
            if self.jump_state == 1:
                pyxel.rect(self.x - 1, self.y - 2, min(int(self.jump_force), 8), 1, 6)
        else:
            sprite = self.sprite_saut
        pyxel.blt(self.x, self.y, 0, sprite[0], sprite[1], 8, 8, 2)


#demarre la partie
Jeu(Map(), Player())