#!/usr/bin/env bash

# A shell function is required to change the calling shell's directory.
b() {
    local file="$HOME/.bmarks"
    local name path saved_name saved_path destination=''

    case "${1:-}" in
        -h|--help)
            printf '%s\n' 'Usage: b register <name> <directory>' '       b <name>'
            return 0
            ;;
        register)
            if [[ $# -ne 3 ]]; then
                printf '%s\n' 'Usage: b register <name> <directory>' >&2
                return 1
            fi
            name=$2
            if [[ ! $name =~ ^[a-zA-Z0-9_][a-zA-Z0-9_.-]*$ || $name == register ]]; then
                printf '%s\n' 'b: use letters, digits, underscores, dots or hyphens; start with a letter, digit or underscore. "register" is reserved.' >&2
                return 1
            fi
            if [[ $3 == *$'\t'* || $3 == *$'\n'* ]]; then
                printf '%s\n' 'b: directory paths cannot contain tabs or newlines.' >&2
                return 1
            fi
            # The trailing slash preserves newlines through command substitution.
            path=$(CDPATH= builtin cd -P -- "$3" && printf '%s/' "$PWD") || return 1
            path=${path%/}
            if [[ $path == *$'\t'* || $path == *$'\n'* ]]; then
                printf '%s\n' 'b: directory paths cannot contain tabs or newlines.' >&2
                return 1
            fi
            # Appending preserves existing bookmarks; the latest matching entry wins.
            (umask 077; printf '%s\t%s\n' "$name" "$path" >> "$file") || return 1
            printf 'Registered %s -> %s\n' "$name" "$path"
            ;;
        *)
            if [[ $# -ne 1 || -z $1 ]]; then
                printf '%s\n' 'Usage: b register <name> <directory>' '       b <name>' >&2
                return 1
            fi
            if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
                printf '%s\n' 'b: run source ~/bin/b first so b can change your current shell directory.' >&2
                return 1
            fi
            if [[ ! -e $file ]]; then
                printf 'b: bookmark not found: %s\n' "$1" >&2
                return 1
            fi
            while IFS=$'\t' read -r saved_name saved_path; do
                if [[ $saved_name == "$1" ]]; then
                    destination=$saved_path
                fi
            done < "$file" || return 1
            if [[ -z $destination ]]; then
                printf 'b: bookmark not found: %s\n' "$1" >&2
                return 1
            fi
            builtin cd -- "$destination"
            ;;
    esac
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
    b "$@"
fi
