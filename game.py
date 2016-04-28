#!/usr/bin/env python3

import threading, random, collections, sys, json, pygame, os, re
import object_loader, game_data
from pygame.locals import *

#(0, 0) is top left corner in pygame.

this = sys.modules[__name__]

position = collections.namedtuple("position", ['x', 'y'])

def subset_dict_from_array(dict1, array):
    return { k : dict1[k] for k in array }

def ordered_subset_dict_from_array(dict1, array):
    out_dict = collections.OrderedDict()
    for k in array:
        out_dict[k] = dict1[k]
    return out_dict

def orderd_dict_from_dict(dict):
    out= collections.OrderedDict()
    for k in list(dict.keys()):
        out[k] = dict[k]
    return out

def array_and(array, array1):
    out = []
    for i in array:
        for v in array1:
            if v == i:
                out.append(v)
    return out

def merge_arrays_to_dict(key_array, var_array):
    return {k : v for k in key_array for v in var_array }

def array_to_pos(array):
    return position(array[0], array[1])

def list_to_str(list):
    out  = ""
    for char in list:
        out+=char
    return out

class LayeredDirtyDict():

    def __init__(self):
        collections.UserDict.__init__(self)
        self.sprites = pygame.sprite.LayeredDirty()
        self.sprite_names = []

    def _get_dict(self):
        return collections.OrderedDict(merge_arrays_to_dict(self.sprite_names, self.sprites.sprites()))

    def add(self, name, sprite):
        self.sprites.add(sprite)
        self.sprite_names.append(name)

    def pop(self, name):
        sprite = self._get_dict()[name]
        self.sprite_names.remove(name)
        self.sprites.remove(sprite)
        return sprite

    def __contains__(self, item):
        return item in self.sprite_names

    def keys(self):
        return self.sprite_names
    
    def __getitem__(self, key):
        return self._get_dict().get(key)

    def __setitem__(self, key, val):
        self.add(key, val)

    def __iter__(self):
        return iter(self._get_dict())

    def __len__(self):
        return len(self.sprite_names)

    def draw(self, surface):
        self.sprites.draw(surface)

    def clear(self, surface, background):
        self.sprites.clear(surface, background)

    def empty(self):
        self.sprites.empty()
        self.sprite_names = []

    def update(self, *args):
        self.sprites.update(*args)

    def update_dict(self, Dict):
        for key, val in Dict:
            self.__setitem__(key, val)


def set_background(name):
    this.background = this.data.backgrounds.get_data(name)
    #self.background_music.play(this.data.sounds.get_data(name))

class sprite(pygame.sprite.DirtySprite):

    def __init__(self, imagename, pos, **kwargs):
        pygame.sprite.DirtySprite.__init__(self)
        #self.sounds = []

        #if 'sounds' in sorted(kwargs.keys()):
        #    self.sounds = this.data.sounds.get_data_dict(kwargs['sounds'])
        #    self.sound_names = kwargs['sounds']
        #else:
        #    self.sound_names = []

        self._imagename = imagename

        self.image = this.data.sprites.get_data(self._imagename)
        self.rect = self.image.get_rect()
        self.rect.x = pos.x
        self.rect.y = pos.y
        if 'battle' in sorted(kwargs.keys()):    
            if kwargs['battle']:
                this.battle_sprites.add(imagename, self)

        self.save_vars = [ '_imagename', 'pos' ]

    def get_rect(self):
        return self.image.get_rect()
    
    def get_pos(self):
        return position(self.image.get_rect().x, self.image.get_rect().y)

    def set_pos(self, pos):
        self.rect.x = pos.x
        self.rect.y = pos.y

    def save_data(self):
        self.pos = self.get_pos()
        return {"vars": subset_dict_from_array(self.__dict__, self.save_vars),
                'classname': self.__class__.__name__}


    def load_save_data(self, data):
        self.__dict__.update(data)

    def activate(self):
        pass

class door(sprite):

    def __init__(self, pos , setting_to, **kwargs):
        imagename = "door"
        if 'imagename' in sorted(kwargs.keys()):
            imagename = kwargs['imagename']

        sprite.__init__(self, imagename, pos) #, sounds = ['door_open'])
        self.setting_to = setting_to
        self.save_vars.append('setting_to')

    def save_data(self):
        self.pos = self.get_pos()
        return {"vars": subset_dict_from_array(self.__dict__, self.save_vars),
                'classname': self.__class__.__name__}

    def __del__(self):
        this.data_sprites[self._imagename] = self.save_data()

    def load_save_data(self, data):
        self.__dict__.update(data)

    def activate(self):
        #self.sounds['door_open'].play()
        this.settings.load(self.setting_to)

