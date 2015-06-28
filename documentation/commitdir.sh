#!/bin/sh
set -e

# Commit the contents of the given directory, to the
# named branch without modifiying the index or
# working directory
#
# cf. https://git-scm.com/book/en/v2/Git-Internals-Git-Objects

usage() {
  echo "$0 <branch> <directory>"
  exit 1
}

die() {
  echo "$1" >&2
  exit 1
}

branch="$1"
indir="$2"

[ "$branch" -a -d "$indir" ] || usage

case "$brancH" in
refs/*) ;;
*) branch="refs/heads/$branch";;
esac

echo "Working against branch $branch"

# Detect existing head for the requested branch
#PARENT=$(git rev-parse --verify "$branch") || true

# Always replace existing history
PARENT=

echo "Parent rev $PARENT"

BASEDIR="$(git rev-parse --show-toplevel)"
export GIT_DIR="$BASEDIR/.git"

# No strictly required, but
[ -d "$GIT_DIR" ] || die "Failed to detect GIT_DIR=$GIT_DIR"

# Use a different index file name to avoid clobbering the default $GIT_DIR/index
export GIT_INDEX_FILE="$GIT_DIR/dirindex"

[ -e "$GIT_INDEX_FILE" ] && die "index file already exists $GIT_INDEX_FILE"

# ensure that our special index file is removed on exit
trap "rm -f $GIT_INDEX_FILE" TERM INT HUP EXIT

( cd "$indir" && git add . )

if [ "$PARENT" ]
then
  if [ -z "$(git diff-index --cached --stat "$PARENT")" ]
  then
    echo "No changes to commit"
    exit 0
  fi
fi

TREE="$(git write-tree)"
echo "tree $TREE"

[ "$PARENT" ] && PARENT="-p $PARENT"

COMMIT="$(git commit-tree -m 'by commitdir.sh' $PARENT "$TREE")"
echo "commit $COMMIT"

git update-ref "$branch" "$COMMIT"

echo "Updated $branch"
