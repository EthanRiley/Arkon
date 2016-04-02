import game_data, game_objects, threading, random, time

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

class moveable(meta_sprite):
    def __init__(self, imagename, pos, **kwargs):
        meta_sprite.__init__(self, imagename, pos)
        sounds.append("collide_beep")
        self.__frame = 0

        if 'sounds' in sorted(kwargs.keys()):
            self.sounds = kwargs['sounds']
            kwargs.pop('sounds')

    def load_data(self, data):
        meta_sprite.load_data(self, data)
        directions = [
                "right",
                "forward",
                "backward"
        ]

        self.animation = {}
        for direction in directions:
            self.animation[direction] = data.get_data_array(self._imagename
                    + "_anim_" + direction + "_\d")

    def facing(self, direction):
        self.facing = direction

    def move(self, dx, dy, game):
        rect = self.get_rect()
        for sprite in game.sprites.sprites():
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


text_data = namedtuple("text_data", ['text', 'font_size', 'font_name'])

class basic_text_box(object):
    def __init__(self, pos, data_dir):
        self.border = meta_sprite("textbox_border", pos)
        rect = self.border.get_rect()
        self.text_box = meta_sprite(self, "textbox", (pos.x - rect.x, pos.y - rect.y))
        self.text_box.sounds.append("activate_beep")
        self.fonts = font_data(os.path.join(data_dir, "fonts"))

    def word_wrap(self, text, font_name, font_size):
        if self.get_rect().x < self.fonts.get_data(font_name).get_rect(text,
                size = font_size).x:
            x = 0
            output = ""
            for word in text.split(' '):
                word_rect = self.get_data(font_name).get_rect(text,
                        size = font_size)
                if x + word_rect.x > rect.x:
                    output += '\n'
                    x = 0
                output += word
            return output
        else:
            return text

    def page_wrap(self, text, font_name, font_size):
        font = self.fonts.get_data(font_name)
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

    def load_data(self, data):
        self.border.load_data(data)
        self.text_box.load_data(data)

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
          self.fonts.get_data(self.txt_data.font_name).render_to(self.text_box,
                  (0, 0), self.txt_data.text, size = self.txt_data.font_size)

    def say(self, text, font_name, font_size):
        text = self.word_wrap(text, font_name, font_size)
        for page in self.page_wrap(text, font_name, font_size):
            self.text_to_render.append(text_data(page, font_size, font_name))
        next_page()

font_data = namedtuple('font_data', ['font_name', 'font_size'])

class text_menu(basic_text_box):

    def render(self):
        self.text = ""
        self.render_text = []
        for item_name in sorted(self.items.keys()):
            self.text += "    " + item_name + self.end_formatting
        if self.end_formatting != '\n':
            self.text = self.word_wrap(text, self.font_data.font_name, self.font_data.font_size)
        self.render_text = self.page_wrap(self.text, self.font_data.font_name, font_size)

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

    def __init__(self, items, pos, data_dir, font_data, **kwargs):
        text_box.__init__(self, pos, data_dir)
        self.text_box.sounds.append("select_beep")
        self.text_box.sounds.append("back_beep")

        #set say function to private; so ppl do not use it
        self.__say = self.say
        self.say = None

        self.items = items
        self.data_dir = data_dir
        self.pos = pos
        self.font_data = font_data

        if 'end_formatting' in sorted(kwargs.keys()):
            self.end_formatting = kwargs['end_formatting']
        else:
            self.end_formatting = '\n'

        self.render()

        self.rows_in_page = len(render_text)/len(self.page_wrap(render_text,
            font_data.font_name, font_data.font_size))

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
                self.items[selected](selected, *args)
            else:
                self.text_box.sounds["back_beep"].play()
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
        self.fonts.get_data(self.font_data.font_name).render_to(self.text_box,
                (0, 0), self.render_text[self.page_number], size = self.font_data.font_size)

def text_martrix(items, pos, data_dir, font_data):
    return text_menu(items, pos, data_dir, font_data, end_formatting = '')