class item(sprite):

    def __init__(self, pos, item_data, **kwargs):
        sprite.__init__(self, "dropped_item", pos)
        self.item_data = item_data
        self.save_vars += [ 'item_data', 'setting_from' ]

    def save_data(self):
        self.pos = self.get_pos()
        return {"vars": subset_dict_from_array(self.__dict__, self.save_vars),
                'classname': self.__class__.__name__}

    def __del__(self):
        this.data_sprites[self._imagename] = self.save_data()

    def load_save_data(self, data):
        self.__dict__.update(data)


class settings:
    
    def __init__(self, settings_dict):
        self.settings  = settings_dict
        self.__current_setting = ""

    def load_data_sprite(self, sprite):

        def get_data_args(sprite, argtype):
                args = ordered_subset_dict_from_array(sprite["vars"],
                    this.sprite_classes_args[sprite["classname"]][argtype])
                for arg in args:
                    if arg == "pos":
                        args[arg] = array_to_pos(args[arg])
                    sprite["vars"].pop(arg)
                return args

        args = list(get_data_args(sprite, "args").values())
        kwargs = get_data_args(sprite, "kwargs")
        Sprite = eval(sprite["classname"]+"(*args, **kwargs)")
        Sprite.load_save_data(sprite["vars"])
        return Sprite

    def load(self, setting_name):
        for Sprite in array_and(sorted(this.onscreen_sprites.keys()), self.settings[setting_name]["sprites_used"]):
            this.onscreen_sprites[Sprite].set_pos(array_to_pos(self.settings[setting_name]["sprites_used"][Sprite]))
            self.settings[setting_name]["sprites_used"].pop(Sprite)

        for sprite in self.settings[setting_name]["sprites_used"]:
                this.data_sprites[sprite]["vars"]["pos"] = array_to_pos(self.settings[setting_name]["sprites_used"][sprite])

        this.onscreen_sprites.update({k: self.load_data_sprite(this.data_sprites[k])
                                      for k in self.settings[setting_name]["sprites_used"]})
                                        
        this.set_background(setting_name)

        for k in self.settings[setting_name]["doors"]:
            if self.settings[setting_name]["doors"][k]["imagename"] == "":
                self.settings[setting_name]["doors"][k]["imagename"] = "door"

            Door = door(array_to_pos(self.settings[setting_name]["doors"][k]["pos"]),
                        k, imagename=self.settings[setting_name]["doors"][k]["imagename"])
            this.onscreen_sprites.add("door_to_" + k , Door)

        self.__current_setting = setting_name

    def get_current_setting(self):
        return self.__current_setting

class moveable(sprite):
    def __init__(self, imagename, pos, **kwargs):
      #  sounds = ["collide_beep"]
   #     if 'sounds' in sorted(kwargs.keys()):
    #        sounds += kwargs['sounds']

        sprite.__init__(self, imagename, pos)
        self.__frame = 0

        directions = [
                "right",
                "forward",
                "backward"
        ]

        self.animation = {}
        for direction in directions:
            self.animation[direction] = this.data.sprites.get_data_array(self._imagename
                    + "_anim_" + direction + "_\d")

        self.facing = "forward"
        self.save_vars.append('facing')
        self.moving = False

    def facing(self, direction):
        self.facing = direction

    def move(self, dx, dy , **kwargs):
        rect = self.get_rect()
        if this.background.get_rect.collidepoint(rect.x+dx, rect.y+dy):

            for sprite in this.onscreen_sprites:
                if sprite != self:
                    rect1 = sprite.get_rect()
                    if rect1.left <= rect.right + dx & rect1.top >= rect.bottom + dy:
                        if rect1.right >= rect.left + dx & rect1.bottom <= rect.top + dy:
                            #self.sounds["collide_beep"].play()
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

        else:
            return False

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
            self.__frame = self.__frame%len(self.animation[self.facing])
            self.moving = False

font_data = collections.namedtuple('font_data', ['size', 'name'])
text_data = collections.namedtuple('text_data', ['text', 'font_size', 'font_name'])

