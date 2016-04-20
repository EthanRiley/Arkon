import game_data, game_object_loader, multiprocessing, random, time, collections, sys, json

#(0, 0) is top left corner in pygame.

this = sys.modules[__name__]

this.data = game_data.game_data("data")
this.window = pygame.display.setmode([680, 480])

position = collections.namedtuple("position", ['x', 'y'])

def subset_dicts_from_array(dict1, array):
    return { k : dict1[k] for k in dict1.keys & array } 

def merge_arrays_to_dict(key_array, var_array):
    return { k : v for k in key_array for v in var_array }

class LayeredDirtyDict():

    def __init__(self):
        collections.UserDict.__init__(self)
        self.sprites = LayeredDirty()
        self.sprite_names = []

    def _get_dict(self):
        return collections.OrderedDict(merge_arrays_to_dict(self.sprite_names, self.sprites.sprites()))

    def add(self, name, sprite, **kwargs):
        self.sprites.add(sprite, **kwargs)
        self.sprite_names.append(name)

    def pop(self, name):
        sprite = self._get_dict()[name]
        self.sprite_names.remove(name)
        self.sprites.remove(sprite)
        return sprite

    def __getitem__(self, key):
        return _get_dict()[key]

    def __iter__(self):
        return iter(self._get_dict())

    def __len__(self):
        return len(self.sprite_names)

    def draw(self, surface):
        self.sprites.draw(surface)

    def clear(self, surface, background):
        self.sprites.clear(surface, background)

    def update(self, *args):
        self.sprites.update(*args)

    def update_dict(self, Dict):
        for key, val in Dict:
            self.__setitem__(key, val)

this.sprites = LayeredDirtyDict()
this.onscreen_sprites = LayeredDirtyDict()

this.background_music = pygame.mixer.channel(0)
this.background = None

def set_background(name):
    this.background = self.data.backgrounds.get_data(name)
    self.background_music.play(self.data.sounds.get_data(name))

