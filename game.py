#!/usr/bin/env python3

# sound loading has been commented out as i had no time for sounds.

# we import everything we need  object_loader and game_data refer to thier files
import threading, random, collections, sys, json, pygame, os, re, copy
import object_loader, game_data
from pygame.locals import *

# (0, 0) is top left corner in pygame.

# module referance, used as a namespace to acsess variables nomatter the scope in the module
this = sys.modules[__name__]

# stores position x and y values
position = collections.namedtuple("position", ['x', 'y'])


def subset_dict_from_array(dict1, array):
    return {k: dict1[k] for k in array}


# creates an ordered subset using orderedDict, as dicts are not ordered
def ordered_subset_dict_from_array(dict1, array):
    out_dict = collections.OrderedDict()
    for k in array:
        out_dict[k] = dict1[k]
    return out_dict


def orderd_dict_from_dict(dict):
    out = collections.OrderedDict()
    for k in list(dict.keys()):
        out[k] = dict[k]
    return out


# logical and operation for an array
def array_and(array, array1):
    out = []
    for i in array:
        for v in array1:
            if v == i:
                out.append(v)
    return out


def merge_arrays_to_dict(key_array, var_array):
    return {k: v for k in key_array for v in var_array}


# converts an arrays 0th and 1st element into a pos tuple
def array_to_pos(array):
    return position(array[0], array[1])


# converts a list to a str, doing this cast wise gives bad output
def list_to_str(list):
    out = ""
    for char in list:
        out += char
    return out


# customized dictionary for holding sprites
class SpriteDict(collections.UserDict):
    def __init__(self, *args, **kwargs):
        collections.UserDict.__init__(self, *args, **kwargs)

    # draw the sprites in the dict
    def draw(self, surface):
        for k in self.data:
            surface.blit(self.data[k].image, self.data[k].rect)

            # run update function on all the sprites in the dict

    def update(self, *args):
        for k in self.data:
            self.data[k].update(*args)

        # add a sprite

    def add(self, key, var):
        self.data[key] = var

    # update the dictionary with sprites
    def update_dict(self, *args, **kwargs):
        collections.UserDict.update(self, *args, **kwargs)


def set_background(name):
    this.background = this.data.backgrounds.get_data(name)
    # self.background_music.play(this.data.sounds.get_data(name))


class sprite(pygame.sprite.DirtySprite):
    def __init__(self, imagename, pos):
        pygame.sprite.DirtySprite.__init__(self)
        # self.sounds = []

        # if 'sounds' in sorted(kwargs.keys()):
        #    self.sounds = this.data.sounds.get_data_dict(kwargs['sounds'])
        #    self.sound_names = kwargs['sounds']
        # else:
        #    self.sound_names = []

        self._imagename = imagename

        # load the image
        self.image = this.data.sprites.get_data(self._imagename)
        self.rect = self.image.get_rect()
        self.rect.x = pos.x
        self.rect.y = pos.y

    def get_rect(self):
        return self.rect

    def get_pos(self):
        return position(self.rect.x, self.rect.y)

    def get_imagename(self):
        return self._imagename

    # set position of sprite
    def set_pos(self, pos):
        self.rect.x = pos.x
        self.rect.y = pos.y

    """  was going to be used; now nolonger.
       def save_data(self):
          self.pos = self.get_pos()
          return {"vars": subset_dict_from_array(self.__dict__, self.save_vars),
               'classname': self.__class__.__name__}"""

    # updates classes attributes from a dict
    def load_save_data(self, data):
        self.__dict__.update(data)

    # function that all sprites will have, there to be overiddern
    def activate(self):
        pass


class door(sprite):
    def __init__(self, pos, setting_to, **kwargs):
        imagename = "door"
        if 'imagename' in sorted(kwargs.keys()):
            imagename = kwargs['imagename']

        sprite.__init__(self, imagename, pos)  # , sounds = ['door_open'])
        self.setting_to = setting_to

    def load_save_data(self, data):
        self.__dict__.update(data)

    def activate(self):
        # self.sounds['door_open'].play()

        setting_from = this.settings.get_current_setting()

        # load the new setting stored by the door
        this.settings.load(self.setting_to)

        if self.setting_to == "overworld":
            rect = this.onscreen_sprites["door_to_" + setting_from].rect.copy()
            this.onscreen_sprites["player"].set_pos(rect.move(rect.width/2, rect.height + 1))

# convenience class for onscreen pick up-able items
class item(sprite):
    def __init__(self, pos, item_data, **kwargs):
        sprite.__init__(self, "dropped_item", pos)
        self.item_data = item_data

    def load_save_data(self, data):
        self.__dict__.update(data)


# loads backgrounds and sprites fomr dict
class settings:
    def __init__(self, settings_dict):
        self.settings = settings_dict
        self.__current_setting = ""

    def load_data_sprite(self, sprite_data):
        # closure to get args of the class we are going to init
        def get_data_args(data, argtype):
            args = ordered_subset_dict_from_array(data["vars"],
                                                  this.sprite_classes_args[data["classname"]][argtype])
            for arg in args:
                # pos is a tuple, not an array as it is defined in the dicts
                # so we change it to a tuple
                if arg == "pos":
                    args[arg] = array_to_pos(args[arg])
                # we remove that arg so it does not get overwrittern by load_save_data
                data["vars"].pop(arg)
            return args

        # we don't want to edit the sprite_data, annoying as this should a copy in C++
        # not a pointer. and as i have came from C++ expected python to follow this rule also.
        data = copy.deepcopy(sprite_data)

        # get *args of class
        args = list(get_data_args(data, "args").values())
        # get **kwargs
        kwargs = get_data_args(data, "kwargs")

        # interpite arg string, creating the class with no need of using an if statment for classname
        Sprite = eval(sprite_data["classname"] + "(*args, **kwargs)")

        # load the rest of the values defined in the json by the fun below
        Sprite.load_save_data(sprite_data["vars"])
        return Sprite

    def load(self, setting_name):
        # stop the thread so we have no errs.
        this.drawing = False
        this.draw_thread.join()

        # wait for all event loops to fin
        pygame.time.delay(5)

        sprites_used = copy.deepcopy(self.settings[setting_name]["sprites_used"])

        # find if a sprite which is going to be used is used currently, if so update its position to the new one
        # and remove it from the sprites used dict
        for sprite_key in sorted(this.onscreen_sprites.keys()):
            if sprite_key in sprites_used:
                this.onscreen_sprites[sprite_key].set_pos(array_to_pos(sprites_used[sprite_key]))
                sprites_used.pop(sprite_key)
            else:
                this.onscreen_sprites.pop(sprite_key)

        # load the rest of the sprites
        for Sprite in sprites_used:
            this.data_sprites[Sprite]["vars"]["pos"] = array_to_pos(sprites_used[Sprite])

        # update the on screen sprites dict
        this.onscreen_sprites.update_dict({k: self.load_data_sprite(this.data_sprites[k])
                                           for k in sprites_used})

        # set the background
        this.set_background(setting_name)

        # iterate over doors, if they do not have an imagename make thier imagename door
        for k in self.settings[setting_name]["doors"]:
            if self.settings[setting_name]["doors"][k]["imagename"] == "":
                self.settings[setting_name]["doors"][k]["imagename"] = "door"

            # load the iter door
            door_sprite = door(array_to_pos(self.settings[setting_name]["doors"][k]["pos"]),
                        k, imagename=self.settings[setting_name]["doors"][k]["imagename"])
            # add iter door
            this.onscreen_sprites.add("door_to_" + k, door_sprite)

        # set the current setting
        self.__current_setting = setting_name

        # restart the thread
        this.drawing = True
        this.draw_thread = threading.Thread(target=update)
        this.draw_thread.start()

    def get_current_setting(self):
        return self.__current_setting