class basic_text_box():

    def __init__(self, pos, border, **kwargs):
        #  sounds = ['activate_beep']

        self.border = sprite(border, pos)
        self.rect = self.border.get_rect()

      #  if 'sounds' in sorted(kwargs.keys()):
       #     sounds += kwargs['sounds']

        self.text_box = pygame.sprite.Sprite()
        self.text_box.image = pygame.Surface([self.rect.width - 6, self.rect.height - 6])
        self.text_box.rect = self.text_box.image.get_rect()
        self.text_box.image.fill(0)
        self.text_box.rect.x = pos.x + 3
        self.text_box.rect.y = pos.y + 3

        self.visible = False

    def set_pos(self, pos):
        self.border.rect.x = pos.x
        self.border.rect.y = pos.y
        self.text_box.rect.x = pos.x + 3
        self.text_box.rect.y = pos.y + 3

    def get_pos(self):
        return position(self.border.rect.x, self.border.rect.y)

    def word_wrap(self, text, font_name, font_size):
        font = this.fonts.get_data(font_name)
        textbox_x = self.text_box.image.get_rect().width
        if textbox_x < font.get_rect(text,
                size = font_size).width:
            lines = []
            output = ""
            for word in text.split(' '):
                if textbox_x < font.get_rect(output + ' ' + word, size = font_size).width:
                    output += '\n'
                    lines.append(output.replace(' ', '', 1))
                    output = ""
                output += ' ' + word
            lines.append(output.replace(' ', '', 1))
            text = ""
            for line in lines:
                text+=line
        return text

    def page_wrap(self, text, font_name, font_size):
        font = this.fonts.get_data(font_name)
        y = self.text_box.image.get_rect().height
        if font.get_rect(text, size = font_size).y > y:
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
            return [text]

    def newline_draw_text(self, txt_data):
        lines = txt_data.text.split('\n')
        for lineNo in range(len(lines)):
            this.fonts.get_data(txt_data.font_name).render_to(self.text_box.image,
                        (6, 6 + 20 * lineNo), lines[lineNo], size=txt_data.font_size, fgcolor=(255, 255, 255))

    def draw_func(self):
        self.text_box.image.fill((0, 0, 0))
    
    def draw(self, surface):
        if self.visible:
            surface.blit(self.border.image, self.get_pos())
            surface.blit(self.text_box.image, self.text_box.rect)
            self.draw_func()

    def show(self):
        self.visible = True

    def hide(self):
        #self.text_box.sounds["activate_beep"].play()
        self.visible = False

class text_box(basic_text_box):

    def __init__(self, pos):
        basic_text_box.__init__(self, pos, "text_box")
        self.pages_to_render = []
        self.new = True
 
    def show(self):
        this.text_box_visible = True
        basic_text_box.show(self)

    def hide(self):
        this.text_box_visible = False
        basic_text_box.hide(self)

    def activate(self, **kwargs):
        #self.border.sounds["activate_beep"].play()
        if len(self.pages_to_render) != 0:
            self.txt_data = self.pages_to_render.pop()
            if 'func' in sorted(kwargs):
                kwargs['func']()
            return True
        else:
            self.hide()

    def draw_func(self):
        basic_text_box.draw_func(self)
        basic_text_box.newline_draw_text(self, self.txt_data)

    def run(self):
        if self.new:
            self.activate()
            self.new = False
        if not this.text_menu_visible:
            while self.visible:
                pygame.event.pump()
                if pygame.event.wait().type == KEYDOWN:
                    self.activate()
              
   
    def say(self, text, **kwargs):
        if "[player_name]" in text:
            text = text.replace("[player_name]", this.onscreen_sprites["player"].player_name)

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

        self.show()
        self.run()

    def draw(self, surface):
        if not this.text_menu_visible:
            basic_text_box.draw(self, surface)

