# Bash Bookmark

Save directory bookmarks and jump to them in your current Bash shell.

## Installation

```bash
git clone https://github.com/LostCore/bash-bookmark.git
mkdir -p ~/bin
ln -s "$(pwd)/bash-bookmark/b.sh" ~/bin/b
echo '[ -f "$HOME/bin/b" ] && source "$HOME/bin/b"' >> ~/.bashrc
source ~/bin/b
```

The function must be sourced because an executable cannot change its parent shell's working directory.
New Bash terminals load it through `.bashrc`.

## Usage

```bash
b register ptapp /home/lostcore/projects/Webdev/personal/ptapp
b ptapp

b register work "./a directory with spaces"
b work
b --help
```

Directories must exist when registered.
Relative paths are resolved to absolute physical paths at registration time.
Names contain letters, digits, underscores, dots or hyphens and start with a letter, digit or underscore.
The name `register` is reserved.
Paths containing tabs or newlines are rejected.

Bookmarks are stored as tab-separated name/path records in `~/.bmarks`, never executed as shell code.
The file is created with owner-only permissions.
Registering the same name again appends its new destination; the latest entry wins.
If a destination is deleted, navigation fails with a directory error.

Registration also works by executing `~/bin/b register <name> <directory>` directly.
Navigation requires the sourced function.

## Tests

```bash
python3 test_b.py
```

Tests use temporary home directories and do not change your bookmarks.
