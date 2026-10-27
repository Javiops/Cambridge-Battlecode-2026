# score.sh TAG BOT: wins of BOT in res/TAG.log
grep -a "WIN (" res/$1.log | grep -c "($2)"; grep -ac "WIN (" res/$1.log
