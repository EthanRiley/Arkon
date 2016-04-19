import game_data, game_objects, threading, random, time, collections, sys

#(0, 0) is top left corner in pygame.

this = sys.modules[__name__]

this.data = game_data.game_data("data")
this.sprites = pygame.sprite.LayeredDirty()
this.battle_sprites = pygame.sprite.LayeredDirty()
this.window = pygame.display.setmode([680, 480])
this.background_music = pygame.mixer.channel(0)

def set_background(name):
    this.window.blit(self.data.backgrounds.get_data(name))
    self.background_music.play(self.data.sounds.get_data(name))

position = collections.namedtuple("position", ['x', 'y'])

class sprite(pygame.sprite.DirtySprite):

    def __init__(self, imagename, pos, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.sounds = [] 

        if 'sounds' in sorted(kwargs.keys()):
            self.sounds = kwargs['sounds']
            kwargs.pop('sounds')


        self._imagename = imagename

        self.image = this.data.sprites.get_data(self._imagename)
        self.rect = self.image.get_rect()

        self.rect.x = pos.x
        self.rect.y = pos.y
        
        self.sounds = this.data.sounds.get_data_dict(self.sounds)
        if 'battle' in sorted(kwargs.keys()):
            if kwargs['battle']:
                this.battle_sprites.add(self)
            else:
                this.sprites.add(self)
        else:
            this.sprites.add(self)

class moveable(sprite):
    def __init__(self, imagename, pos, **kwargs):
        sounds = ["collide_beep"]
        if 'sounds' in sorted(kwargs.keys()):
            sounds += kwargs['sounds']

        sprite.__init__(self, imagename, pos, sounds = sounds)
        self.__frame = 0

        directions = [
                "right",
                "forward",
                "backward"
        ]

        self.animation = {}
        for direction in directions:
            self.animation[direction] = this.data.get_data_array(self._imagename
                    + "_anim_" + direction + "_\d")

    def facing(self, direction):
        self.facing = direction

    def move(self, dx, dy):
        rect = self.get_rect()
        for sprite in this.sprites.sprites():
            if sprite != self:
                rect1 = sprite.get_rect()
                if rect1.left <= rect.right + dx & rect1.top >= rect.bottom + dy:
                    if rect1.right >= rect.left + dx & rect1.bottom <= rect.top + dy:
                        self.sounds["collide_beep"].play()
                        self.moving = False
                        return False
        self.rect.move_ip(dx, dy)
        self.moving = True
        return True

    def update(self, *args):
        if moving:
            if self.facing == "right" | self.facing == "left":
                self.image.blit(self.animation["right"][self.__frame])
                if self.facing == "left":
                    pygame.transform.flip(self.image, True, False)

            else:
                 self.image.blit(self.animation[self.facing][self.__frame])

            self.dirty = 1
            self.__frame += 1
            self.__frame = self.__frame%len(self.animation[direction])
            self.moving = False


this.fonts = game_data.font_data(os.path.join(data_dir, "fonts"))
class basic_text_box(object):

    def __init__(self, pos, data_dir):
        self.border = game_data.sprite("textbox_border", pos)
        rect = self.border.get_rect()
        self.text_box = game_data.sprite(self, "textbox", (pos.x - 6, pos.y - 6))
        self.text_box.sounds.append("activate_beep")

    def set_pos(self, pos):
        self.border.rect.x = pos.x
        self.border.rect.y = pos.y
        self.text_box.rect.x = pos.x - 6
        self.text_box.rect.y = pos.y - 6

    def word_wrap(self, text, font_name, font_size):
        font = this.font.get_data(font_name)
        textbox_x = self.text_box.get_rect().x
        if textbox_x < font.get_rect(text,
                size = font_size).x:
            output = ""
            for line in text.split('\n'):
                if textbox_x < font.get_rect(line, size = font_size):
                    lineoutput = ""
                    for word in text.split(' '):
                        if font.get_rect(output + ' ' + word, size = font_size).x > textbox_x:
                            lineoutput += '\n'
                        lineoutput += ' ' + word  
                    lineoutput.replace(' ', '', 1)
                    output += lineoutput
                else:
                    output += line
        else:
            return text

    def page_wrap(self, text, font_name, font_size):
        font = this.fonts.get_data(font_name)
        y = self.textbox.get_rect().y
        page_text = ""
        pages = []
        for line in text.split('\n'):
            if y + font.get_rect(line,
                    size=font_size).y < y:
                page_text += '\n' + line
            else:
                pages.append(page_text)
                page_text = line
        return pages

    def draw(self, surface):
        if len(self.text_to_render) != 0 | self.visible:
          surface.blit(self.text_box.image)
          surface.blit(self.border.image)
          self.draw_func(self, surface)

    def show(self):
        self.visible = True

    def hide(self):
        self.text_box.sounds["activate_beep"].play()
        self.visible = False

class text_box(basic_text_box):

    def __init__(self, pos, data_dir):
        basic_text_box.__init__(self, pos, data_dir)
        self.text_to_render = collections.deque()

    def next_page(self):
        self.txt_data = self.text_to_render.pop()
        self.text_box.sounds["activate_beep"].play()

    def draw_func(self, surface):
          this.fonts.get_data(self.txt_data.font_name).render_to(self.text_box,
                  (0, 0), self.txt_data.text, size = self.txt_data.font_size)

    def say(self, text, **kwargs):
        font = None
        if 'font' not in sorted(kwargs.keys()):
            font = this.default_font
        else:
            font = kwargs['font']

        text = self.word_wrap(text, font.name, font.size)
        for page in self.page_wrap(text, font.name, font.size):
            self.text_to_render.append(text_data(page, font.size, font.name))
        next_page()

class text_menu(basic_text_box):

    def render(self):
        self.text = ""
        self.render_text = []
        for item_name in sorted(self.items.keys()):
            self.text += "    " + item_name + self.end_formatting
        if self.end_formatting != '\n':
            self.text = self.word_wrap(text, self.font.name, self.font.size)
        self.render_text = self.page_wrap(self.text, self.font.name, self.font.size)

    def __deselect(self, item_name):
        self.text[self.render_text.find(item_name) - 2] = ' '
        self.selected = None

    def select(self, index):
        self.text_box.sounds["select_beep"].play()

        selected = sorted(self.items.keys)[index]
        if self.selected != None & index != self.selected:
            self.__deselect(selected)

        self.text[self.text.find(selected) - 2] = '>'
        self.selected = item_name
        self.page_number = int(self.text.find(selected)/self.rows_in_page)

    def __init__(self, items, pos, data_dir, **kwargs):
        basic_text_box.__init__(self, pos, data_dir)
        self.text_box.sounds.append("select_beep")
        self.text_box.sounds.append("back_beep")

        #set say function to private; so ppl do not use it
        self.__say = self.say
        self.say = None

        self.items = items
        self.data_dir = data_dir
        self.pos = pos

        if 'font' in sorted(kwargs.keys()):
            self.font = kwargs['font']
        else:
            self.font = this.default_font

        if 'end_formatting' in sorted(kwargs.keys()):
            self.end_formatting = kwargs['end_formatting']
        else:
            self.end_formatting = '\n'

        self.render()

        self.rows_in_page = len(render_text)/len(self.page_wrap(render_text,
            Font_data.name, Font_data.size))

        self.select(0)

    def select_next(self):
        self.select(self.selected+1)

    def select_previous(self):
        self.select(self.selected-1)

    def get_selected(self):
        return sorted(self.items.keys)[self.selected]

    def activate_selected(self, *args):
        selected = self.get_selected()
        if self.items[selected].__class__.__name__ != 'dict':
            if self.items[selected] != None:
                if self.items[selected](selected, *args) == "previous":
                    self.previous_menu()
            elif self.items[selected] != "previous":
                self.text_box.sounds["back_beep"].play()
            else:
                self.previous_menu()
        else:
            self.previous = self.items
            self.items = self.items[selected]

    def previous_menu(self):
        if self.previous != None:
            self.text_box.sounds["back_beep"].play()
            self.items = previous
            self.render()
        else:
            self.hide()

    def draw_func(self, surface):
        this.fonts.get_data(self.font.name).render_to(self.text_box,
                (0, 0), self.render_text[self.page_number], size = self.font.size)

def text_martrix(items, pos, data_dir, **kwargs):
    if 'font' in sorted[kwargs.keys()]:
        return text_menu(items, pos, data_dir, font = kwargs['font'], end_formatting = '')
    else:
        return text_menu(items, pos, data_dir, end_formatting = '')

this.textbox = text_box((0 , 0), "data")
this.textbox.set_pos(0, this.window.get_height() - this.textbox.border.rect.bottom)

buff = collections.namedtuple('buff', ['stat', 'buff'])

def concat_dicts(*dicts, **kwargs):
    output = {}
    for dic in dicts:
        if len(dic) > 0:
            keys = output.keys() | dic.keys()
            output = {k: output.get(k, kwargs["default"]) + dic.get(k, kwargs["default"]) for k in keys }
    return output

def deconcat_dicts(*dicts, **kwargs):
    output = {}
    for dic in dicts:
        if len(dic) > 0:
            keys = output.keys() | dic.keys()
            output = {k: output.get(k, kwargs["default"]) - dic.get(k, kwargs["default"]) for k in keys }
    return output

class entity(moveable):

    def __init__(self, name, pos, basestat, **kwargs):
        moveable.__init__(self, name, pos, **kwargs)
        self.__stunned = 0
        self.__basestat = basestat
        self.__equipped = {}
        self.__inventory = {}
        self.__moves = {}
        self.__temp_buffs = []
        self.__stats = {}
        self.__persuasion = 0
        self.__damage_taken = 0 
        self.__stats_needs_update = True

    def get_imagename(self):
        return self._imagename

    def get_buffs_from_dict(self, dictbuff):
        buffs = []
        for item in dictbuff:
            buffs.append(item["buffs"])
        return concat_dicts(*buffs, default = 0)

    def get_basestats(self):
        return self.__basestat

    def __update_stats(self):
        self.__stats = concat_dicts(self.__basestat,
                self.get_buffs_from_dict(self.__temp_buffs),
                    self.get_buffs_from_dict(self.__equipped), default = 0)
        self.__stats["enlightenment"] *=  self.__stats["focus"] / 2
        self.__stats["enlightenment"] +=  0.25 * self.__stats["determination"]
        self.__stats["enlightenment"] *= random.randrange(0.2, 1.1)
        self.__stats["determination"] -= self.__damage_taken
    
    def is_dead(self):
        stats = self.get_stats()
        if stats["determination"] - self.__damage_taken <= 0:
            return True
        elif self.persuasion > stats["determination"] + stats["focus"]:
            return True
        return False

    def get_stats(self):
        if self.__stats_needs_update:
            self.__update_stats()
            self.__stats_needs_update = False
        return self.__stats

    def add_move(self, move):
        self.__moves[move["name"]] = move

    def get_moves(self):
        return self.__moves

    def unequip(self, itemname):
        self.__stats_needs_update =  True
        self.inventory[itemname] = self.__equipped[itemname]
        self.__equipped.pop(itemname)

    def equip(self, itemname):
        self.__stats_needs_update =  True
        self.__equipped[itemname] = self.__inventory[itemname]
        self.__inventory.pop(itemname)

    def get_equipped(self):
        return self.__equipped

    def add_to_inventory(self, item):
        if item["name"] in self.__inventory:
            self.__inventory[item["name"]] += item["quantity"]
        else:
            self.__inventory[item["name"]] = item

    def remove_from_inventory(self, item):
        self.__inventory[item["name"]] -= item["quantity"]
        if self.__inventory[item["name"]] <= 0:
            self.__inventory.pop(item["name"])

    def get_inventory(self):
        return self.__inventory

    def trade(self, item_to_remove, item_to_gain):
        self.remove_from_inventory(item_to_remove)
        self.add_to_inventory(item_to_gain)

    def use_item(self, itemname):
        self.__stats_needs_update =  True
        for buff in self.__inventory[itemname]["buffs"]:
           self.basestat[buff] +=  self.__inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]
        if self.__inventory[itemname][effect] != None:
            self.__inventory[itemname][effect]()
        if self.__inventory[itemname]["equipabble"]:
            self.equip(itemname)
        if  self.inventory[itemname]["consumable"]:
            self.remove_from_inventory(self.__inventory[itemname])

    def _stun(self, enemy_stats,  NumberOfTurns):
        enemy_attack = (enemy_stats/4) * random.randrange(0 , (0.5 + enemy_stats["focus"]/130))
        if self.get_stats()["wit"] >  enemy_attack:
            this.battlebox.say(self.name + " was stunned!")
            self.stunned = NumberOfTurns

    def _take_damage(self, enemy_stats, is_hopeful):
        stats = self.get_stats()

        if is_hopeful:
                for k in enemy_stats:
                    enemy_stats[k] *= 2

        if stats["wit"] > enemy_stats["enlightenment"] / 4 * random.randrange(0, 0.5 + enemy_stats["focus"] / 55 ):
           self.persuasion += enemy_stats["enlightenment"] 
        else:
            this.battlebox.say("your oppenent out witted your attack! You focus on not embarrasing yourself futher.")

        self.__damage_taken = self.__damage_taken + enemy_stats["focus"] - stats["control"]
         
    def use_move(self, movename, enemy):
        if self.basestat["thought"] - self.moves[movename]["thought"] > 0 ^ self.__stunned == 0:
            self.basestat["thought"] =- self.moves[movename]["thought"]
            for buff in self.moves[movename]["buffs"]:
                self.basestat += self.moves[movename]["buffs"][buff]
            self.__temp_buffs.append(self.moves[movename]["temporary_buffs"])
            self.__stats_needs_update =  True
            if self.moves[movename]["stun_effect"] > 0:
                enemy.stun(self.get_stats(), 
                        self.moves[movename]["stun_effect"])
            return True
        else:
            return False

    def next_turn(self):
        self.stunned -= 1
        for buff in self.__temp_buffs:
            buff["turns"] -= 1
            if buff["turns"] < 0:
                self.__temp_buffs.remove(buff)
        self.get_stats()
        
    def load_battle_assets(self):
        self._imagename = imagename+"_battle"
        self.load_sprite(this.data)
        self.fighting = True

    def is_hopeful(self):
        if self.get_stats()["hope"] > random.randrange(0, 500):
            return True
        else:
            return False

