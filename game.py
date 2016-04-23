#!/usr/bin/env python3

import multiprocessing, random, time, collections, sys, json, pygame, os
import object_loader, data

#(0, 0) is top left corner in pygame.

this = sys.modules[__name__]

position = collections.namedtuple("position", ['x', 'y'])

def subset_dict_from_array(dict1, array):
    return { k : dict1[k] for k in dict1.keys & array } 

def merge_arrays_to_dict(key_array, var_array):
    return { k : v for k in key_array for v in var_array }

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

    def __getitem__(self, key):
        return _get_dict()[key]

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
    self.background_music.play(this.data.sounds.get_data(name))

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

        self.save_vars = [ '_imagename', 'pos' ]

    def get_rect(self):
        return self.image.get_rect()

    def get_pos(self):
        return position(self.rect.x, self.rect.y)

    def save_data(self):
        self.pos = self.get_pos()
        return { "vars" : subset_dict_from_array(self.__dict__, self.save_vars), 
                'classname' :  self.__class__.__name__ }

    def __del__(self):
        if self.__class__.__name__ not in this.sprite_class_args:
            this.sprite_class_args[self.__class__.__name__] = self.class_arg_data()

        this.data_sprites[self._imagename] = self.save_data()
    
    def load_save_data(self, data):
        self.__dict__.update(data["vars"])

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
        this.setting.set_zone(setting_to)
        s_from = self.setting_from 
        self.setting_from = self.setting_to
        self.setting_to = s_from 

class item(sprite):

    def __init__(pos, item_data, **kwargs):
        sprite.__init__(self, "dropped_item", pos)
        self.item_data = item_data
        self.save_vars += [ 'item_data', 'setting_from' ] 

class settings:
    
    def __init__(self, settings_dict_data):
        self.settings  = settings_dict_data

    def load_data_sprite(sprite):
        def get_data_args(sprite, argtype):
                args = subset_dict_from_array(sprite["vars"], 
                    this.sprite_class_args[sprite["classname"]]["argtype"]).values()
                for arg in args:
                    sprite.pop(arg)
                return sorted(args)
                
        args = get_data_args(sprite, "args")
        kwargs = get_data_args(sprite, "kwargs")
        sprite = eval(sprite["classname"]+"(*args, **kwargs)")
        sprite.load_save_data(sprite["vars"])
        return sprite

    def load(setting_name):
        this.onscreen_sprites.empty()
        this.onscreen_sprites.update({ k : self.load_data_sprite(this.data_sprites[k]) 
                                        for k in self.settings[setting_name]["sprites_used"]})
                                        
        this.set_background(setting_name)

        for key in self.settings[setting_name]["doors"].keys():
            Door = door(self.settings[setting_name]["doors"][door_keys[i]]["pos"], 
                    setting_name, door_keys[i])
            this.onscreen_sprites.add("door_" + str(i))


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
        if this.background.get_rect.collidepoint(rect.x+dx, rect.y+dy):

            for sprite in this.onscreen_sprites:
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
            self.__frame = self.__frame%len(self.animation[direction])
            self.moving = False


class basic_text_box(multiprocessing.Process):

    def __init__(self, pos, border, **kwargs):
        multiprocessing.Process.__init__(self)
        sounds = ['activate_beep']

        self.border = sprite(border, pos, sounds = sounds)
        this.sprites.remove(self.border._imagename)
        self.rect = self.border.get_rect()

        if 'sounds' in sorted(kwargs.keys()):
            sounds += kwargs['sounds']

        self.text_box = pygame.Sprite()
        self.text_box.image = pygame.Surface([self.rect.x - 2, self.rect.y - 2])
        self.text_box.rect = self.text_box.image.get_rect()
        self.text_box.image.fill(0)
        self.text_box.rect.x = pos.x - 2
        self.text_box.rect.y = pos.y -2

        self.visible = False

    def set_pos(self, pos):
        self.border.rect.x = pos.x
        self.border.rect.y = pos.y
        self.text_box.rect.x = pos.x - 2
        self.text_box.rect.y = pos.y - 2

    def get_pos(self):
        return position(self.border.rect.x, self.border.rect.y)

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
        self.start()

    def hide(self):
        self.text_box.sounds["activate_beep"].play()
        self.visible = False
        self.terminate()

