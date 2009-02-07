#!/bin/bash
set -o errexit
set -o nounset

# Purpose: get a copy of an arbitrary Makefile target from any git revision
# usage: SRC_FN DST_FN [REV]
#   * if REV is provided, then that rev's version of SRC_FN will be built
#   * if REV is omitted, then the current state is used
#   * DST_FN should be outside the repo

# validate args
me=$0
if [ $# -lt 2 ]; then
    echo "$me error: too few args"
    exit 1
elif [ $# -gt 3 ]; then
    echo "$me error: too many args"
    exit 1
fi
src=$1
dst=$2

# make sure we're in the repo
dir=`dirname $src`
cd $dir

if [ $# -eq 3 ]; then
    origBranch=`git branch -a | fgrep '*' | sed -e 's#* ##'`

    # stash any unsaved changes (so they aren't merged into our temporary branch)
    set +o errexit
    numChanges=`git s | fgrep -c 'modified:'`
    set -o errexit
    if [ $numChanges -gt 0 ]; then
        trap 'echo "Warning: changed files may have been stashed away; try git stash list"; exit 1' 2
        git stash save

        # try to gracefully cleanup on Ctrl-C before exiting
        trap 'echo Warning: unstashing changes on Ctrl-C; git checkout -q $origBranch; git stash pop > /dev/null; git branch -D $tmpBranch; exit 1' 2
    fi

    # create a temporary branch which includes commits up to the specified revision
    rev=$3
    tmpBranch=tmp$rev
    git branch $tmpBranch $rev
    git checkout -q $tmpBranch
fi

# build and copy the binary
name=`basename $src`
make -C $dir $name
cp $src $dst

if [ $# -eq 3 ]; then
    # cleanup the temporary branch
    git checkout -q $origBranch
    git branch -D $tmpBranch

    # restore stashed changes
    if [ $numChanges -gt 0 ]; then
        git stash pop > /dev/null
        echo "Restored stashed changes"
    fi
fi
