LOG_FILE=/config/shell/cafe.log
touch $LOG_FILE
echo "`date` : début du script" >> $LOG_FILE
python ./switchbot-cmd.py E3:07:07:E3:A8:89 press
echo "`date` : fin du script" >> $LOG_FILE