class moveable(sprite):
    def __init__(self, imagename, pos, **kwargs):
        #  sounds = ["collide_beep"]
        #     if 'sounds' in sorted(kwargs.keys()):
        #        sounds += kwargs['sounds']

        sprite.__init__(self, imagename, pos)

        # make an array of all directions needed to load
        directions = [
            "right",
            "forward",
            "backward"
        ]

        # get all the images used for animation and put them in a dict with
        # the direction as the key
        self.animation = {}
        for direction in directions:
            self.animation[direction] = this.data.sprites.get_data_array(self._imagename
                                                                         + "_anim_" + direction + "_\d")

        # set animation frame to 0 and a direction
        self._facing = "right"
        self.__frame = 0

        # set the sprites movement to false, as it's not moving
        self.moving = False

    # set direction the sprite is facing
    def facing(self, direction):
        self._facing = direction
        self.__frame = 0

    # move the sprite.
    def move(self, dx, dy, **kwargs):
        rect = self.rect.move(dx, dy)

        # don't let the sprite get out of the background
        if this.background.get_rect().contains(rect):
            # check the collision between each sprite
            for sprite in this.onscreen_sprites:
                # don't check the same sprite as it self as it will allways collide
                if sprite != self._imagename:
                    # incorrect col. dunno why.
                    if rect.colliderect(this.onscreen_sprites[sprite].rect):
                        # check whether the collided sprite is a door.
                        if this.onscreen_sprites[sprite].__class__.__name__ == "door":
                            # if so activate that sprite, making the setting change
                            this.onscreen_sprites[sprite].activate()
                            # self.sounds["collide_beep"].play()
                            self.moving = False
                            # exit func and return false as not moving
                            return False
                        elif this.settings.get_current_setting() != "moonlight-scene":
                            # self.sounds["collide_beep"].play()
                            self.moving = False
                            # exit func and return false as not moving
                            return False

            # if there is a customized move_func use it
            # if not use the rect.move func
            if 'move_func' not in sorted(kwargs.keys()):
                self.rect = self.rect.move(dx, dy)
            else:
                kwargs['move_func'](dx, dy)

            # set moveing as true and return true
            self.moving = True
            return True

        else:
            self.moveing = False
            return False

    def update(self, *args):
        if self.moving:
            # clear the image
            self.image.fill((0, 0, 0, 1))

            #inc. frame
            self.__frame += 1

            pygame.time.delay(5)

            # stops errs when changing facing in movement
            # errs happern as we are using threads
            facing = self._facing

            # right and left image is the same
            if (facing == "right") | (facing == "left"):
                # modulo over the length of the frames available to our frame counter
                self.__frame %= len(self.animation["right"])
                # delay so you can see each frame
                self.image.blit(self.animation["right"][self.__frame], (0, 0))
                if facing == "left":
                    # left direction is a flipped image of right. so we flip it instead of making a copy
                    self.image = pygame.transform.flip(self.image, True, False)

            else:
                self.__frame %= len(self.animation[facing])
                self.image.blit(self.animation[facing][self.__frame], (0, 0))

            # make pygame redraw the sprite
            self.dirty = 1
            self.moving = False


# tuples to store text related data
font_data = collections.namedtuple('font_data', ['size', 'name'])
text_data = collections.namedtuple('text_data', ['text', 'font_size', 'font_name'])


