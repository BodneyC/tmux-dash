#!/usr/bin/env python3

import os
import sys
import yaml
import logging
import argparse

import libtmux

logging.basicConfig(level=logging.WARN)

DEFAULT_CONFIG = os.environ.get('TMUX_DASH_CONFIG', os.environ.get('HOME', '.')
                                + '/.config/tmux-dash/config.yml')
MODULE_DIR = os.environ.get('TMUX_DASH_MODULE_DIR', os.path.dirname(os.path.realpath(__file__)) + '/modules')
TMUX_VAR = os.environ.get('TMUX', None)


class ConfigParseError(Exception):
    pass


class PlaySession:
    def __init__(self, session, config):
        self.log = logging.getLogger('Session')
        self.session = session
        self.config = config
        self.pane_id_dict = {}
        self.t_height = None
        self.t_width = None
        self.window = None

    def _percent_conversion(self, s, d):
        return int((int(s[:-1]) / 100) * int(d))

    def _make_split(self, conf):
        pane_id = self.session.attached_pane._pane_id
        if 'from' in conf:
            if conf['from'] in self.pane_id_dict:
                pane_id = self.window.select_pane(
                    self.pane_id_dict[conf['from']]
                )._pane_id
            else:
                self.log.warning(f'{conf["from"]} not assigned, check ordering')

        try:
            from_pane = self.window.select_pane(pane_id)
        except libtmux.exc.LibTmuxException:
            self.log.error(
                f'Cannot select {pane_id}, splitting from {self.session.attached_pane._pane_id}'
            )
            from_pane = self.session.attached_pane

        vert = True
        if 'direction' in conf and conf['direction'] == 'horz':
            vert = False

        self.window.select_pane(
            from_pane.split_window(pane_id, vertical=vert)._pane_id
        )

        if 'width' in conf:
            if isinstance(conf['width'], str):
                conf['width'] = self._percent_conversion(conf['width'], self.t_width)
            self.session.attached_pane.set_width(conf['width'])
        if 'height' in conf:
            if isinstance(conf['height'], str):
                conf['height'] = self._percent_conversion(conf['height'], self.t_height)
            self.session.attached_pane.set_height(conf['height'])

    def _setup_panes(self, conf):
        for pane_name, pane in conf.items():
            if 'split' in pane and pane['split']:
                self._make_split(pane['split'])
            self.pane_id_dict[pane_name] = self.session.attached_pane._pane_id
            if 'command' in pane:
                self.session.attached_pane.send_keys(pane['command'])
            elif 'module' in pane:
                self.session.attached_pane.send_keys(f'{MODULE_DIR}/{pane["module"]}')

    def _get_terminal_size(self):
        self.session.attached_pane.cmd('resize-pane', '-Z')
        self.t_height, self.t_width = os.popen('stty size', 'r').read().split()
        self.session.attached_pane.cmd('resize-pane', '-Z')

    def play_session(self):
        self._get_terminal_size()
        for window_name, conf in self.config.items():
            number = conf.pop('number')
            try:
                self.session.new_window(window_name, window_index=number)
            except libtmux.exc.LibTmuxException:
                self.log.warning(f'Window {number} exists, results may vary')
            self.window = self.session.select_window(number)
            self._setup_panes(conf)


# Don't judge me...
def validate_config(config):
    if not config:
        raise ConfigParseError('Empty config')

    pane_directives = ['command', 'split']
    split_directives = ['direction', 'from', 'width', 'height']

    for window_name, window in config.items():
        if 'number' not in window:
            raise ConfigParseError(f'\nNo window number: {window_name}')
        for pane_name, pane in window.items():
            err_str = f'pane: {pane_name}\n window: {window_name}'
            if pane_name == 'number':
                if not isinstance(pane, int):
                    raise ConfigParseError(f'\nInvalid window number:\n {err_str}')
                continue
            if 'split' not in pane:
                raise ConfigParseError(f'\n"split" key missing:\n {err_str}')
            for directive in pane:
                d_err_str = f'directive: {directive}\n {err_str}'
                if directive not in pane_directives:
                    raise ConfigParseError(f'\nInvalid directive:\n {d_err_str}')
                if directive == 'split' and pane[directive]:
                    for split_name in pane[directive]:
                        split_val = pane[directive][split_name]
                        if split_name not in split_directives:
                            raise ConfigParseError(f'\nInvalid directive:\n {d_err_str}')
                        s_err_str = f'split directive: {split_name}\n {d_err_str}'
                        if split_name == 'direction':
                            if split_val != 'horz' and split_val != 'vert':
                                raise ConfigParseError(f'\nInvalid value:\n {s_err_str}')
                        if split_name == 'from':
                            if split_val not in window:
                                raise ConfigParseError(f'\nPane not found:\n {s_err_str}')
                        if split_name == 'width' or directive == 'height':
                            if not isinstance(split_val, int) and split_val[-1] != '%':
                                raise ConfigParseError(f'\nInvalid value:\n {s_err_str}')


def find_session(i, n):
    server = libtmux.Server()
    if i:
        return server.get_by_id(i)
    if n:
        return server.find_where({'session_name': n})
    return server.find_where({'session_name': TMUX_VAR.split(',', 2)[-1]})


def read_config(fn):
    try:
        with open(fn) as f:
            return yaml.safe_load(f.read())
    except FileNotFoundError as e:
        raise e
    except yaml.scanner.ScannerError as e:
        raise e


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, default=DEFAULT_CONFIG)
    session_id = parser.add_mutually_exclusive_group()
    session_id.add_argument('-i', '--session-id', type=str)
    session_id.add_argument('-n', '--session-name', type=str)
    return parser.parse_args()


def main():
    args = parse_args()
    config = read_config(args.config)
    validate_config(config)
    session = find_session(args.session_id, args.session_name)
    if not session:
        raise libtmux.exc.TmuxSessionExists
    play = PlaySession(session, config)
    play.play_session()


if __name__ == '__main__':
    #  sys.tracebacklimit = 0
    try:
        main()
    except KeyboardInterrupt:
        print('Signal received, exiting...')
