$mainFile = Get-ChildItem ../src/main.py
$configFile = Get-ChildItem ../src/config.py
$packages = get-childItem ../dev/Lib/site-packages/**/


$files = @()
$files += $mainFile
$files += $packages
$files | Compress-Archive -DestinationPath .\signal.zip