class basic_text_box():
    def __init__(self, pos, border, **kwargs):
        #  sounds = ['activate_beep']

        self.border = sprite(border, pos)
        self.rect = self.border.rect

        #  if 'sounds' in sorted(kwargs.keys()):
        #     sounds += kwargs['sounds']

        # make textbox sprite little bit smaller than border, clear it and center it in the border
        self.text_box = pygame.sprite.Sprite()
        self.text_box.image = pygame.Surface([self.rect.width - 6, self.rect.height - 6])
        self.text_box.rect = self.text_box.image.get_rect()
        self.text_box.image.fill(0)
        self.text_box.rect.x = pos.x + 3
        self.text_box.rect.y = pos.y + 3

        self.visible = False

    # set correct position remembering the centering of text_box
    def set_pos(self, pos):
        self.border.rect.x = pos.x
        self.border.rect.y = pos.y
        self.text_box.rect.x = pos.x + 3
        self.text_box.rect.y = pos.y + 3

    def get_pos(self):
        return position(self.border.rect.x, self.border.rect.y)

    def word_wrap(self, text, font_name, font_size):
        # get font, then get the width of textbox
        font = this.fonts.get_data(font_name)
        textbox_x = self.text_box.image.get_rect().width

        # if the text is larger than the textbox width then...
        if textbox_x < font.get_rect(text,
                                     size=font_size).width:
            lines = []
            output = ""
            # find which word the text goes over the width of the text box
            for word in text.split(' '):
                if textbox_x < font.get_rect(output + ' ' + word, size=font_size).width:
                    # and put a newline before it
                    output += '\n'
                    lines.append(output.replace(' ', '', 1))
                    output = ""
                output += ' ' + word

            # get remaining text
            lines.append(output.replace(' ', '', 1))
            # return output
            text = ""
            for line in lines:
                text += line
        return text

    # similar for textbox but using height
    def page_wrap(self, text, font_name, font_size):
        font = this.fonts.get_data(font_name)
        y = self.text_box.image.get_rect().height
        if font.get_rect(text, size=font_size).height > y:
            page_text = ""
            pages = []
            for line in text.split('\n'):
                if font.get_rect(page_text,
                                 size=font_size).height < y:
                    page_text += '\n' + line
                else:
                    pages.append(page_text)
                    page_text = ""
            return pages
        else:
            # returns an array as that is what the caller is expecting.
            return [text]

    # parse newlines into drawable output
    def newline_draw_text(self, txt_data):
        lines = txt_data.text.split('\n')
        for lineNo in range(len(lines)):
            this.fonts.get_data(txt_data.font_name).render_to(self.text_box.image,
                                                              (6, 6 + 20 * lineNo), lines[lineNo],
                                                              size=txt_data.font_size, fgcolor=(255, 255, 255))

    # clear the textbox image
    def draw_func(self):
        self.text_box.image.fill((0, 0, 0))

    # draw the textbox on screen
    def draw(self, surface):
        if self.visible:
            surface.blit(self.border.image, self.get_pos())
            surface.blit(self.text_box.image, self.text_box.rect)
            self.draw_func()

    # controls drawing. stops main draw func from getting bloated.
    def show(self):
        self.visible = True

    def hide(self):
        # self.text_box.sounds["activate_beep"].play()
        self.visible = False


class text_box(basic_text_box):
    def __init__(self, pos):
        basic_text_box.__init__(self, pos, "text_box")
        self.pages_to_render = []
        self.txt_data = ""
        self.new = True
        self.frozen = False

    def show(self):
        this.text_box_visible = True
        basic_text_box.show(self)

    def hide(self):
        this.text_box_visible = False
        basic_text_box.hide(self)

    def activate(self, **kwargs):
        # self.border.sounds["activate_beep"].play()
        if len(self.pages_to_render) != 0:
            self.txt_data = self.pages_to_render.pop()
            if 'func' in sorted(kwargs):
                kwargs['func']()
        self.hide()

    def draw_func(self):
        basic_text_box.draw_func(self)
        basic_text_box.newline_draw_text(self, self.txt_data)

    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False

    # handle the events for the text_box
    def run(self):
        while self.visible & (not this.text_menu_visible) & (not self.frozen):
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
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

        # inc. the page so the textbox has something to show
        # if it is the first time of it running say func
        self.activate()


        self.show()
        self.run()

    def draw(self, surface):
        if not this.text_menu_visible:
            basic_text_box.draw(self, surface)


class text_menu(basic_text_box):
    def hide(self):
        basic_text_box.hide(self)
        this.text_menu_visible = False

    # word and page wrap
    def format(self):
        if self.end_formatting != '\n':
            self.text = self.word_wrap(self.text, self.font.name, self.font.size)

        self.render_text = self.page_wrap(self.text, self.font.name, self.font.size)

    # create menu text from the items dict
    def render(self):
        self.text = ""
        self.render_text = []

        for item_name in list(self.items.keys()):
            if item_name != "reload_func":
                self.text += "    " + item_name + self.end_formatting
            else:
                self.reload_func = self.items[item_name]
                self.items.pop(item_name)

        self.format()

    # deselect an item, should not be pos. to have nothing selected, so is private
    # acts to reset the >
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
        if len(self.items.keys()) != 0:
            if self.selected != "":
                self.__deselect()

            self.selected_index = index % len(self.items.keys())

            self.selected = sorted(self.items.keys())[self.selected_index]

            textlist = list(self.text)

            textlist[re.search(r"\b" + self.selected + r"\b", self.text).start() - 2] = '>'

            self.text = list_to_str(textlist)

            self.page_number = self.find_page_number_of_item(self.selected)
            self.format()

    def select_next(self):
        self.select(self.selected_index + 1)

    def select_previous(self):
        self.select(self.selected_index - 1)

    def get_selected(self):
        return self.selected

    def reload_menu(self):
        if self.reload_func is not None:
            self.items = self.reload_func()
            self.render()
            if self.selected not in self.items.keys():
                self.select(0)

    # activate selected
    def activate(self, *args):
        selected = self.selected
        item_selected = self.items.get(selected)

        if item_selected is not None:
            if item_selected.__class__.__name__ != 'dict':
                if item_selected != "previous":
                    output = item_selected(selected)
                    self.reload_menu()
                    if output == "previous":
                        self.previous_menu()
                    elif output.__class__.__name__ == 'dict':
                        self.previous = self.items
                        self.previous["reload_func"] = self.reload_func
                        self.selected = ""
                        self.items = output
                        self.render()
                        self.select(0)
                    return output
                else:
                    self.previous_menu()
                    return "previous"
            else:
                self.items["reload_func"] = self.reload_func
                self.previous = self.items
                self.items = item_selected
                self.selected = ""
                self.render()
                self.select(0)
        else:
            self.previous_menu()


    def previous_menu(self):
        # self.text_box.sounds["back_beep"].play()
        if self.previous is not None:
            self.items = self.previous
            self.previous = None
            self.render()
            self.selected = ""
            self.select(0)
        else:
            self.hide()

    def draw_func(self):
        basic_text_box.draw_func(self)
        basic_text_box.newline_draw_text(self, text_data(self.render_text[self.page_number],
                                                         self.font.size, self.font.name))

    # handle the events for the text_menu
    def run(self):
        while self.visible & this.drawing:
            # wait for event
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

    # runs self, as well as show.
    def show(self):
        this.text_menu_visible = True
        basic_text_box.show(self)
        self.run()

    def __init__(self, items, pos, **kwargs):
        border = "text_menu"
        self.reload_func = None

        if 'border' in kwargs:
            border = kwargs['border']

        # reload func reloads menu when something may have changed e.g. a item removed from inv.
        if 'reload_func' in kwargs:
            self.reload_func = kwargs['reload_func']

        basic_text_box.__init__(self, pos, border)  # , sounds = ['select_beep', 'back_beep'])
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