class text_menu(basic_text_box):

    def hide(self):
        this.text_menu_visible = False
        basic_text_box.hide(self)

    def show(self):
        this.text_menu_visible = True
        basic_text_box.show(self)
        self.run()

    def format(self):
        if self.end_formatting != '\n':
            self.text = self.word_wrap(self.text, self.font.name, self.font.size)

        self.render_text = self.page_wrap(self.text, self.font.name, self.font.size)

    def render(self):
        self.text = ""
        self.render_text = []

        for item_name in self.items.keys():
            self.text += "    " + item_name + self.end_formatting

        self.format()

    def __deselect(self):
        textlist = list(self.text)
        textlist[self.text.find('>')] = ' '
        self.text = list_to_str(textlist)
        self.selected = ""
        self.format()

    def find_page_number_of_item(self, item):
        for i in range(len(self.render_text)):
            if self.render_text[i].find(item):
                return i

    def select(self, index):
        # self.border.sounds["select_beep"].play()

        if self.selected != "":
            self.__deselect()

        self.selected_index = index % len(self.items.keys())

        self.selected = sorted(self.items.keys())[self.selected_index]

        textlist = list(self.text)

        textlist[re.search(r"\b" + self.selected + r"\b", self.text).start() - 2] = '>'

        self.text = list_to_str(textlist)

        self.page_number = self.find_page_number_of_item(self.selected)
        self.format()


    def __init__(self, items, pos, **kwargs):
        border = "text_menu"

        if 'border' in kwargs:
            border =  kwargs['border']

        basic_text_box.__init__(self, pos, border)#, sounds = ['select_beep', 'back_beep'])
        self.items = orderd_dict_from_dict(items)

        if 'font' in sorted(kwargs.keys()):
            self.font = kwargs['font']
        else:
            self.font = this.default_font

        if 'end_formatting' in sorted(kwargs.keys()):
            self.end_formatting = kwargs['end_formatting']
        else:
            self.end_formatting = '\n'

        self.render()

        self.selected = ""
        self.previous = None

        self.select(0)

        this.text_menus_to_draw.append(self)
        
    def select_next(self):
        self.select(self.selected_index + 1)

    def select_previous(self):
        self.select(self.selected_index - 1)

    def get_selected(self):
        return self.selected

    def activate(self, *args):
        if self.items.get(self.selected) is not None:
            print(self.items.get(self.selected))
            if self.items.get(self.selected).__class__.__name__ != 'dict':
                if self.items.get(self.selected) != "previous":
                    output = self.items.get(self.selected)(self.selected, *args)
                    if output == "previous":
                        self.previous_menu()
                    return output
                else:
                    self.previous_menu()
                    return "previous"
            else:
                self.previous = self.items
                self.items = self.items.get(self.selected)
                self.render()
        else:
            self.previous_menu()

    def previous_menu(self):
        #self.text_box.sounds["back_beep"].play()
        if self.previous is not None:
            self.items = self.previous
            self.previous = None
            self.render()
        else:
            self.hide()

    def draw_func(self):
        basic_text_box.draw_func(self)
        basic_text_box.newline_draw_text(self, text_data(self.render_text[self.page_number],
                                                        self.font.size, self.font.name))

    def run(self):
        while self.visible:
            event = pygame.event.wait() 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.select_previous()
                elif event.key == pygame.K_LEFT:
                    self.select_previous()
                elif event.key == pygame.K_RETURN:
                    self.activate()
                elif event.key == pygame.K_z:
                    self.activate()
                elif event.key == pygame.K_x:
                    self.previous_menu()
                elif event.key == pygame.K_RIGHT:
                    self.select_next()

buff = collections.namedtuple('buff', ['stat', 'name'])

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
        self.__losing_message = "..."
        if 'losing_message' in kwargs:
            self.__losing_message = kwargs['losing_message']

        self.save_vars += ['__moves', '__inventory', '__equipped', '__basestat', '__losing_message' ]

    def get_losing_message(self):
        return self.__losing_message

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
        self.__stats["enlightenment"] +=  self.__stats["determination"] / 4
        self.__stats["enlightenment"] *= random.randrange(0.2, 1.1)
        self.__stats["determination"] -= self.__damage_taken
    
    def say(self, text):
        this.textbox.say(text, font = self._imagename, speaker = self._imagename)

    def is_dead(self):
        stats = self.get_stats()
        return(stats["determination"] - self.__damage_taken <= 0 |
                self.persuasion > stats["determination"] + stats["focus"])
    
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

    def use_item(self, itemname):
        self.__stats_needs_update =  True

        for buff in self.__inventory[itemname]["buffs"]:
           self.basestat[buff] +=  self.__inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]

        if self.__inventory[itemname]["effect"] is not None:
            self.__inventory[itemname]["effect"]()

        if self.__inventory[itemname]["equipabble"]:
            self.equip(itemname)

        if  self.inventory[itemname]["consumable"]:
            self.remove_from_inventory(self.__inventory[itemname])

    def _stun(self, enemy_stats,  NumberOfTurns):
        enemy_attack = (enemy_stats["enlightenment"]/4) * random.randrange(0 , (0.5 + enemy_stats["focus"]/130))

        if self.get_stats()["wit"] >  enemy_attack:
            this.battlebox.say(self.battle_name+ " was stunned!")
            self.stunned = NumberOfTurns

    def is_hopeful(self):
        if self.get_stats()["hope"] > random.randrange(0, 500):
            return True
        else:
            return False

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

        self.__stats_needs_update = True

