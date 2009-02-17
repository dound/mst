#!/bin/bash
set -o errexit
set -o nounset

CONF="`dirname $0`/conf/tracked_revs"
MAX_SHA1_LEN=10
MAX_COMMIT_MSG_LEN=50

# build the new file by iterating through all revisions in chrono order
function rebuildCONF {
    mytags=$1
    shift

    newCONF=$CONF.new
    echo -e "#Line#\tRev#\tSHA1      \tTags\tFirst Line of Commit Message" > $newCONF
    git-rev-list --reverse --pretty=oneline HEAD > .tmp
    i=0
    j=0
    while read line; do
        sha1=`echo $line | cut -d\  -f1`
        sha1="${sha1:0:$MAX_SHA1_LEN}"

        for tsha1 in $@; do
            if [ "$sha1" = "$tsha1" ]; then
                if [ $1 = $tsha1 ]; then
                    tags=$mytags
                else
                    tags=`fgrep $sha1 $CONF | cut -f4`
                fi
                msg=`echo $line | cut -d\  -f3-`

                if [ ${#msg} -gt $MAX_COMMIT_MSG_LEN ]; then
                    msg="${msg:0:$MAX_COMMIT_MSG_LEN}..."
                fi

                echo -e "$j\t$i\t$sha1\t$tags\t$msg" >> $newCONF
                j=$(($j + 1))
                break
            fi
        done

        i=$(($i + 1))
    done < .tmp
    rm -f .tmp
    mv $newCONF $CONF
}

if [ $# -lt 1 ]; then
    echo "usage: %prog [options] COMMAND [ARGS]"
    echo "Simple interface to which revisions we are tracking for performance reasons."
    echo ""
    echo "Commands:"
    echo "  add REV [tags] - starts tracking git revision REV"
    echo "  del REV [tags] - stops tracking git revision REV"
    echo "  list [tag_re]  - lists revisions being tracked with (if specified) tags matching the regular expression tag_re"
    exit 1
fi

if [ $1 = "add" -o $1 = "del" ]; then
    if [ $# -lt 2 ]; then
        rev=HEAD
    else
        rev="$2"
    fi
    if [ $# -lt 3 ]; then
        tags=
    else
        tags=`echo $3 | sed -e 's# #_#g'`
    fi

    mysha1=`git log $rev | head -n 1 | sed -e 's#commit ##'`
    mysha1="${mysha1:0:$MAX_SHA1_LEN}"

    touch $CONF
    cat $CONF | cut -f3 | fgrep -q $mysha1 > /dev/null 2> /dev/null && exist=1 || exist=0

    if [ $1 = "add" ]; then
        if [ $exist -eq 1 ]; then
            echo "$mysha1 is already being tracked"
        else
            rebuildCONF "$tags" $mysha1 `cat $CONF | cut -f3`
            msg=`fgrep $mysha1 $CONF | cut -f4-`
            echo "$mysha1 is now being tracked: $msg"
        fi
    else
        if [ $exist -eq 0 ]; then
            echo "$mysha1 was not being tracked"
        else
            oldmsg=`fgrep $mysha1 $CONF | cut -f4-`
            rebuildCONF `fgrep -v $mysha1 $CONF | cut -f3`
            echo "$mysha1 is no longer being tracked: $oldmsg"
        fi
    fi
elif [ $1 = "list" ]; then
    if [ $# -lt 2 ]; then
        cat $CONF
    else
        # tag filtering
        tf=$2
        while read line; do
            tags=`echo $line | cut -f4`
            echo $tags | egrep -q "$tf" > /dev/null 2> /dev/null && exist=1 || exist=0
            if [ $exist -eq 1 ]; then
                echo "$line"
            fi
        done < $CONF
    fi
else
    echo "unknown command: $1"
    exit 1
fi
