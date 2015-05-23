This script asks an Emoncms server for an energy value. If the value is high, ie if the monitored device
draws power, a notice is sent to a Smartphone.
The monitored device in this case is a washing maching, and actions are taken to just send a notice
when the machine is started and when the wash is done. A washer draws power irregularly, so counters are
used to make sure not to send notifications when the washer is idle during the wash cycle.
Notifications are sent via NMA, http://www.notifymyandroid.com.
To use this service, an account is needed. This account gives a developer key, which is stored in the file "mydeveloperkey".

The script can be started from /etc/rc.local by adding these lines to 
the end of rc.local, before the line "exit 0":

cd /home/pi/nma/
python logpower.py &