buff = collections.namedtuple('buff', ['stat', 'name'])


def concat_dicts(*dicts, **kwargs):
    output = {}
    for dic in dicts:
        if len(dic) > 0:
            keys = output.keys() | dic.keys()
            output = {k: output.get(k, kwargs["default"]) + dic.get(k, kwargs["default"]) for k in keys}
    return output


def deconcat_dicts(*dicts, **kwargs):
    output = {}
    for dic in dicts:
        if len(dic) > 0:
            keys = output.keys() | dic.keys()
            output = {k: output.get(k, kwargs["default"]) - dic.get(k, kwargs["default"]) for k in keys}
    return output



# convenience function for creating item data for text_menus
def menu_data(data_get, var):
    output = {}

    for data in data_get:
        output[data] = var

    return output


class entity(moveable):
    def __init__(self, name, pos, basestat, **kwargs):
        moveable.__init__(self, name, pos, **kwargs)
        self.__stunned = 0
        self.max_determination = basestat["determination"]
        self.basestat = basestat
        self.equipped = {}
        self.inventory = {}
        self.moves = {}
        self.__temp_buffs = []
        self.__stats = {}
        self.__persuasion = 0
        self.__damage_taken = 0
        self.__stats_needs_update = True
        self.__losing_message = "..."
        if 'losing_message' in kwargs:
            self.__losing_message = kwargs['losing_message']

    # getters.
    def get_persuasion(self):
        return self.__persuasion

    def get_losing_message(self):
        return self.__losing_message

    # utitly get funcs.
    def get_buffs_from_dict(self, dictbuff):
        buffs = []
        for item in dictbuff:
            buffs.append(item["buffs"])
        if len(buffs) != 0:
            return concat_dicts(*buffs, default=0)
        else:
            return {}

    def get_temp_buffs(self):
        buffs = []
        for Item in self.__temp_buffs:
            if Item != "turns":
                buffs.append(Item)
        if len(buffs) != 0:
            return concat_dicts(*buffs, default=0)
        else:
            return {}

    def get_basestats(self):
        return self.basestat

    def __update_stats(self):
        self.__stats = concat_dicts(self.basestat,
                                    self.get_temp_buffs(),
                                    self.get_buffs_from_dict(self.equipped), default=0)
        self.__stats["enlightenment"] *= self.__stats["focus"] / 2
        self.__stats["enlightenment"] += self.__stats["determination"] / 4
        self.__stats["enlightenment"] *= random.uniform(0.2, 1.1)

        if self.__stats["determination"] < self.max_determination:
            self.__stats["determination"] = self.max_determination

        if self.__damage_taken > 0:
            self.__stats["determination"] -= self.__damage_taken

    def is_dead(self):
        stats = self.get_stats()
        return (stats["determination"] - self.__damage_taken <= 0) | \
               (self.get_persuasion() > stats["determination"] + stats["focus"])

    def get_stats(self):
        if self.__stats_needs_update:
            self.__update_stats()
            self.__stats_needs_update = False
        return self.__stats

    def add_move(self, move):
        self.moves[move["name"]] = move

    def get_moves(self):
        return self.moves

    def unequip(self, itemname):
        self.__stats_needs_update = True
        self.inventory[itemname] = self.equipped[itemname]
        self.equipped.pop(itemname)

    def equip(self, itemname):
        self.__stats_needs_update = True
        self.equipped[itemname] = self.inventory[itemname]
        self.inventory.pop(itemname)

    def get_equipped(self):
        return self.equipped

    def add_to_inventory(self, item):
        if item["name"] in self.inventory:
            self.inventory[item["name"]]["quantity"] += item["quantity"]
        else:
            self.inventory[item["name"]] = item

    def remove_from_inventory(self, item):
        self.inventory[item["name"]]["quantity"] -= item["quantity"]
        if self.inventory[item["name"]]["quantity"] <= 0:
            self.inventory.pop(item["name"])

    def get_inventory(self):
        return self.inventory

    def get_inventory_menu_data(self, *args):
        if len(self.inventory) > 0:
            out = menu_data(sorted(self.get_inventory().keys()), self.use_item)
            out["reload_func"] = self.get_inventory_menu_data
            return out
        else:
            return {}

    def trade(self, item_to_remove, item_to_gain):
        self.remove_from_inventory(item_to_remove)
        self.add_to_inventory(item_to_gain)

    def use_item(self, itemname):
        self.__stats_needs_update = True
        for buff in self.inventory[itemname]["buffs"]:
            if buff != "determination":
                self.basestat[buff] += self.inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]
            else:
                self.max_determination += self.inventory[itemname]["buffs"][buff] * self.inventory[itemname]["potency"]

        if self.inventory[itemname]["effect"] is not None:
            self.inventory[itemname]["effect"]()

        if self.inventory[itemname]["equipabble"]:
            self.equip(itemname)

        if self.inventory[itemname]["consumable"]:
            self.remove_from_inventory({"name": itemname, "quantity": 1})

    def _stun(self, enemy_stats, NumberOfTurns):
        enemy_attack = (enemy_stats["enlightenment"] / 4) * random.uniform(0, (0.5 + enemy_stats["focus"] / 130))

        if self.get_stats()["wit"] > enemy_attack:
            this.battlebox.say(self.battle_name + " was stunned!")
            self.__stunned = NumberOfTurns

    def is_hopeful(self):
        if self.get_stats()["hope"] > random.randrange(0, 500):
            return True
        else:
            return False

    def take_damage(self, enemy):
        stats = self.get_stats()
        enemy_stats = enemy.get_stats()

        if enemy.is_hopeful():
            for k in enemy_stats:
                enemy_stats[k] *= 2

        if stats["wit"] > enemy_stats["enlightenment"] / 4 * random.uniform(0, 0.5 + enemy_stats["focus"] / 55):
            self.__persuasion += enemy_stats["enlightenment"]
        else:
            this.battlebox.say(self.battle_name + " out witted the attack! " +
                               enemy.battle_name + " focuses on not embarrasing themselves futher.")

        self.__damage_taken = self.__damage_taken + enemy_stats["focus"] - stats["control"]

    def use_move(self, movename, enemy):
        if (self.basestat["thought"] - self.moves[movename]["thought"] > 0) | (self.__stunned <= 0):
            self.basestat["thought"] =- self.moves[movename]["thought"]

            for buff in self.moves[movename]["buffs"]:
                if buff == "determination":
                    self.max_determination += self.moves[movename]["buffs"][buff]
                self.basestat[buff] += self.moves[movename]["buffs"][buff]

            if len(list(self.moves[movename]["temporary_buffs"].keys())) != 0:
                self.__temp_buffs.append(self.moves[movename]["temporary_buffs"])

            self.__stats_needs_update = True

            if self.moves[movename]["stun_effect"] > 0:
                enemy.stun(self.get_stats(),
                           self.moves[movename]["stun_effect"])

            enemy.take_damage(self)

            return True
        else:
            this.battlebox.say("but " + self.battle_name + " does not have enough thought to preform that move!")
            return False

    # dec. a temporary status effects turn number, if they are 0 remove them.
    def next_turn(self):
        if self.__stunned != 0:
            self.__stunned -= 1
        for buff in self.__temp_buffs:
            buff["turns"] -= 1
            if buff["turns"] < 0:
                self.__temp_buffs.remove(buff)

        self.__stats_needs_update = True