def response_menu(items):
    responsebox = text_menu(items, position(0, 0), border = "text_box", end_formatting = '    ')
    responsebox.set_pos(position(0, this.window.get_height() - this.textbox.border.rect.height))
    responsebox.show()
    return responsebox

class NPC(entity):
    
    def __init__(self, name, pos, basestat, **kwargs):
        entity.__init__(self, name, pos, basestat, **kwargs)
        self.__dialog = {}
        self.__player_battle_won = None
        self.__repeat_dialog = {'...':''}
        if 'battle_name' in kwargs:
            self.battle_name = kwargs['battle_name']
        else:
            self.battle_name = self._imagename
        self.save_vars += ['__dialog', '__repeat_dialog' ]

    def load_save_data(self, data):
        self.__dict__.update(data)

    def save_data(self):
        self.pos = self.get_pos()
        return { "vars" : subset_dict_from_array(self.__dict__, self.save_vars),
                'classname' :  self.__class__.__name__ }

    def sell(self, item_to_sell):
        if this.onscreen_sprites["player"].get_inventory()["sterling"] >= self.item_to_buy["price"]:
            self.trade( item_to_sell, {"name": "sterling", "quantity": item_to_sell["price"]})
            this.onscreen_sprites["player"].trade({"name": "sterling", "quantity": item_to_sell["price"]},
                                                  item_to_sell)
            return True
        else:
            return False

    def _get_sell_menu_data(self):
        return self.get_iventory_menu_data(do_func=self.sell)
   
    def _get_dialog(self):
        get_setting_dict  = lambda dict: dict.getdefault(dict[this.settings.get_current_setting()], dict["default"])
        if self.player_battle_won:
            return get_setting_dict(self.__dialog["battle_lost"])
        elif not self.player_battle_won:
            return get_setting_dict(self.__dialog["battle_won"])
        else:
            return get_setting_dict(self.__dialog["no_battle"])

    def move_to(self, sprite_name):
        pos_to = this.onscreen_sprites[sprite_name].get_pos()
        pos_from = self.get_pos()
        self.move(pos_from.x - pos_to.x - 1, pos_from.y - pos_to.y - 1 )

    def parse_dialog(self, dialog):
        if dialog != "" | dialog is not None:
            if dialog.__class__.__name__ == 'dict':
                self.dialog_dict = dialog
                response_menu({ k : self.menu_dialog for k in dialog.keys()})
            if '_give_item' in dialog:
                this.onscreen_sprites["player"].add_to_inventory(re.match('_give_item (\w+)').group(1))
            elif '_give_move' in dialog:
                this.onscreen_sprites["player"].add_move(re.match('_give_move (\w+)').group(1))
            elif '_move_to' in dialog:
                self.move_to(re.match('_move_to (\w+)').group(1))
            elif '_move_player_to' in dialog:
                this.onscreen_sprites["player"].move_to(re.match('_move_to (\w+)').group(1))
            elif dialog == "_trade":
                text_menu(self._get_sell_menu_data, (0,0))
            elif dialog == "_attack_player":
                self._player_battle_won = battle(this.onscreen_sprites["player"], self)
            else:
                self.say(dialog)

    def menu_dialog(self, dialog):
        self.parse_dialog(self.dialog_dict[dialog])

    def activate(self):
        if len(sorted(self.__get_dialog.keys())) != 0:
            if sorted(self._get_dialog().keys()[0]) != "":
                self.say(sorted(self.__dialog.keys())[0])
            
            self.parse_dialog(self._get_dialog().pop())
        else:
            key = sorted(self.__repeat_dialog.keys()[0])
            self.say(key)
            self.parse_dialog(self.__repeat_dialog[key])

def menu_data(self, data_get, var):
    output = {}

    for data in data_get():
        output[data] = var

    return output
 