class Game(object):

    def __init__(self, name):
        self.data = GameData("data")
        self.sprites = pygame.sprite.LayeredDirty()
        self.window = pygame.display.setmode([680, 480])
        self.background_music = pygame.mixer.channel(0)
        pygame.display.caption(name)

        self.textbox = text_box((0,0), "data")
        self.textbox.load_data(self.data)

    def set_background(self, name):
        self.window.blit(self.data.backgrounds.get_data(name))
        self.background_music.play(self.data.sounds.get_data(name))

    def load_sprite(self, meta_sprite):
        meta_sprite.load_data(self.data)
        self.sprites.add(meta_sprite)
        return meta_sprite

    def update(self):
        self.sprites.update(self.data)
        self.sprites.draw(self.window)
        self.textbox.draw(self.window)
        pygame.display.update()

buff = namedtuple('buff', ['stat', 'buff'])

class entity(moveable):

    def __init__(self, name, pos,  basestat, **kwargs):
        moveable.__init__(self, name, pos, **kwargs)
        self.__basestat = basestat
        for key in ordered(kwargs.keys()):
            self.basestat[key] = kwargs[key]
        self.__basestat['determination'] = 100
        self.__equipped = {}
        self.__inventory = {}
        self.__moves = {}
        self.__temp_buffs = []
        self.__stats = {}
        self.__stats_needs_update = True

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
        self.__inventory[item["name"]] += item["quantity"]

    def remove_from_inventory(self, item):
        self.__inventory[item["name"]] -= item["quantity"]
        if self.__inventory[item["name"]] <= 0:
            self.__inventory.pop(item["name"])

    def get_inventory(self):
        return self.__inventory

    def trade(self, item, item1):
        self.remove_from_inventory(item)
        self.add_to_inventory(item1)

    def use_item(self, itemname, game):
        self.__stats_needs_update =  True
        for buff in self.__inventory[itemname]["buffs"]:
           self.basestat[buff] +=  self.__inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]
        if self.__inventory[itemname][effect] != None:
            self.__inventory[itemname][effect](game)
        if self.__inventory[itemname]["equipabble"]:
            self.equip(itemname)
        if  self.inventory[itemname]["consumable"]:
            self.remove_from_inventory(self.__inventory[itemname])

    def use_move(self, movename, game):
        self.__stats_needs_update =  True
        for buff in self.moves[movename]["buffs"]:
            self.basestat += self.moves[movename]["buffs"][buffs]
        self.temp_buffs.append(self.moves[movename]["temporary_buffs"])

    def load_battle_assets(self, game):
            self._imagename = imagename+"_battle"
            self.load_sprite(game.data)
            self.fighting = True

    def is_hopeful(self):
        if self.get_stats()["hope"] > random.randrange(1, 500):
            return True
        else:
            return False

class player(entity):

    def __init__(self, name):
        player.name = name

    def __del__(self):
        self.save()

    def is_player(self):
        return True;

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
    
    def get_player_menu(self):
        return {
                    "inventory" : self.get_inventory_menu_data,
                    "equipped" : self.get_equipped_menu_data,
                    "stats" : self.get_stats_menu_data,
                    "save and quit" : self.__del__
               }

class battle_entity:
    def __init__(self, entity, game):
        entity.load_battle_assets(game)
        self.__entity = entity
        self.__func_queue = collections.Deque()

    def use_item(self, itemname):
        self.__func_queue.append({"func" : self.__entity.use_item,"args" : itemname})

    def use_move(self, movename):
        self.__func_queue.append({"func" : self.__entity.use_move, "args" : movename})

    def do_queued(self):
        function = self.queue.pop()
        function["func"]("args")
        self.turns += 1

    def ready(self):
        if len(self.__func_queue) > 0:
            return True
        return False

    def get_stats(self):
        return self.__entity.get_stats()

    def is_hopeful(self):
        return self.__entity.is_hopeful()

class battle(threading.Thread):
    def __init__(self, entity, entity1, game):
            threading.Thread.__init__(self)
            self.entity = battle_entity(entity, game)
            self.entity1 = battle_entity(entity1, game)
            game.set_background("battle")
            self.start()

    def run(self):
        if self.__entity_turn & self.entity.ready():
            self.entity.do_queued()
        if not self.__entity_turn & self.entity1.ready():
            self.entity1.do_queued()