# a text_menu which is the same size as a text_box and items are ordered horizontally
def battle_menu(items):
    responsebox = text_menu(items, position(0, 0), border="text_box", end_formatting='    ')
    responsebox.set_pos(position(0, this.window.get_height() - this.textbox.border.rect.height))
    return responsebox

def response_menu(items):
    responsebox = battle_menu(items)
    responsebox.show()
    return responsebox

class NPC(entity):
    def __init__(self, name, pos, basestat, **kwargs):
        entity.__init__(self, name, pos, basestat, **kwargs)
        self.__dialog = {}
        self.__battle_won = None
        self.dialog_dict = {}
        self.__repeat_dialog = {'...': ''}
        if 'battle_name' in kwargs:
            self.battle_name = kwargs['battle_name']
        else:
            self.battle_name = self._imagename

    def is_dead(self):
        self.__battle_won = False
        return entity.is_dead(self)

    def won_battle(self):
        self.__battle_won = True

    # wrapper for text to say.
    def say(self, text):
        this.textbox.say(text, font=font_data(20, self._imagename), speaker=self._imagename)

    def load_save_data(self, data):
        self.__dict__.update(data)

    # trade an item for stering(in game money)
    def sell(self, item_to_sell):
        # check if the player has enough money.
        if "sterling" in this.onscreen_sprites["player"].inventory:
            if this.onscreen_sprites["player"].inventory["sterling"]["quantity"] >= self.inventory[item_to_sell]["price"]:
                this.onscreen_sprites["player"].trade(
                    {"name": "sterling", "quantity": self.inventory[item_to_sell]["price"]},
                    this.items[item_to_sell])
                self.trade(this.items[item_to_sell], {"name": "sterling", "quantity":self.inventory[item_to_sell]["price"]})
            else:
                # if not notify player.
                self.say("you don't have enough money. get some and ask again.")
        # else:
            # self.say("you have no money, how are you going to buy something without money?")
        return "previous"

    # menu for selling items
    def _get_sell_menu_data(self):
        if len(self.inventory) > 0:
            out = menu_data(sorted(self.get_inventory().keys()), self.sell)
            out["reload_func"] = self._get_sell_menu_data
            return out
        else:
            self.say("I'm out of goods sorry")
            return None

    # gets the correct dialog tree
    def _get_dialog(self):
        if self.__battle_won is not None:
            if self.__battle_won:
                return self.__dialog["battle_won"].get(this.settings.get_current_setting())
            else:
               return self.__dialog["battle_lost"].get(this.settings.get_current_setting())
        else:
            # no battle has occurred.
            return self.__dialog["battle_none"].get(this.settings.get_current_setting())

    # emulate players movement.
    def move(self, dx, dy):
        for i in range(abs(dx)):
            pygame.time.delay(7)
            if dx != abs(dx):
                moveable.move(self, -1, 0)
            else:
                moveable.move(self, 1, 0)
        for i in range(abs(dy)):
            pygame.time.delay(7)
            if dy != abs(dy):
                moveable.move(self, 0, -1)
            else:
                moveable.move(self, 0, 1)

    def move_to(self, sprite_name):
        pos_to = this.onscreen_sprites[sprite_name].get_pos()
        pos_from = self.get_pos()
        self.move(pos_to.x - pos_from.x - 1, pos_to.y - pos_from.y - 1)

    # parses dialog string
    def parse_dialog(self, dialog):
        if dialog != "":
            if dialog.__class__.__name__ == 'dict':
                self.dialog_dict = dialog
                response_menu({k: self.menu_dialog for k in dialog.keys()})
            if '_give_item' in dialog:
                this.onscreen_sprites["player"].add_to_inventory(this.items[re.match('_give_item (.+)', dialog).group(1)])
            elif '_give_move' in dialog:
                this.onscreen_sprites["player"].add_move(this.moves[re.match('_give_move (.+)', dialog).group(1)])
            elif '_move_to' in dialog:
                self.move_to(re.match('_move_to (.+)', dialog).group(1))
            elif '_move_player_to' in dialog:
                NPC.move_to(this.onscreen_sprites["player"], (re.match('_move_player_to (.+)', dialog).group(1)))
            elif dialog == "_trade":
                menu = text_menu(self._get_sell_menu_data(), position(0, 0))
                menu.show()
            elif dialog == "_attack_player":
                self.__battle_won = battle(this.onscreen_sprites["player"], self)
            else:
                self.say(dialog)

    # activation, will be activated by players activation function/key.
    def activate(self):
        dialog = self._get_dialog()
        if dialog is not None:
            sorted_keys = sorted(self._get_dialog().keys())
            if len(sorted_keys) != 0:
                if sorted_keys[0] != "":
                    self.say(sorted_keys[0])
                self.parse_dialog(self._get_dialog().pop(sorted_keys[0]))
            else:
                key = sorted(self.__repeat_dialog.keys())[0]
                self.say(key)
                self.parse_dialog(self.__repeat_dialog[key])
        else:
            key = sorted(self.__repeat_dialog.keys())[0]
            self.say(key)
            self.parse_dialog(self.__repeat_dialog[key])