class text_box(basic_text_box):

    def __init__(self, pos):
        basic_text_box.__init__(self, pos, "text_box")
        self.pages_to_render = multiprocessing.Queue()

    def activate(self, **kwargs):
        self.border.sounds["activate_beep"].play()
        if len(pages_to_render) > 0:
            self.txt_data = self.pages_to_render.get()
            if 'func' in sorted(kwargs):
                kwargs['func']()
            return True
        else:
            self.hide()

    def draw_func(self, surface):
          this.fonts.get_data(self.txt_data.font_name).render_to(self.text_box,
                  (0, 0), self.txt_data.text, size = self.txt_data.font_size)

    def run(self):
        if not this.text_menu.visible:
            pygame.event.pump()
            if pygame.event.wait() == pygame.KEYDOWN: 
                self.activate()

    def say(self, text, **kwargs):
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
            self.pages_to_render.put(text_data(page, font.size, font.name))

        self.activate()
        self.show()

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
        if self.items[self.selected] != None:
            if self.items[self.selected].__class__.__name__ != 'dict':
                if self.items[self.selected] != "previous":
                    output = self.items[self.selected](selected, *args)
                    if output == "previous":
                        self.previous_menu()
                    return output
                else:
                    self.previous_menu()
                    return "previous"
            else:
                self.previous = self.items
                self.items = self.items[self.selected]
                self.render()   

    def previous_menu(self):
        self.text_box.sounds["back_beep"].play()
        if self.previous != None:
            self.items = self.previous
            self.previous = None
            self.render()
        else:
            self.terminate()
            self.hide()

    def draw_func(self, surface):
        this.fonts.get_data(self.font.name).render_to(self.text_box,
                (0, 0), self.render_text[self.page_number], size = self.font.size)

    def run(self):
        pygame.event.pump()
        event = pygame.event.wait() 
        if event == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN | event.key == pygame.K_LEFT:
                self.select_previous()
            elif event.key == pygame.K_RETURN | event.key == pygame.K_z:
                self.activate()
            elif event.key == pygame.K_x:
                self.previous_menu()
            else:
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
        self.__dying_message = "..."
        if 'dying_message' in kwargs:
            self.__dying_message = kwargs['dying_message']

        self.save_vars += ['__moves', '__inventory', '__equipped', '__basestat', '__dying_message' ]
        self.arg_vars = [ '_imagename', 'pos', '__basestat' ]
        self.kwarg_vars = ['__dying_message']

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
        this.textbox.say(response, font = self._imagename, speaker = self._imagename)

    def is_dead(self):
        stats = self.get_stats()
        return (stats["determination"] - self.__damage_taken <= 0 |
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

    def buy(self, item_to_buy):
        if self.__inventory["sterling"] >= self.item_to_buy["price"]:
            self.add_to_inventory(item_to_buy)
            self.remove_from_inventory({"name": "sterling", "quantity": item_to_buy["price"]})
            return True
        else:
            return False

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

        if self.__inventory[itemname][effect] != None:
            self.__inventory[itemname][effect]()

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
    responsebox = text_menu(items, (0, 0), border = "text_box", end_formatting = '')
    responsebox.set_pos(0, this.window.get_height() - this.textbox.border.rect.y )
    responsebox.show()
    return responsebox

class NPC(entity):
    
    def __init__(self, name, pos, basestat, **kwargs):
        entity.__init__(self, name, pos, basestat, **kwargs)
        self.__dialog = {}
        self.__func_dialog = {}
        self.save_vars.append('__dialog', '__func_dialog')
        self.args_vars = ['_imagename', 'pos', '__basestat']
        if 'battle_name' in kwargs:
            self.battle_name = kwargs['battle_name']
        else:
            self.battle_name = self._imagename
        
    def activate(self):
        if self.__dialog.keys()[0] != "":
            self.say(self.__dialog.keys()[0])

        response = response_menu(self.__dialog.pop())
        if response.__class__.__name__ == "dict":
            #dicts are only used in trading items.
            self.say(self.__func_dialog["trade"][this.onscreen_sprites["player"].buy(response)])
        elif response == "_attack_player":
            this.Battle = battle(this.onscreen_sprites["player"], self)
        else:
            self.speak(response)

def menu_data(self, data_get, var):
    output = {}

    for data in data_get():
        output[data] = var

    return output
 
class player(entity, multiprocessing.Process):

    def get_inventory_menu_data(self):
        return menu_data(sorted(self.get_inventory().keys()), self.use_item)

    def get_equipped_menu_data(self):
        return menu_data(sorted(self.get_equipped().keys()), self.unequip)

    def get_stats_menu_data(self):
        output = {}

        for stat, val in self.get_stats():
            output[stat+"  =  "+val] = None 

        return output
   
    def is_sure_dialog(self, if_sure):
        this.textbox.say("are you sure?", self.font.name, self.font.size) 

        def sure(*args):
            this.text_box.next_page()
            this.text_box.hide()
            return if_sure()

        return {
                    "yep" : sure, 
                    "nope": "previous"
               }
    
    def get_player_menu_items(self, game):
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
                }, sounds = ['activate_beep'])

        this.player_menu = text_menu(self.get_player_menu_items()) 
        self.player_name = name
        self.battle_name = self.player_name
        self.save_vars.append('player_name')
        self.args = [ 'player_name', 'pos' ] 
    
    def move(self, dx, dy):
        moveable.move(self, dx, dy)
        return moveable.move(self, dx, dy, this.background.scroll)

    def activate_sprite(self, sprite):
        self.sounds['activate_beep'].play()
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
            else:
                self.sounds['collide_beep'].play()

    def get_pos(self):
        rect = self.get_rect()
        return position(rect.x, rect.y)

    def get_menu(self):
        return self.menu
    
    def run():
        if not(this.text_box.visible | this.player_menu.visible | this.inbattle):
            pygame.event.pump()
            event = pygame.event.wait()
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


