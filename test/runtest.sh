#!/bin/bash
set -e

die() {
  echo "$1"
  exit 1
}

EPICS_BASE=${EPICS_BASE:=/usr/lib/epics}

[ -r "${EPICS_BASE}/dbd/base.dbd" ] || die "Can't find EPICS base"

GET=../getpvs
APPLY=../applypvs

install -d output

echo "Testing getpvs"

# Checks that getpvs produces the expected output given known input

echo "db"

$GET -I "${EPICS_BASE}/dbd" -I input -o output/as-db.pot base.dbd save_restoreStatus.db

echo "edl"

$GET -m edl -I input -o output/as-edl.pot \
 save_restoreStatus.edl save_restoreStatus_more.edl \
 save_restoreStatus_tiny.edl

echo "opi"

$GET -m opi -I input -o output/bnl-opi.pot cameraview.opi drfm-main.opi

# remove generated date stamps before compare

sed -i -e '/-Date/d' output/as-db.pot output/as-edl.pot output/bnl-opi.pot


echo "Testing applypvs"

# Checks that applypvs produces the expected output given known input
# Does forward and then reverse operations to ensure
# that the round trip still matches the original

install -d output/forward/
install -d output/reverse/

echo "db"

$APPLY -F -i input/as-db.po -o output/forward \
 input/save_restoreStatus.db

echo "edl"

$APPLY -m edl -F -i input/as-db.po -o output/forward \
 input/save_restoreStatus.edl input/save_restoreStatus_more.edl \
 input/save_restoreStatus_tiny.edl input/softGlue_AND_debug.edl

echo "opi"

$APPLY -m opi -F -i input/bnl-opi.po -o output/forward \
 input/drfm-main.opi input/cameraview.opi

for ff in save_restoreStatus.edl save_restoreStatus_more.edl \
          save_restoreStatus_tiny.edl softGlue_AND_debug.edl \
          save_restoreStatus.db drfm-main.opi cameraview.opi
do
  diff -u input/$ff output/forward/$ff > output/$ff.diff || true
done

echo "Reverse db"

$APPLY -F -R -i input/as-db.po -o output/reverse \
 output/forward/save_restoreStatus.db

echo "Reverse edl"

$APPLY -m edl -F -R -i input/as-db.po -o output/reverse \
 output/forward/save_restoreStatus.edl \
 output/forward/save_restoreStatus_more.edl \
 output/forward/save_restoreStatus_tiny.edl \
 output/forward/softGlue_AND_debug.edl

echo "Reverse opi"

$APPLY -m opi -F -R -i input/bnl-opi.po -o output/reverse \
 output/forward/drfm-main.opi \
 output/forward/cameraview.opi

echo "Comparing with expectations"

for ff in as-db.pot as-edl.pot bnl-opi.pot \
 forward/save_restoreStatus.edl \
 forward/save_restoreStatus_more.edl \
 forward/save_restoreStatus_tiny.edl \
 forward/softGlue_AND_debug.edl \
 forward/drfm-main.opi \
 forward/cameraview.opi \
 reverse/save_restoreStatus.edl \
 reverse/save_restoreStatus_more.edl \
 reverse/save_restoreStatus_tiny.edl \
 reverse/softGlue_AND_debug.edl \
 reverse/drfm-main.opi \
 reverse/cameraview.opi
do
  echo "Compare $ff"
  if ! diff expected/$ff output/$ff &>/dev/null
  then
    echo "  Differs"
    diff -u expected/$ff output/$ff || true
    printf "\n\n\n"
  else
    echo "  OK"
  fi
done