class Player(entity):
    def get_player_data(self):
        return self.__dict__

    def load_save_data(self, data):
        self.__dict__.update(data)

    #   def save_data(self):
    #       self.pos = self.get_pos()
    #       return { "vars" : subset_dict_from_array(self.__dict__, self.save_vars),
    #              'classname' :  self.__class__.__name__ }

    # Menus and dialogs for player to interface with.
    def get_equipped_menu_data(self, *args):
        return menu_data(sorted(self.get_equipped().keys()), self.unequip)

    def get_stats_menu_data(self, *args):
        output = {}

        stats = self.get_stats()
        for stat in stats:
            output[stat + "  =  " + str(int(stats[stat]))] = None
        return output

    # confirmation dialogs.
    def is_sure_dialog(self, if_sure, **kwargs):
        dialog = "are you sure?"
        if 'dialog' in kwargs:
            dialog = kwargs['dialog']

        self.sure_dialogs.append({'dialog': dialog, 'if_sure': if_sure})

    def is_sure_dialog_hook(self, *args, **kwargs):
        if 'dialog' in kwargs:
            dialog = kwargs['dialog']
        else:
            dialog = self.sure_dialogs.pop()

        this.textbox.say(dialog['dialog'])

        def sure(*args):
            this.textbox.activate()
            this.textbox.hide()
            return dialog["if_sure"]()

        return response_menu({
            "yep": sure,
            "nope": "previous"
        })

    # quit dialog
    def exit_dialog(self, *args):
        return self.is_sure_dialog_hook(dialog={'if_sure': this.exit, 'dialog': 'do you really want to quit?'})

    def item_description_menu(self, itemname):
        return self.is_sure_dialog(self.use_item, dialog='it says "' + self.inventory[itemname]["description"] + '" eat it?"')

    def get_player_menu_items(self):
        return {
            "inventory": self.get_inventory_menu_data,
            "equipped": self.get_equipped_menu_data,
            "stats": self.get_stats_menu_data,
            "quit": self.exit_dialog
        }

    # player event handling
    def run(self):
        # while no other GUI elements are visible or not in battle
        while this.drawing & (not (this.text_box_visible | this.text_menu_visible | this.inbattle)):
            pygame.event.pump()

            event = pygame.event.poll()

            if event.type == pygame.KEYDOWN:
                # get keys pressed using pygame.key.get_pressed() as it is more continous than events.
                if event.key == pygame.K_LCTRL:
                    # seperate hide and show buttons as they would counteract eachother.
                    self.player_menu.show()
                elif event.key == pygame.K_z:
                    self.activate()
                elif event.key == pygame.K_f:
                    # quick testing key to find if the battles work has to be with a background
                    #  where Lucidia Bright is present.
                    battle(self, this.onscreen_sprites["Lucida Bright"])

            pygame.time.delay(5)

            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:
                self.facing("backward")
                self.move(0, -1)
            elif keys[pygame.K_DOWN]:
                self.facing("forward")
                self.move(0, 1)
            elif keys[pygame.K_LEFT]:
                self.facing("left")
                self.move(-1, 0)
            elif keys[pygame.K_RIGHT]:
                self.facing("right")
                self.move(1, 0)

    def __init__(self, name, pos):
        # lowest stats set.
        entity.__init__(self, "player", pos,
                        {
                            'determination': 100,
                            'enlightenment': 5,
                            'hope': 10,
                            'focus': 1,
                            'wit': 10,
                            'thought': 500,
                            'control': 5
                        }, losing_message="you lost...")  # , sounds = ["activate_beep"] )

        self.sure_dialogs = []

        self.add_move(this.moves["Libertarianism"])
        self.add_move(this.moves["Realism"])
        self.add_move(this.moves["Philla"])
        self.add_move(this.moves["Anticonformism"])

        self.player_menu = text_menu(self.get_player_menu_items(), position(0, 0))
        self.player_name = name
        this.player_name = name
        self.battle_name = this.player_name

        money = this.items["sterling"]
        money["quantity"] = 100
        self.add_to_inventory(money)

    # check if it is an dropped item, if so put the item_data in the inventory and del. it
    def activate_sprite(self, sprite):
        # self.sounds['activate_beep'].play()
        if sprite.__class__.__name__ == "item":
            self.add_to_inventory(sprite.item_data)
            this.text_box("picked up some " + sprite.item_data["name"])
            del sprite
        else:
            sprite.activate()

    # check for a sprite is in range, if so activate it.
    def activate(self):
        rect = self.rect.copy()
        rect.width += 6
        rect.height += 6
        rect.x -= 3
        rect.y -= 3
        # really there should be different rect's for each different direction but player will not notice as it
        # is a short range.
        for Sprite in this.onscreen_sprites:
            # make sure its not a door that we are activating, maybe unexpected for player.
            if (Sprite != self._imagename) & (Sprite.__class__.__name__ != 'door'):
                if rect.colliderect(this.onscreen_sprites[Sprite].rect):
                    self.activate_sprite(this.onscreen_sprites[Sprite])
                # else:
                    # self.sounds['collide_beep'].play()

    def get_pos(self):
        return position(self.rect.x, self.rect.y)

    def get_menu(self):
        return self.menu

    def update(self, *args):
        self.player_menu.draw(this.window)
        entity.update(self, *args)


