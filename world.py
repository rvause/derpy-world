#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Hello World
'''

__author__ = 'Rick Vause <rvause@gmail.com>'
__version__ = '0.0.1'
__copyright__ = 'Copyright (c) 2012 Rick Vause'
__license__ = 'GNU General Public License'


import random
import cocos
from pyglet import window
from cocos.actions import *
from cocos.director import director


# CONSTANTS
CLOUD_MIN = 10
CLOUD_MAX = 120
DAY_LENGTH = 120

NIGHT_COLOR = (10, 51, 102)
DAY_COLOR = (131, 168, 224)

SUN_ELEVATION = 50


class Background(cocos.layer.ColorLayer):

    def __init__(self):
        super(Background, self).__init__(131, 168, 224, 255)

        self.win_width, self.win_height = director.get_window_size()

        # Game info
        self.day = True
        self.night = False
        self.day_counter = 1

        self.day_counter_label = cocos.text.Label(
                'Day %s' % self.day_counter,
                font_name='sans-serif',
                font_size=32,
                anchor_x='left',
                anchor_y='top',
                color=(50, 50, 50, 255)
            )

        self.day_counter_label.position = 5, self.win_height - 5
        self.add(self.day_counter_label, z=10)

        clouds = (
                'assets/cloud1.png',
                'assets/cloud2.png',
                'assets/cloud3.png',
                'assets/cloud4.png',
                'assets/cloud5.png',
                'assets/cloud6.png',
            )
        self.cloud_sprites = []
        for i, cloud in enumerate(clouds):
            setattr(self, 'cloud_%d' % (i + 1), cocos.sprite.Sprite(cloud))
            c = getattr(self, 'cloud_%d' % (i + 1))
            rect = c.get_rect()
            self.add(c)
            c.position = -rect.width / 2, random.randrange(rect.height / 2, self.win_height - rect.height / 2)
            c.do(MoveBy((self.win_width + rect.width, 0), random.randrange(CLOUD_MIN, CLOUD_MAX)))
            self.cloud_sprites.append(c)

        # Sun
        self.sun = cocos.sprite.Sprite('assets/sun.png')
        self.sun.position = 0, 400
        self.add(self.sun)
        rect = self.sun.get_rect()

        # Moon
        self.moon = cocos.sprite.Sprite('assets/moon.png')
        self.moon.position = -rect.width / 2, 400
        self.add(self.moon)

        self.start_orbit_position = (0, 400)
        self.mid_orbit_position = (self.win_width / 2, SUN_ELEVATION)
        self.end_orbit_position = (self.win_width / 2, -SUN_ELEVATION)

        self.reset_orbit = Place((-rect.width / 2, 400))
        self.nudge = MoveBy((rect.width / 2, 0), 1)
        self.move_orbit_up = MoveBy(self.mid_orbit_position, DAY_LENGTH / 4)
        self.move_orbit_down = MoveBy(self.end_orbit_position, DAY_LENGTH / 4)

        self.schedule_interval(self.update, 3)
        self.schedule(self.update_light)
        self.schedule(self.move_sun_moon)

    def update(self, dt, *ar, **kw):
        for cloud in self.cloud_sprites:
            rect = cloud.get_rect()
            if cloud.x >= self.win_width + rect.width / 2:
                cloud.position = -rect.width / 2, random.randrange(rect.height / 2, self.win_height - rect.height / 2)
                cloud.do(MoveBy((self.win_width + rect.width, 0), random.randrange(CLOUD_MIN, CLOUD_MAX)))

    def change_time(self):
        if self.day:
            self.night = True
            self.day = False
        else:
            self.day = True
            self.night = False

    def update_light(self, dt, *ar, **kw):
        if self.day:
            light = DAY_COLOR
        else:
            light = NIGHT_COLOR

        if self.color != light:
            if self.color[0] > light[0]:
                r = self.color[0] - 1
            elif self.color[0] < light[0]:
                r = self.color[0] + 1
            else:
                r = self.color[0]

            if self.color[1] > light[1]:
                g = self.color[1] - 1
            elif self.color[1] < light[1]:
                g = self.color[1] + 1
            else:
                g = self.color[1]

            if self.color[2] > light[2]:
                b = self.color[2] - 1
            elif self.color[2] < light[2]:
                b = self.color[2] + 1
            else:
                b = self.color[2]

            self.color = (r, g, b)

    def move_sun_moon(self, dt, *ar, **kw):
        rect = self.sun.get_rect()

        # Moving the sun
        if self.sun.x == self.mid_orbit_position[0]:
            self.sun.do(self.move_orbit_down)
        if self.sun.x == self.win_width:
            self.sun.do(self.nudge)
            self.moon.do(self.nudge)
            self.change_time()
        if self.sun.x == self.win_width + rect.width / 2:
            self.sun.do(self.reset_orbit)
        if self.sun.x == self.start_orbit_position[0]:
            self.sun.do(self.move_orbit_up)

        # Moving the Moon
        if self.moon.x == self.mid_orbit_position[0]:
            self.moon.do(self.move_orbit_down)
        if self.moon.x == self.win_width:
            self.moon.do(self.nudge)
            self.sun.do(self.nudge)
            self.change_time()
            self.day_counter += 1
            self.day_counter_label.element.text = 'Day %s' % self.day_counter
        if self.moon.x == self.win_width + rect.width / 2:
            self.moon.do(self.reset_orbit)
        if self.moon.x == self.start_orbit_position[0]:
            self.moon.do(self.move_orbit_up)


class World(cocos.layer.Layer):

    def __init__(self):
        super(World, self).__init__()

        self.win_width, self.win_height = director.get_window_size()

        self.world = cocos.sprite.Sprite('assets/planet.png')
        self.world.position = self.win_width / 2, self.win_height / 2
        self.add(self.world)


if __name__ == '__main__':
    director.init(width=640, height=480)
    world_layer = World()
    world_layer.do(Repeat(RotateBy(360, DAY_LENGTH)))
    main_scene = cocos.scene.Scene(
            Background(),
            world_layer
        )
    director.run(main_scene)
