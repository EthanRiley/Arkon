def alchol_effect(self, game):
    pygame.transform.rotate(player.game.window, 360)

def hope_effect(self, game): 
    game.window.get_rect().move(0, 5)
    time.sleep(0.25)
    game.window.get_rect().move(0, -5)

def mysterious_effect(self, game):
    fun = os.path.join("data", "fun") 
    temmie = get_image(os.path.join(fun, "temmie.png"))
    temmie_sound = pygame.mixer.Sound(os.path.join(fun, "temmie.ogg"))
    for sprite in game.sprites.sprites:
        sprite.image = temmie
    game.window.blit(temmie)
    pygame.transform.rotate(player.game.window, 360*4000)