class Player(entity):

    def get_player_data(self):
        return self.__dict__

    def load_save_data(self, data):
        self.__dict__.update(data)

    def save_data(self):
        self.pos = self.get_pos()
        return { "vars" : subset_dict_from_array(self.__dict__, self.save_vars),
                'classname' :  self.__class__.__name__ }

    def get_equipped_menu_data(self):
        return menu_data(sorted(self.get_equipped().keys()), self.unequip)

    def get_stats_menu_data(self):
        output = {}

        for stat, val in self.get_stats():
            output[stat+"  =  "+val] = None 

        return output

    def is_sure_dialog(self, if_sure, **kwargs):
        dialog = "are you sure?"
        if 'dialog' in kwargs:
            dialog = kwargs['dialog']

        self.sure_dialogs.append({'dialog': dialog, 'if_sure': if_sure})

    def is_sure_dialog_hook(self, *args, **kwargs):
        if 'dialog' in kwargs:
            dialog = kwargs['dailog']
        else:
            dialog = self.sure_dialogs.pop()
        this.textbox.say(dialog)
        def sure(*args):
            this.text_box.next_page()
            this.text_box.hide()
            return dialog["if_sure"]()

        return response_menu({
            "yep": sure,
            "nope": "previous"
        })

    def save_dialog(self, *args):
        return self.is_sure_dialog_hook(dialog = {'if_sure': this.save_data, 'dialog': 'do you really want to save and quit?'})

    def item_description_menu(self, itemname):
            self.is_sure_dialog(self.use_item, dialog = 'it says "' + self.__inventory[itemname]["description"] + '" eat it?"') 

    def get_inventory_menu_data(self):
               return menu_data(sorted(self.get_inventory().keys()), self.item_description_menu)


    def get_player_menu_items(self):
        return {
                    "inventory" : self.get_inventory_menu_data,
                    "equipped" : self.get_equipped_menu_data,
                    "stats" : self.get_stats_menu_data,
                    "save and quit" : self.save_dialog
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
                }, losing_message = "you lost...")#, sounds = ["activate_beep"] )

        self.sure_dialogs = []

        self.player_menu = text_menu(self.get_player_menu_items(), position(0,0))
        self.player_name = name
        this.player_name = name
        self.battle_name = this.player_name
        self.save_vars.append('player_name')
        #self.run()
    
    def move(self, dx, dy):
        return moveable.move(self, dx, dy, this.background.scroll)

    def activate_sprite(self, sprite):
        #self.sounds['activate_beep'].play()
        if sprite.__class__.__name__ == "item":
             self.add_to_inventory(sprite.item_data)
             this.text_box("picked up some "+ sprite.item_data["name"])
             del sprite
        else:
            sprite.activate()

    def activate(self):
        rect = self.get_rect()
        for sprite in this.onscreen_sprites:
            rect1 = sprite.get_rect()
            if (self.facing == "forward" & rect1.y + 3 >= rect.y |
                    self.facing == "backward" & rect1.y - 3 <= rect.y |
                    self.facing == "left" & rect1.x + 3 >= rect.x |
                    self.facing == "right" & rect1.x -3 <= rect.x ):
                self.activate_sprite()
            #else:
                #self.sounds['collide_beep'].play()

    def get_pos(self):
        rect = self.get_rect()
        return position(rect.x, rect.y)

    def get_menu(self):
        return self.menu

    def update(self, *args):
        self.player_menu.draw(this.window)
        entity.update(self, *args)

    def run(self):
        while not(this.text_box.visible | this.player_menu.visible | this.inbattle):
            pygame.event.pump()
            event = pygame.event.wait()
            if event.type == KEYDOWN:
                if event.key == pygame.K_x:
                    this.player_menu.show()
                elif event.key == pygame.K_z:
                    self.activate()
                elif event.key == pygame.K_UP:
                    self.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    self.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    self.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move(1, 0)

