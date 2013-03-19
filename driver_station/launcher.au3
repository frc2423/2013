
$python = "C:\Python27\python.exe"
;$python = "C:\Python27\pythonw.exe"
$dir = "C:\kwarqs-workspace\2013\driver_station"
$options = "--robot-ip 10.24.23.2 --camera-ip 10.24.23.11 --competition"

$sdkdir = EnvGet("GSTREAMER_SDK_ROOT_X86")
$oldpath = EnvGet("PATH")

EnvSet("PYTHONPATH", $sdkdir & "\lib\python2.7\site-packages")
EnvSet("PATH", $sdkdir & "\bin;" & $oldpath)

Run($python & " " & $dir & "\main.py " & $options, $dir)