class battle_player():

    # wrapper funcs.
    def is_dead(self):
        return self._entity.is_dead()

    def get_persuasion(self):
        return self._entity.get_persuasion()

    # funcs which are added to queue
    def use_item(self, itemname):
        self.battle_menu.hide()
        self.__func_queue.append({"func": self._entity.use_item, "args": [itemname]})

    def use_move(self, movename):
        self.battle_menu.hide()
        self.__func_queue.append({"func": self._entity.use_move, "args": [movename, self.enemy]})

    # func that calls theese queued functions
    def do_queued(self):
        function = self.__func_queue.pop()
        out = function["func"](*function["args"])
        self._entity.next_turn()
        return out

    def ready(self):
        return len(self.__func_queue) > 0

    def get_stats(self):
        return self._entity.get_stats()

    def get_moves(self):
        return self._entity.get_moves()

    def get_losing_message(self):
        return self._entity.get_losing_message()

    def get_item_menu_data(self, *args):
        return menu_data(sorted(self._entity.get_inventory().keys()), self.use_item)

    def get_move_is_sure_disc(self, movename):
        this.battlebox.say(self.get_moves()[movename]["description"])
        return self.use_move(movename)

    def get_move_menu_data(self, *args):
        return menu_data(self._entity.get_moves().keys(), self.use_move)

    def __init__(self, entity, enemy):
        self._entity = entity
        self.__func_queue = []
        self.enemy = enemy
        self.battle_menu = battle_menu({
            'items': self.get_item_menu_data,
            'moves': self.get_move_menu_data
        })


class battle_NPC(sprite):
    def __init__(self, entity, pos):
        self._entity = entity
        sprite.__init__(self, entity.battle_name, pos)

    def is_dead(self):
        return self._entity.is_dead()

    def won(self):
        self._entity.won_battle()

    def __del__(self):
        pass

    def get_persuasion(self):
        return self._entity.get_persuasion()

    def get_stats(self):
        return self._entity.get_stats()

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
            move = sorted(moves.keys())[random.randrange(0, len(moves))]
            this.battlebox.say(self._entity.battle_name + " used " + move)
            self._entity.use_move(move, this.onscreen_sprites["player"])
            self._entity.next_turn()

    def get_losing_message(self):
        return self._entity.get_losing_message()

# no longer a thread as it doesn't need to be
# threads are very resource hogging, but also very preformant so we should use them sparingly.
class battle:
    def __init__(self, player, npc):
        this.inbattle = True
        this.battle_npc = battle_NPC(npc, position(0, 0))
        self.player = battle_player(player, npc)

        calc_pos = lambda winx, objx: winx / 2 - objx / 2
        this.battle_npc.set_pos(position(calc_pos(this.window.get_width(), this.battle_npc.rect.right),
                                         calc_pos(this.window.get_height(), this.battle_npc.rect.bottom)))

        if self.player.get_stats()["focus"] > this.battle_npc.get_stats()["focus"]:
            self.__player_turn = True
        else:
            self.__player_turn = False

        self.run()

    def __del__(self):
        this.first_battle = False

    def battle_end(self):
        if this.battle_npc.is_dead() | self.player.is_dead():
            # closure for transferring inv.
            def transfer_inventory(e1, e2):
                inv = e2._entity.get_inventory()
                for item in list(inv.keys()) :
                    e1._entity.add_to_inventory(inv[item])
                    e2._entity.remove_from_inventory(inv[item])

            # transfer losers inventory to winner.
            if this.battle_npc.is_dead():
                transfer_inventory(self.player, this.battle_npc)
                this.battlebox.say(this.battle_npc.get_losing_message())
            else:
                this.battle_npc.won()
                transfer_inventory(this.battle_npc, self.player)
                this.battlebox.say(self.player.get_losing_message())

            this.inbattle = False
            del this.battle_npc
            self.__del__()

            # stop the battle
            return True
        return False

    def run(self):
        if this.first_battle:
            this.battlebox.say("Welcome to a battle.")
            this.battlebox.say("you win by lowering your openents determination to 0 or persuading them until they are pesuaded")
            this.battlebox.say("you do this by either selecting a move, which will lower an oppenents stats")
            this.battlebox.say("or use an item which will heal yourself or give a boost to your stats giving you an advantage.")

        while not self.battle_end():
            if self.__player_turn:
                # show stats
                this.battlebox.say(
                    this.player_name + " DETERMINATION: " + str(int(self.player.get_stats()["determination"])) + """
                    """ + this.battle_npc._entity.battle_name + "DETERMINATION: " + str(int(this.battle_npc.get_stats()["determination"])) + """
""" + this.player_name + " PERSUATION: " + str(int(self.player.get_persuasion())) + """
""" + this.battle_npc._entity.battle_name +" PERSUATION: " + str(int(this.battle_npc.get_persuasion())))

                # show menu
                self.player.battle_menu.show()

                # do queued if ready
                if self.player.ready():
                    self.player.do_queued()

                # no longer players turn
                self.__player_turn = False

            else:
                # calc. attack and do it.
                this.battle_npc.do_attack()
                # now players turn
                self.__player_turn = True
        # there is no need for this object; the battle has ended.
        del self


# quit function really should be __del__ but might interfere in module destruction when imported.
def exit():
    # stop the thread safely
    this.drawing = False
    this.draw_thread.join()

    # quit.
    pygame.quit()
    sys.exit()


# draw all sprites and background, menus, textboxes etc...
# was going be in a thread but was too complex for such a simple program.
def update():
    while this.drawing:
            # pump an event, stops the program from not responding when it is not getting events
            pygame.event.pump()

            # clear window so we don't get horrible screen
            this.window.fill(0)

            if not this.inbattle:
                if this.background is not None:
                    # blit background
                    this.window.blit(this.background, (0, 0))
                    # update sprite hook called
                    this.onscreen_sprites.update()
                    # blit all sprites
                    this.onscreen_sprites.draw(this.window)
                this.textbox.draw(this.window)
            else:
                this.window.blit(this.battle_npc.image, this.battle_npc.rect)
                this.battlebox.draw(this.window)

            # draw all menus.
            for menu in this.text_menus_to_draw:
                menu.draw(this.window)

            # update dislplay
            pygame.display.flip()

# def save_data():
#   json.dumps({
#    "sprites":this.data_sprites,
#    "setting":this.settings.get_current_setting()
# })


# gets name input
def get_name():
    # freeze event checking by textbox so there is no competetion
    this.textbox.freeze()

    name = ""
    iterate = True
    shift = False
    while iterate:
        # make the textbox allways visible, stops it from flashing between keypresses.
        this.textbox.visible = True

        # wait for an event
        event = pygame.event.wait()

        # if a key has been pressed
        if event.type == pygame.KEYDOWN:
            # get the keys name
            char = pygame.key.name(event.key)
            if char == "space":
                char = ' '
                name += char
            elif (char == "left shift") | (char =="right shift"):
                shift = True
            elif char == "backspace":
                name = re.match(r'(.*).', name).group(1)
            elif char == "return":
                iterate = False
            else:
                if shift:
                    char.capitalize()
                    shift = False
                name += char

            # say the name
            this.textbox.say(name)
            # activate so it shows correct text
            this.textbox.activate()

    # resume textbox events
    this.textbox.unfreeze()
    return name


