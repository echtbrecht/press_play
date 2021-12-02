@echo off
echo Copy files to remote
pscp -r -pw kobetakesover C:\Users\brech\PycharmProjects\press_play\docker  pi@Venus:/home/pi/Desktop/pressplay

echo Build Compose
putty.exe -ssh pi@Venus -pw kobetakesover -m ssh_commands.txt