def get_trade_menu(buyer, seller):
    return text_menu({
            "buy": seller.get_inventory,
            "sell": buyer.get_inventory
        }, (0, 0)) 

class battle_entity():

    def __init__(self, entity):
        self._entity = entity
        self.__func_queue = []

    def use_item(self, itemname):
        self.__func_queue.append({"func" : self._entity.use_item, "args" : itemname})

    def use_move(self, movename):
        self.__func_queue.append({"func" : self._entity.use_move, "args" : [movename, self.enemy]})

    def do_queued(self):
        function = self.__func_queue.pop()
        out = function["func"](*funtction["args"])
        self._entity.next_turn()
        return out

    def ready(self):
        return len(self.__func_queue) > 0

    def get_stats(self):
        return self._entity.get_stats()


class battle_player(battle_entity):

    def __init__(self, entity, enemy):
        battle_entity.__init__(self, entity)
        self.enemy = enemy

    def get_item_menu_data(self):
        return menu_data(sorted(self._entity.get_inventory().keys()), self.use_item)
    
    def get_move_menu_data(self):
        return self.menu_data(self._entity.get_moves, self.use_move)

    def get_battle_menu(self):
        return response_menu({
                    "idealogies" : self.get_move_menu_data,
                    "items" : self.get_item_menu_data
                })

class battle_NPC(battle_entity):

    def __init__(self, entity, pos):
        battle_entity.__init__(self, entity)
        self.battle_sprite = sprite(entity.get_imagename() + "_battle", pos, battle = True)
        self.enemy = this.sprites["player"]

    def get_what_do_next(self):
        stats = self.get_stats()

        if stats["determination"] < 25:
            health_items = {}
            if len(self.entity.get_inventory()) != 0:
                    for item in self._entity.get_inventory():
                        if item["type"] == "health":
                            health_items[item["potency"]] = item["name"]
                    self.entity.use_item(health_items[sorted(health_items.keys())[-1]])
        else:
            moves = self._entity.get_moves()
            self._entity.use_move(moves[random.randrange(len(moves))], this.sprite["player"])
               
