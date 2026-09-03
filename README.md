This Repo is for SDV Asset Development



Dependent Tools
---------------
To install all the dependencies run below command from repo
`./tools/scripts/setupEnv.sh `
To Build
--------
cd buildScript
make the shell script executable using: chmod +x build_adasApp.sh
 
to Build: 
    ./build_adasApp.sh
    ./build_bmsApp.sh


How to Run
---------

Line Departure Warning App:  `./../out/executables/appAdas/ldw_camera ../simRepo/adas/simDriver.mp4`

Driver Monitoring App:  `./../out/executables/appAdas/dmsApp ../simRepo/adas/simDriver.mp4`

Battery Management App: `./../out/executables/appBms/bms_status_service ../simRepo/batteryData/Processed`

Edge Cloud
----------
`cd appEdge`

In Terminal 1 (for server): `python3 cloud.py`
in Terminal 2 (for Client): `python3 client.py`