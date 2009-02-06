#!/bin/bash
set -o errexit
set -o nounset

# usage: SRC_FN DST_FN [REV]
# if REV is provided, then that revision will be checked out and its copy of SRC_FN will built
# DST_FN should be outside the repo if REV is provided

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

if [ $# -eq 3 ]; then
    origBranch=`git branch -a | fgrep '*' | sed -e 's#* ##'`

    # stash any unsaved changes (so they aren't merged into our temporary branch)
    numChanges=`git s | fgrep -c 'modified:'`
    if [ $numChanges -gt 0 ]; then
        trap 'echo "Warning: changed files may have been stashed away; try git stash list"; exit 1' 2
        git stash save

        # try to gracefully cleanup on Ctrl-C before exiting
        trap 'echo Warning: unstashing changes on Ctrl-C; git checkout $origBranch; git stash pop > /dev/null; git branch -D $tmpBranch; exit 1' 2
    fi

    # create a temporary branch which includes commits up to the specified revision
    rev=$3
    tmpBranch=tmp$rev
    git branch $tmpBranch $rev
    git checkout $tmpBranch
fi

# build and copy the binary
dir=`dirname $src`
name=`basename $src`
make -C $dir $name
cp $src $dst

if [ $# -eq 3 ]; then
    # cleanup the temporary branch
    git checkout $origBranch
    git branch -D $tmpBranch

    # restore stashed changes
    if [ $numChanges -gt 0 ]; then    
        git stash pop > /dev/null
        echo "Restored stashed changes"
    fi
fi