class battle(multiprocessing.Process):

    def __init__(self, player, npc):
        multiprocessing.Process.__init__(self)
        self.npc = battle_NPC(npc, (0,0))
        self.player = battle_entity(player, npc)

        calc_pos = lambda winx, objx: winx/2 - objx/2
        self.npc.set_pos((clac_pos(this.window.get_width(), 
                self.npc.rect.right),
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
            for item in self.npc._entity.get_inventory():
                self.player._entity.add_to_inventory(item)
            this.inbattle = False
            self.terminate()
        return False

    def run(self):
        if not self.battle_end(): 
            if  self.__player_turn & self.player.ready():
                self.player.do_queued()
            elif not self.__player_turn & self.npc.ready():
                self.npc.get_what_do_next()
                self.npc.do_queued()
def update():
    this.onscreen_sprites.clear(this.background)
    this.onscreen_sprites.update(this.data)
    this.onscreen_sprites.draw(this.window)

    if not this.inbattle:
        this.textbox.draw(this.window)
        this.player_menu.draw(this.window)
    else:
        this.battlebox.draw(this.window)

    pygame.display.update()

def save_data():
   return json.dumps(this.data_sprites)

def start_screen():
    this.text_box.say("""Press ANY key.""")
    this.text_box.say(""" thank you for accepting our not so binding agreement for you to play this game.
                            here is now a BIG DISCLAMER that this game is SATIRE and is a GAME(DUN-DUN-DUN!).""")

    this.text_box.say("""hello. Welcome to the world of Earth(R) 
                        You need a name, due to budjet cuts from the education system 
                        we can only give you a few, choose well!""")


    this.response_menu({"bob":None, "bob": None, "bob": None })
    this.text_box.say("great Choice! ...")

    this.text_box.say("STOP! POLITICAL CORRECTNESS POLICE IS HERE TO GIVE JUSTICE!", speaker = "???")
    this.text_box.say("Nooooooo! please Nooo.", speaker = "narrator")
    this.text_box.say("""YOU HAVE BEEN SECTIONED ON RESTRICTING HUMAN EXPRESSION.
                        CHOOSE YOUR NAME BEFORE HE STARTS WRITING YOU DESTINY.
                        PRESS ENTER ONCE YOU HAVE COMPLTED YOUR NAME.""",
                        speaker = "POLITICAL CORRECNTESS POLICE")
    key = ""
    name = ""
    while key != "return":
       key = pygame.event.wait(KEYDOWN).name()
       name += key
       this.text_box.say(name)

    this.text_box.say("oh so your name is " + name + ". I guess we could use that.", 
            speaker = "narrator")

    this.settings.load("start")
    
    this.onscreen_sprites.add("player", Player(name, (0,0)))

    this.text_box.say("""ERM... HERE ILL HELP YOU UP, CALL ME RICHARD.
                        USE YOU'RE ARROW KEYS TO MOVE,
                        X TO OPEN THE MENU AND THE Z TO ACTIVATE THINGS
                        WHATEVER THAT MEANS. 
                        WEIRD THAT YOU CAME WITH AN OPERATION MANUAL""", speaker = "Richard")
def init():

    try:
        this.data = data.game_data("data")
        this.fonts = data.font_data(os.path.join("data", "fonts"))
    finally:
        print("cannot find resources, check data paths exist.")
        sys.exit(404)

    this.textbox = text_box((0 , 0))
    this.textbox.set_pos(0, this.window.get_height() - this.textbox.border.rect.y)

    this.battlebox = text_box((0 , 0))
    this.battlebox.set_pos(0, this.window.get_height() - this.textbox.border.rect.bottom)

    this.data_sprites = {}
    this.onscreen_sprites = LayeredDirtyDict()

    this.background_music = pygame.mixer.Channel(0)
    this.background = None

    try:
        this.sprite_classes_args = json.load(open("sprite_classes_args.json"))
    finally:
        print("cannot find the sprite_classes_args.json file, Exiting.")
        sys.exit(404)

    try:
        this.data_sprites = json.load(open("save.json"))
    except (OSError, IOError):
        try:
            items = object_loader.load_objects("items.json")
            moves = object_loader.load_objects("moves.json")
            settings = settings(json.load(open("settings.json")))
        except (OSError, IOError):
            print("cannot load object.json or settings.json, Fatal Error. Exiting")
            sys.exit(404)

        for sprite in json.load(open("npcs.json")):
           this.data_sprites[sprite["name"]] =  {
                "classname":"NPC",
                "vars" : {
                    "__inventory" : subset_dict_from_array(this.items, sprite.items),
                    "__equipped" : subset_dict_from_array(this.items, sprite.items),
                    "__moves" : subset_dict_from_array(this.moves, sprite.moves),
                    "__dialog" : sprite["dialog"],
                    "__func_dialog" : sprite["func_dialog"],
                    "__baststat" : sprite["stats"],
                    "pos" : sprite["pos"],
                    "_imagename": sprite["name"]
                }
            }  
       
        for classname, sprites in json.load(open("sprites.json")):
            for name, sprite in sprites:
                sprite['name'] = name
                this.data_sprites[sprite['name']] = { 'classname': classname, 'vars': sprite }

    this.window = pygame.display.set_mode([680, 480])