this.battlebox = text_box((0 , 0), "data")
this.battlebox.set_pos(0, this.window.get_height() - this.textbox.border.rect.bottom)

class player(entity):

    def get_inventory_menu_data(self):
        output = {}
        for item_name in sorted(self.get_inventory().keys()):
            output[item_name] = self.use_item
        return output

    def get_equipped_menu_data(self):
        output = {}
        for item_name in sorted(self.get_equipped().keys()):
            output[item_name] = self.unequip
        return output

    def get_stats_menu_data(self):
        output = {}
        for stat, val in self.get_stats():
            output[stat+"  =  "+val] = None
        return output
   
    def is_sure_dialog(self, if_sure):
        this.textbox.say("are you sure?", self.font.name, self.font.size) 
        def sure_dialog(self, if_sure):
            self.game.text_box.next_page()
            self.game.text_box.hide()
            return if_sure
        return {
                    "yep" : self.sure_dialog(self, if_sure),
                    "nope": self.sure_dialog(self, "previous"),
                }
    
    def get_player_menu_items(self, game):
        return {
                    "inventory" : self.get_inventory_menu_data,
                    "equipped" : self.get_equipped_menu_data,
                    "stats" : self.get_stats_menu_data,
                    "save and quit" : self.is_sure_dialog(game.save_quit, game)
               }

    def __init__(self, name):
        entity.__init__(self, "player", {
                'determination' : 100,
                'enlightenment' : 5,
                'hope' : 10,
                'focus' : 1,
                'wit' : 10,
                'thought' : 100
            }
            )
        self.menu = text_menu(self.get_player_menu_items()) 
        self.player_name = name

    def is_player(self):
        return True;

    def get_player_menu(self):
        return self.menu

