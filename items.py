def alchol_effect(self):
    pygame.transform.rotate(this.window, 360)

def hope_effect(self): 
    this.window.get_rect().move(0, 5)
    time.sleep(0.25)
    this.window.get_rect().move(0, -5)

def mysterious_effect(self):
    fun = os.path.join("data", "fun") 
    temmie = get_image(os.path.join(fun, "temmie.png"))
    #temmie_sound = pygame.mixer.Sound(os.path.join(fun, "temmie.ogg"))
    for sprite in this.sprites.sprites:
        sprite.image = temmie
    this.window.blit(temmie)
    pygame.transform.rotate(this.window, 360*4000)
