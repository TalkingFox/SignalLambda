$mainFile = Get-ChildItem ../src/main.py
$configFile = Get-ChildItem ../src/config.py
$wordsFile = Get-ChildItem ../src/words.txt
$packages = get-childItem ../dev/Lib/site-packages/**/


$files = @()
$files += $mainFile
$files += $configFile
$files += $wordsFile
$files += $packages
write-output "Packaged core files"
write-output "Packaging dependencies"
$files | Compress-Archive -DestinationPath .\signal.zip