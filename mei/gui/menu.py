import functools
import os
import pygame

from mei import plugin, theme, datafiles, config
from mei.gui import videobrowser, widgets

class Menu(widgets.Window):
    def __init__(self, app, choices=None):
        super(Menu, self).__init__()

        self._app = app
        self._theme = theme.get('menu')
        self._config = config.get('menu')

        if not choices:
            choices = self._config['choices']

        self._choices = []

        if app.current_window:
            self._choices.append((self.makeButton('Back'), self.goBack))


        browser_types = {
            'video': videobrowser.VideoBrowser
        }
        for choice in choices:
            type = choice['type'].lower()
            
            if type.startswith('browser_'):
                type = type[len('browser_'):]
                if not type in browser_types:
                    raise "WTFBBQ" # TODO: Fix.

                func = functools.partial(browser_types[type], choice['title'], choice['path'])
            elif type == 'menu':
                func = functools.partial(Menu, choices=choice['choices'])
            elif type == 'plugin':
                # Apply default config for this plugin.
                default_config = plugin.get_defaults(choice['plugin'])
                cfg = config.merge(default_config, choice)

                func = functools.partial(plugin.get_plugin(choice['plugin']), cfg)
            else:
                raise "WTFBBQ" # TODO: Fix.

            self._choices.append((self.makeButton(choice['title']), func))

        self.selected = 0

    def goBack(self, app):
        app.close_window()
        return None

    def makeButton(self, label):
        icon = datafiles.get('icon_%s.png' % label.lower())
        if not os.path.isfile(icon):
            icon = None

        return widgets.Button(label, icon, theme.get('menu/button'))

    def calcHeight(self):
        h = 0
        for (button, _)  in self._choices:
            h += button.getDimensions()[1]

        h += (len(self._choices) - 1) * self._theme['spacing']

        return h

    def key(self, event):
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_q or event.key == pygame.K_BACKSPACE:
            self._app.close_window()
        elif event.key == pygame.K_DOWN:
            if self._choices:
                self.selected = (self.selected + 1) % len(self._choices)
        elif event.key == pygame.K_UP:
            if self._choices:
                self.selected = (self.selected - 1) % len(self._choices)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT:
            if self._choices:
                win = self._choices[self.selected][1](self._app)
                if win:
                    self._app.open_window(win)

    def draw(self, screen):
        super(Menu, self).draw(screen)

        y = (screen.get_size()[1] - self.calcHeight())/2
        selected = self.selected
        for (button, _) in self._choices:
            (w, h) = button.getDimensions()
            x = (screen.get_size()[0] - w)/2

            (dx, dy) = button.draw(screen, (x, y), selected == 0)
            selected -= 1

            y += dy + self._theme['spacing']