class sprite(pygame.sprite.DirtySprite):

    def __init__(self, imagename, pos, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        self.sounds = [] 

        if 'sounds' in sorted(kwargs.keys()):
            self.sounds = this.data.sounds.get_data_dict(kwargs['sounds'])
            self.sound_names = kwargs['sound_names']
        else:
            self.sound_names = []

        self._imagename = imagename

        self.image = this.data.sprites.get_data(self._imagename)
        self.rect = self.image.get_rect()
        self.rect.x = pos.x
        self.rect.y = pos.y
        if 'battle' in sorted(kwargs.keys()):    
            if kwargs['battle']:
                this.battle_sprites.add(imagename, self)
            else:
                this.sprites.add(imagename, self)
        else:
            this.sprites.add(imagename, self)

        self.save_vars = [ 'imagename', 'sound_names', 'pos' ] 

    def get_rect(self):
        return self.image.get_rect()

    def get_pos(self):
        return position(self.rect.x, self.rect.y)

    def save_data(self):
        self.pos = self.get_pos()
        return { "vars" : subset_dicts_from_array(self.__dict__, self.save_vars), 
                    'classname' :  self.__class__.__name__ }
    
    def load_save_data(self, data):
        self.__dict__.update(data)

    def activate(self):
        pass

class door(sprite):

    def __init__(pos ,setting_from, setting_to, **kwargs):
        imagename = "door"
        if 'imagename' in sorted(kwargs.keys()):
            imagename = kwargs['imagename']

        sprite.__init__(self, imagename, pos, sounds = ['door_open'])
        self.setting_to = setting_to
        self.setting_from = setting_from
        self.save_vars += ['setting_to', 'setting_from']

    def activate(self):
        this.story.set_zone(setting_to)
        s_from = self.setting_from 
        self.setting_from = self.setting_to
        self.setting_to = s_from 

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

        self.facing = "forward"
        self.save_vars.append('facing')

    def facing(self, direction):
        self.facing = direction

    def move(self, dx, dy , **kwargs):
        rect = self.get_rect()
        for sprite in this.sprites:
            if sprite != self:
                rect1 = sprite.get_rect()
                if rect1.left <= rect.right + dx & rect1.top >= rect.bottom + dy:
                    if rect1.right >= rect.left + dx & rect1.bottom <= rect.top + dy:
                        self.sounds["collide_beep"].play()
                        self.moving = False
                        if sprite.__class__.__name__ == "door":
                            sprite.activate()
                        return False
        if 'move_func' not in sorted(kwargs.keys()):
            self.rect.move(dx, dy)
        else:
            kwargs['move_func'](dx, dy)
        self.moving = True
        return True

    def update(self, *args):
        if self.moving:
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


this.fonts = game_data.font_data(os.path.join("data", "fonts"))
class basic_text_box(object):

    def __init__(self, pos, border, **kwargs):
        self.border = game_data.sprite(border, pos, sounds = sounds)
        this.sprites.remove(self.border._imagename)
        self.rect = self.border.get_rect()
        sounds = ['activate_beep']
        if 'sounds' in sorted(kwargs.keys()):
            sounds += kwargs['sounds']
        self.text_box = pygame.Sprite()
        self.text_box.image = pygame.Surface([self.rect.x - 2, self.rect.y - 2])
        self.text_box.rect = self.text_box.image.get_rect()
        self.text_box.image.fill(0)
        self.text_box.rect.x = pos.x - 2
        self.text_box.rect.y = pos.y -2

    def set_pos(self, pos):
        self.border.rect.x = pos.x
        self.border.rect.y = pos.y
        self.text_box.rect.x = pos.x - 2
        self.text_box.rect.y = pos.y - 2

    def get_pos(self):
        return position(self.border.rect.x, self.border.rect.y)

    def word_wrap(self, text, font_name, font_size):
        font = this.font.get_data(font_name)
        textbox_x = self.text_box.image.get_rect().x
        if textbox_x < font.get_rect(text,
                size = font_size).x:
            output = ""
            for word in text.split(' '):
                if font.get_rect(output + ' ' + word, size = font_size).x > textbox_x:
                    output += '\n'
                    x = 0
                output += ' ' + word  
            return output.replace(' ', '', 1)
        else:
            return text

    def page_wrap(self, text, font_name, font_size):
        font = this.fonts.get_data(font_name)
        y = self.textbox.image.get_rect().y
        if font.get_rect(text, size = font_size).y < y:
            page_text = ""
            pages = []
            for line in text.split('\n'):
                if font.get_rect(page_text,
                        size=font_size).y < y:
                    page_text += '\n' + line
                else:
                    pages.append(page_text)
                    page_text = ""
            return pages
        else:
            return text

    def draw_func(self, surface):
        pass
    
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

    def __init__(self, pos):
        basic_text_box.__init__(self, pos, "text_box")
        self.pages_to_render = collections.deque()

    def activate(self, **kwargs):
        self.txt_data = self.pages_to_render.pop()
        self.border.sounds["activate_beep"].play()
        if 'func' in sorted(kwargs):
            kwargs['func']()

    def draw_func(self, surface):
          this.fonts.get_data(self.txt_data.font_name).render_to(self.text_box,
                  (0, 0), self.txt_data.text, size = self.txt_data.font_size)

    def say(self, text, **kwargs):
        font = None
        if 'font' not in sorted(kwargs.keys()):
            font = this.default_font
        else:
            font = kwargs['font']

        if 'speaker' in sorted(kwargs.keys()):
            text = kwargs['speaker'] + '\n' + text

        text = self.word_wrap(text, font.name, font.size)
        for page in self.page_wrap(text, font.name, font.size):
            self.pages_to_render.append(text_data(page, font.size, font.name))
        activate()

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
        self.border.sounds["select_beep"].play()
        
        self.selected_index = index % len(self.items.keys())
        
        selected = self.items.keys()[index]
        if self.selected != None & selected != self.selected:
            self.__deselect(selected)

        self.text[self.text.find(selected) - 2] = '>'
        self.selected = selected
        self.page_number = int(self.text.find(selected)/self.rows_in_page)

    def __init__(self, items, pos, **kwargs):
        border = "text_menu"
        if 'border' in kwargs:
            border =  kwargs['border']
        basic_text_box.__init__(self, pos, border, sounds = ['select_beep', 'back_beep'])

        self.items = items

        if 'font' in sorted(kwargs.keys()):
            self.font = kwargs['font']
        else:
            self.font = this.default_font

        if 'end_formatting' in sorted(kwargs.keys()):
            self.end_formatting = kwargs['end_formatting']
        else:
            self.end_formatting = '\n'

        self.render()

        self.rows_in_page = len(self.render_text)/len(self.page_wrap(self.render_text,
            Font_data.name, Font_data.size))

        self.select(0)
        self.save_vars += ['end_formatting', 'font', 'items']
        
    def select_next(self):
        self.select(self.selected_index+1)

    def select_previous(self):
        self.select(self.selected_index-1)

    def get_selected(self):
        return self.selected

    def activate(self, *args):
        selected = self.items[selected]
        if self.items[selected].__class__.__name__ != 'dict':
            if self.items[selected] != None:
                if self.items[selected](selected, *args) == "previous":
                    self.previous_menu()
            elif self.items[selected] != "previous":
                self.border.sounds["back_beep"].play()
            else:
                self.previous_menu()
        else:
            self.previous = self.items
            self.items = self.items[selected]

    def previous_menu(self):
        if self.previous != None:
            self.border.sounds["back_beep"].play()
            self.items = previous
            self.render()
        else:
            self.hide()

    def draw_func(self, surface):
        this.fonts.get_data(self.font.name).render_to(self.text_box,
                (0, 0), self.render_text[self.page_number], size = self.font.size)

def text_matrix(items, pos, **kwargs):
    if 'font' in sorted[kwargs.keys()]:
        return text_menu(items, pos, font = kwargs['font'], end_formatting = '', border = "textbox")
    else:
        return text_menu(items, pos, end_formatting = '', border = "textbox")

this.textbox = text_box((0 , 0))
this.textbox.set_pos(0, this.window.get_height() - this.textbox.border.rect.y)

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
        self.__dialog = {} 
        self.__persuasion = 0
        self.__damage_taken = 0 
        self.__stats_needs_update = True
        self.save_vars += ['__moves', '__inventory', '__equipped', '__basestat' ]

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

    def get_inventory_menu_data(self, **kwargs):
        output = {}
        for item_name in sorted(self.get_inventory().keys()):
            if 'do_func' not  in kwargs:
                output[item_name] = self.use_item
            else:
                output[item_name] = kwargs['do_func']
        return output

    def trade_menu_data(self, buyer):
        pass

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

class NPC(entity):
    
    def __init__(self, name, pos, basestat, **kwargs):
        entity.__init__(self, name, pos, basestat, **kwargs)
        self.dialog = {}
        self.save_vars.append('__dialog')

    def get_next_dialog(self):
        this.textbox.say(self.__dialog.keys()[0],font = self._imagename, speaker = self._imagename)
        response = self.__dialog.pop()
        this.sprites

class player(entity):

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
        def sure():
            this.text_box.next_page()
            this.game.text_box.hide()
            return if_sure()
        return {
                    "yep" : sure(),
                    "nope": "previous"
                }

    def get_player_menu_items(self):
        return {
                    "inventory" : self.get_inventory_menu_data,
                    "equipped" : self.get_equipped_menu_data,
                    "stats" : self.get_stats_menu_data,
                    "save and quit" : self.is_sure_dialog(this.save_quit)
               }

    def __init__(self, name, pos):
        entity.__init__(self, "player", pos,
                {
                    'determination' : 100,
                    'enlightenment' : 5,
                    'hope' : 10,
                    'focus' : 1,
                    'wit' : 10,
                    'thought' : 100
                }
            )

        this.player_menu = text_menu(self.get_player_menu_items()) 
        self.player_name = name
        self.save_vars.append('player_name')
    
    def move(self, dx, dy):
        return moveable.move(self, dx, dy, this.background.scroll)

    def get_pos(self):
        rect = self.get_rect()
        return position(rect.x, rect.y)

    def is_player(self):
        return True;

    def get_player_menu(self):
        return self.menu

def get_trade_menu(buyer, seller):
    return text_menu({
            "buy": seller.get_inventory
            "sell": buyer.get_inventory
        }


def response_box(items):
    responsebox = text_menu(items, (0, 0), border = "text_box")
    responsebox.set_pos(0, this.window.get_height() - this.textbox.border.rect.y )
    return responsebox


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
               
class battle(multiprocessing.Process):

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

    def battle_end(self):
        if self.npc.is_dead() | self.player.is_dead():
            this.inbattle = False
            self.terminate()
        return False

    def run(self):
        if not self.battle_end(): 
            if  self.__player_turn & self.player.ready():
                self.player.do_queued()
            elif not self.__player_turn & self.npc.ready():
                self.npc.do_queued()

def update():
    this.onscreen_sprites.clear(this.background)
    this.onscreen_sprites.update(self.data)
    this.onscreen_sprites.draw(self.window)
    if not this.inbattle:
        this.textbox.draw(self.window)
        this.player_menu.draw(self.window)
    else:
        this.battlebox.draw(self.window)
    pygame.display.update()

def save_data():
   return json.dumps({
       "sprites" : {
           sprite.imagename: sprite.save_data() for sprite in this.sprites
        },
       "settings":{
            setting.background: setting.save_data() for setting in this.settings        
        }
    })

def load_data():
    game = json.load(open("save.json"))
    this.sprites.update_dict(game["sprites"])