# start procedure
def start_screen():
    # display set text on screen
    this.textbox.say("""Press ANY key.""")
    this.textbox.say("""thank you for accepting our not so binding agreement for you to play this game.""")

    # joke tutorial element to help player
    this.textbox.say("""hello. Welcome to the world of Earth(R)
You need a name, due to budget cuts from the education system
we can only give you a few, choose well!
with the power of the arrow keys to select and the z key to confirm!""")
    # make sure not drawing over menu
    this.textbox.hide()

    # create tutorial, menu element
    response_menu({"bob": None, "bobett": None, "bobafett": None})

    this.textbox.show()
    this.textbox.say("great Choice! ...")

    this.textbox.say("STOP! POLITICAL CORRECTNESS POLICE IS HERE TO GIVE JUSTICE!")
    this.textbox.say("Nooooooo! please Nooo.")
    this.textbox.say("""YOU HAVE BEEN SECTIONED ON RESTRICTING HUMAN EXPRESSION.
ENTER YOUR NAME BEFORE HE STARTS WRITING YOU DESTINY.
PRESS ENTER ONCE YOU HAVE COMPLETED YOUR NAME.""")

    # create a blank screen
    this.textbox.activate()

    # get the players name
    name = get_name()

    # use the name confirming it.
    this.textbox.say("oh so your name is " + name + ". I guess we could use that.")

    # make a new player.
    this.onscreen_sprites["player"] = Player(name, position(0, 0))

    # load the starting background
    this.settings.load("overworld")

    this.textbox.say("""ERM... HERE ILL HELP YOU UP, CALL ME RICHARD.
USE YOU'RE ARROW KEYS TO MOVE,
CTRL TO OPEN THE MENU AND X TO CLOSE.
THE Z TO ACTIVATE THINGS IN FRONT OF YOU WHATEVER THAT MEANS. WEIRD THAT YOU CAME WITH AN OPERATION MANUAL""",
                     speaker="Poor Richard")

    this.textbox.say("""ha.. just kidding! you're the new guy who just moved in,
well yours is the one right in front of you, have a nice day!""", speaker="Poor Richard")

    this.textbox.say("""anyway don't forget that you have got an exam, just telling you if you have a suddern bout of amnesia!""",
                     speaker="Poor Richard")

    this.textbox.say("""after that the vicor said that he wanted me to come to tea, he's in the rightmost house he said that he
        wanted to welcome me(give exposition) into the neighbourghood.""")

    # start the player event system
    this.onscreen_sprites["player"].run()

def __init__():
    # load all variables needed that are used moudle-wide
    this.first_battle = True
    this.drawing = True
    this.text_menu_visible = False
    this.text_box_visible = False
    this.inbattle = False
    this.player_name = "player"

    # make the window
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

    # textbox which is used throughout game
    this.textbox = text_box(position(0, 0))

    # have to do this as textbox rect was not defined before
    this.textbox.set_pos(position(0, this.window.get_height() - this.textbox.border.rect.height))

    # battle box textbox for when in battle.
    this.battlebox = text_box(position(0, 0))
    this.battlebox.set_pos(position(0, this.window.get_height() - this.textbox.border.rect.bottom))

    # load vars
    this.data_sprites = {}
    this.onscreen_sprites = SpriteDict()
    this.text_menus_to_draw = []

    # pygame.mixer.init()
    # this.background_music = pygame.mixer.Channel(0)
    this.background = None

    # try to get resouces quit if can't
    try:
        this.items = object_loader.load_objects("items.json")
        this.moves = object_loader.load_objects("moves.json")
    except (OSError, IOError, FileNotFoundError):
        print("cannot load items.json or moves.json, Fatal Error. Exiting")
        sys.exit(404)

    # load NPCs from npc.json
    for sprite in json.load(open("npcs.json")):
        this.data_sprites[sprite["name"]] = {
            "classname": "NPC",
            "vars": {
                "_imagename": sprite["name"],
                "inventory": subset_dict_from_array(this.items, sprite["items"]),
                "equipped": subset_dict_from_array(this.items, sprite["equipped"]),
                "moves": subset_dict_from_array(this.moves, sprite["moves"]),
                "_NPC__dialog": sprite["dialog"],
                "_NPC__repeat_dialog": sprite["repeat_dialog"],
                "battle_name": sprite["battle_name"],
                "basestat": sprite["stats"],
                "losing_message": sprite["losing_message"]
            }
        }

    # load sprites from sprite.json
    for sprite in json.load(open("sprites.json")):
        classname = sprite['classname']
        this.data_sprites[sprite['_imagename']] = {'classname': classname, 'vars':sprite}

    # startup draw(update) thread.
    this.draw_thread = threading.Thread(target=update)
    this.draw_thread.start()

    # run the start procedure
    start_screen()


# only run init if not being imported
if __name__ == '__main__':
    __init__()


"""
    a critique of the game: it's awful.
    code wise and gameplay wise. thats it.

    code wise the event system is dire, dure to the use of threads and the run() functions.
    also the game does not apply to pep8 standards.

    another major problem is the inability to have dialog that is more than two textboxes full worth of dialog in one activation
    and that NPC's do not really interact with each other.

    the text menu selection is muddled as dicts maintain no order.
    also there is no showing of the description of moves, as is sure_dialogs
    did not work and i did not have enough time to fix them.

    really most of the errors came from the expectation that pythons arguments
    we're copies of the objects instead of pointers.

    the rest of the errors came from bad autocomplete and little linting power
    along with the large scale codebase which was not runnable in the instant
    as they could have been nipped in the bud easly e.g. not adding a key to the dict variable would give a similar error.

    due to this also in build testing has also been hampered. and most of the original code has been corrected.

    oh and the story uses *all* the cliches. and is just. strange.
    play it for youself and see.
"""