@echo off
cls
REM *******************************************
REM **Setup VPN registry configuration and Route**
REM *******************************************

REG ADD HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\PolicyAgent /v AssumeUDPEncapsulationContextOnSendRule /t REG_DWORD /d 2 /f
START regedit
route -p add 192.31.0.0 mask 255.255.250.0 0.0.0.0
