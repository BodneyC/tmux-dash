Tmux Dash
=========

The point of this project was to have an easily configurable dashboard for [tmux](https://github.com/tmux/tmux) which would sit on window 0; essentially, it would have a todo list, various clocks, things of that nature.

There are a couple of alternatives, the one that really comes up often if you're googling around the phrases "terminal" and "dashboard" is [wtfutil](https://wtfutil.com/), my core issue with this is that the module selection is a little limited, I'm also not a big fan of the way it looks and configuration available doesn't really help that.

The other project of a similar nature is [tmuxinator](https://github.com/tmuxinator/tmuxinator) but I didn't want to use it as a binary replacement for `tmux` itself. I also wanted a config which is more focused on a specific layout, for which specific splits are defined for each pane.

## Usage

From within a tmux session run this script and either use the default config (`$HOME/.config/tmux-dash/config.yml`) or specify a config file with the `-c` option.

Next is to specify a tmux session, this can be done with the session id with `-i` or session name with `-n`. Alternativley, if you are within a tmux session, specify nothing and tmux-dash will pick up on your `$TMUX` environment variable.

## Configuration

A sample configuration could be:

```
  dashboard:
    number: 0
    vim-pane:
      command: vim
      split: null
    htop:
      command: htop
      split: 
        direction: horz
        width: 40
    head:
      command: "watch tail /var/log/pacman.log"
      split:
        from: vim-pane
```

This will create a window, numbered 0. In it will be `vim` in the first pane, creating no split (`split: null`), a horizontal split of width 40 containing an instance of `htop`, finally, splitting vertically from the pane marked `vim-pane` watching a log.

So, something like this,

```
  +-------------------+--------+
  |                   |        |
  |                   |        |
  |        Vim        |        |
  |                   |        |
  |                   |        |
  +-------------------+  Htop  |
  |                   |        |
  |                   |        |
  |   watch tail...   |        |
  |                   |        |
  |                   |        |
  +-------------------+--------+
```

The meta config would look something like the following:

```
  <window name>:
    number: <window number>
    <pane id>:
      [command: <command>]
      [module: <module>]
      split: (null|
        [direction: (horz|vert)]
        [from: <pane id>]
        [width: <char width>]
        [height: <char height>])
    <pane 2 id>:
      ...
  <window 2 name>:
    ...
```

## Dependencies

Literally just the one, aside from [Python3](https://www.python.org/download/releases/3.0/), is [libtmux](https://github.com/tmux-python/libtmux).

## Additional Info

`module` refers to what you may find as an empty directory, these are to come, or for anyone who finds this to populate with scripts/binaries, its sole purpose is to put things that you may not necessarily want on your path, kind of pointless but hey.

The only thing that I wouldn't advise it setting up a configuration and not taking into account the fact that the script is running in a particular pane, obviously, that module/command won't be launched.

Hopefully, there's more to come.
