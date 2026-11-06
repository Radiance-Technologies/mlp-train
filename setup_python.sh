#!/usr/bin/env bash
if [ "${BASH_SOURCE[0]}" == "$0" ] ; then
echo "Please invoke as 'source $(basename $BASH_SOURCE)' instead."
exit
fi

# 1. Discover Project Root using native Git
if [ -z "${GITROOT+x}" ]; then
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        GITROOT="$(git rev-parse --show-toplevel)"
        echo "Project root found at: ${GITROOT}"
    else
        echo "WARNING: Not inside a Git repository. Falling back to current directory."
        GITROOT="$(pwd)"
    fi
    export GITROOT
fi

make install