class battle_entity():

    def __init__(self, entity):
        self._entity = entity
        self.__func_queue = collections.Deque()

    def use_item(self, itemname):
        self.__func_queue.append({"func" : self.__entity.use_item, "args" : itemname})

    def use_move(self, movename):
        self.__func_queue.append({"func" : self.__entity.use_move, "args" : movename})

    def do_queued(self):
        function = self.queue.pop()
        out = function["func"](*funtction["args"])
        self._entity.next_turn()
        return out

    def ready(self):
        if len(self.__func_queue) > 0:
            return True
        return False

    def get_stats(self):
        return self._entity.get_stats()

    def is_hopeful(self):
        return self._entity.is_hopeful()

class battle_player(battle_entity):

    def __init__(self, entity):
        battle_entity(self, entity)

    def get_battle_menu(self):
        return text_menu

class battle_NPC(battle_entity):

    def __init__(self, entity, battle_queue, pos):
        battle_entity.__init__(self, entity)
        self.battle_sprite = sprite(entity.get_imagename() + "_battle", pos, battle = True)

    def get_what_do_next(player_stats):
        stats = self.get_stats()
        if stats["determination"] < 25:
            health_items = {}
            if len(self.entity.get_inventory()) != 0:
                    for item in self._entity.get_inventory():
                        if item["type"] == "health":
                            health_items[item["potency"]] = item["name"]
                    self.entity.use_item(health_items[sorted(health_items.keys())[-1]])
               
class battle(threading.Thread):

    def __init__(self, entity, entity1):
        threading.Thread.__init__(self)
        self.player = battle_entity(entity)
        self.npc = battle_NPC(entity1, (0,0))

        calc_pos = lambda winx, objx: winx/2 - objx/2
        self.entity1.set_pos((clac_pos(this.window.get_width(), 
                self.entity1.rect.right),
                    calc_pos(this.window.get_height(), self.entity1.rect.bottom)))

        if self.player.get_stats["speed"] > self.npc.get_stats["speed"]:
            self.__player_turn= True
        else:
            self.__player_turn= False

        this.set_background("battle")
        self.start()
    
    def get_player(self):
        return self.player

    def get_npc(self):
        return self.npc

    def run(self):
        self.check_if_dead() 
        if  self.__player_turn & self.player.ready():
            self.player.do_queued()
        elif not self.__player_turn & self.npc.ready():
            self.npc.do_queued()

def update():
    if not this.inbattle:
        this.sprites.update(self.data)
        this.sprites.draw(self.window)
        this.textbox.draw(self.window)
    else:
        this.battle_sprites.update(self.data)
        this.battle_sprites.draw(self.window)
    pygame.display.update()