class battle_player():

    def __init__(self, entity, enemy):
        self._entity = entity
        self.__func_queue = []
        self.enemy = enemy

    def use_item(self, itemname):
        self.__func_queue.append({"func" : self._entity.use_item, "args" : itemname})

    def use_move(self, movename):
        self.__func_queue.append({"func" : self._entity.use_move, "args" : [movename, self.enemy]})

    def do_queued(self):
        function = self.__func_queue.pop()
        out = function["func"](*function["args"])
        self._entity.next_turn()
        return out

    def ready(self):
        return len(self.__func_queue) > 0

    def get_stats(self):
        return self._entity.get_stats()

    def get_losing_message(self):
        return self._entity.get_losing_message()

    def get_item_menu_data(self):
        return menu_data(sorted(self._entity.get_inventory().keys()), self.use_item)
    
    def get_move_is_sure_disc(self, movename):
        self._entity.is_sure_dialog(self.use_move, dialog = self._entity.get_moves()["discription"] + '". do you want to use this move? "')
    
    def get_move_menu_data(self):
        return menu_data(self._entity.get_moves, self.get_move_is_sure_disc)

    def get_battle_menu(self):
        return response_menu({
                    "idealogies" : self.get_move_menu_data,
                    "items" : self.get_item_menu_data
                })


class battle_NPC(sprite):

    def __init__(self, entity, pos):
        self._entity = entity
        self.sprite.__init__(self, entity.get_imagename() + "_battle", pos, battle = True)

    def __del__(self):
        pass

    def do_attack(self):
        stats = self.get_stats()
        if stats["determination"] < 25:
            health_items = {}
            if len(self.entity.get_inventory()) != 0:
                    for item in self._entity.get_inventory():
                        if item["type"] == "health":
                            health_items[item["potency"]] = item["name"]
                    self._entity.use_item(health_items[sorted(health_items.keys())[-1]])
        else:
            moves = self._entity.get_moves()
            self._entity.use_move(moves[random.randrange(len(moves))], this.onscreen_sprites["player"])
            
    def get_losing_message(self):
        return self._entity.get_losing_message()
               
class battle(threading.Thread):

    def __init__(self, player, npc):
        threading.Thread.__init__(self)
        this.battle_npc = battle_NPC(npc, (0,0))
        self.player = battle_player(player, npc)

        calc_pos = lambda winx, objx: winx/2 - objx/2
        self.npc.set_pos(position((calc_pos(this.window.get_width(),
                self.npc.rect.right),
                    calc_pos(this.window.get_height(), self.npc.rect.bottom))))
    
        if self.player.get_stats["speed"] > self.npc.get_stats["speed"]:
            self.__player_turn= True
        else:
            self.__player_turn= False

        this.set_background("battle")   
        self.start()
    
    def get_player(self):
        return self.player

    def get_npc(self):
        return this.battle_npc

    def battle_end(self):
        if this.battle_npc.is_dead()| self.player.is_dead():
            def transfer_inventory(e1, e2):
                for item in e2._entity.get_inventory(): e1.add_to_inventory(item)

            if this.battle_npc.is_dead():
                 transfer_inventory(self.player, this.battle_npc)
                 this.battle.box.say(this.battle_npc.get_losing_message())
            else:
                 transfer_inventory(this.battle_npc, self.player)
                 this.battle.box.say(self.player.get_losing_message())
            self.terminate()
            this.inbattle = False
            del this.battle_npc
            self.__del__()
            return True
        return False

    def run(self):
        if not self.battle_end(): 
            if  self.__player_turn & self.player.ready():
                this.battlebox.say("PLAYER HEALTH: " + str(self.player.get_stats()["determination"]))
                self.player.get_battle_menu()
                self.player.do_queued()
            elif not self.__player_turn:
                self.npc.do_attack()
def update():
    while True:
        pygame.event.pump()
        if not this.inbattle:
            this.onscreen_sprites.clear(this.window, this.background)
            this.onscreen_sprites.update()
            this.onscreen_sprites.draw(this.window)
            this.textbox.draw(this.window)
            if this.background is not None:
                window.blit(this.background, (0,0))
            for menu in this.text_menus_to_draw:
                menu.draw(this.window)
        else:
            this.window.blit(this.battle_npc)
            this.battlebox.draw(this.window)
        pygame.display.flip()

def save_data():
   json.dumps({
       "sprites":this.data_sprites,
       "setting":this.settings.get_current_setting()
    })

