#!/bin/sh
python app.py &

rm database.sqlitedb
cucumber ./tests/features

#LAST_STATE=`tail -1 /tmp/state.txt`
SUCCESS=$?

#echo "LAST STATE: $LAST_STATE"

#if [ $LAST_STATE != $SUCCESS ];then
if [ $SUCCESS != 0 ];then
  say "You broke the build..."
  osascript ./scripts/random_song.scpt &
else
  say "The build is nice and greeeeeeeen"
  open "/Users/stardif/Music/iTunes/iTunes Media/Music/Lesley Gore/Unknown Album/Sunshine, Lollipops, Rainbows.mp3"
fi
#fi


#echo $SUCCESS > /tmp/state.txt
killall python

exit $SUCCESS