def start_screen():

    this.textbox.say("""Press ANY key.""")
    this.textbox.say("""thank you for accepting our not so binding agreement for you to play this game.""")

    this.textbox.say("""hello. Welcome to the world of Earth(R) 
You need a name, due to budget cuts from the education system
we can only give you a few, choose well!
with the power of the arrow keys to select and the z key to confirm!""")
    this.textbox.hide()
    response_menu({"bob": None, "bobett": None, "bobafett": None})
    this.textbox.activate()
    this.textbox.show()
    this.textbox.say("great Choice! ...")

    this.textbox.say("STOP! POLITICAL CORRECTNESS POLICE IS HERE TO GIVE JUSTICE!")
    this.textbox.say("Nooooooo! please Nooo.")
    this.textbox.say("""YOU HAVE BEEN SECTIONED ON RESTRICTING HUMAN EXPRESSION.
CHOOSE YOUR NAME BEFORE HE STARTS WRITING YOU DESTINY.
PRESS ENTER ONCE YOU HAVE COMPLETED YOUR NAME.""")
    key = ""
    name = ""
    while key != "return":
       event = pygame.event.wait()
       if event.type == pygame.KEYDOWN:
           key = pygame.key.name(event.key)
           if key == "return":
               break
           name += key
           this.textbox.say(name)

    this.textbox.say("oh so your name is " + name + ". I guess we could use that.")

    this.onscreen_sprites.add("player", Player(name, position(this.window.get_width()/2,this.window.get_height()/2)))

    this.settings.load("overworld")

    this.textbox.say("""ERM... HERE ILL HELP YOU UP, CALL ME RICHARD.
USE YOU'RE ARROW KEYS TO MOVE,
X TO OPEN THE MENU AND THE Z TO ACTIVATE THINGS
WHATEVER THAT MEANS. 
WEIRD THAT YOU CAME WITH AN OPERATION MANUAL""", speaker = "Poor Richard")

    this.textbox.say("""ha.. just kidding! you're the new guy who just moved in, 
well yours is the one right in front of you, have a nice day!""", speaker = "Poor Richard")

    this.textbox.hide()

def __init__():
    this.text_menu_visible = False
    this.text_box_visible= False
    this.inbattle = False
    this.player_name = "player"

    this.window = pygame.display.set_mode([640, 480])
 
    this.data = game_data.game_data("data")
    this.fonts = game_data.font_data(os.path.join("data", "fonts"))

    this.default_font = font_data(16, "default")

    try:
        this.sprite_classes_args = json.load(open("sprite_classes_args.json"))
        this.settings = settings(json.load(open("settings.json")))
    except(OSError, IOError):
        print("cannot find the sprite_classes_args.json or settings.json file, Exiting.")
        sys.exit(404)

    this.textbox = text_box(position(0 , 0))
    this.textbox.set_pos(position(0, this.window.get_height() - this.textbox.border.rect.height))

    this.battlebox = text_box(position(0 , 0))
    this.battlebox.set_pos(position(0, this.window.get_height() - this.textbox.border.rect.bottom))

    this.data_sprites = {}
    this.onscreen_sprites = LayeredDirtyDict()
    this.text_menus_to_draw = []

    #pygame.mixer.init()
    #this.background_music = pygame.mixer.Channel(0)
    this.background = None
    this.draw_process = threading.Thread(target=update).start()
    try:
      data = json.load(open("save.json"))
    except (OSError, IOError, FileNotFoundError):
        try:
            this.items = object_loader.load_objects("items.json")
            this.moves = object_loader.load_objects("moves.json")
        except (OSError, IOError, FileNotFoundError):
            print("cannot load items.json or moves.json, Fatal Error. Exiting")
            sys.exit(404)

        for sprite in json.load(open("npcs.json")):
           this.data_sprites[sprite["name"]] =  {
                "classname":"NPC",
                "vars" : {
                    "_imagename": sprite["name"],
                    "__inventory" : subset_dict_from_array(this.items, sprite["items"]),
                    "__equipped" : subset_dict_from_array(this.items, sprite["equipped"]),
                    "__moves" : subset_dict_from_array(this.moves, sprite["moves"]),
                    "__dialog" : sprite["dialog"],
                    "__repeat_dialog": sprite["repeat_dialog"],
                    "__basestat" : sprite["stats"],
                    "losing_message": sprite["losing_message"]
                }
            }

        for sprite in json.load(open("sprites.json")):
                this.data_sprites[sprite['name']] = { 'classname': sprite["classname"], 'vars': sprite }

        start_screen()
    else:
            this.data_sprites = data["sprites"]
            this.settings.load(data["setting"])

if __name__ == '__main__':
    __init__()
