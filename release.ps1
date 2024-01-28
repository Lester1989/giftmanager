$gitstatus = git status --porcelain
# Check if Docker engine is running
if (!(docker ps)) {
    Write-Host "Docker engine is not running. Please start Docker engine and try again."
    exit -1
}
Write-Host "Docker engine is running"

if ($gitstatus) {
    Write-Host "Please Commit and Push your local changes before running this script"
    exit -1
}
Write-Host "Git status is clean"

# update version
poetry version patch

# Get the file path
$filePath = "version.txt"

# Get the new version number
$newVersion = poetry version --short
$projectName = "friendship"

# Write the new version number to the file
Set-Content $filePath $newVersion

foreach ($a in $(git describe --tags --abbrev=0)) {
    $logRange = $a+"..HEAD"
    $latesttag = $a
}
$changelog = git log --pretty=format:"%s %B" $logRange
Write-Host "Version updated to $newVersion"

Write-Host "Changes since $latesttag : "
ForEach ($line in $changelog.Split("`n")) {
    Write-Host $line
}
if ($changelog.Length -eq 0) {
    Write-Host "No changes since last tag, exiting"
    git checkout .
    exit -1
}
git add .
git commit -m "Incremented version to $newVersion ChangeLog:$changelog"
git push
git tag -a "$newVersion" -m "Incremented version to $newVersion ChangeLog:$changelog" 
git push --tags



$versionTag = $projectName + ":" +$newVersion
$versionTagLatest = $projectName + ":latest"
docker build --force-rm . -t lukasjaspaert/$versionTag
docker build --force-rm . -t lukasjaspaert/$versionTagLatest

docker push lukasjaspaert/$versionTag
docker push lukasjaspaert/$versionTagLatest
Write-Host "Deployment completed successfully! $versionTag is now available on the registry, rebuilding the stack"


exit 0
# TODO activate hook and check after first build
# Invoke-RestMethod -Uri COMING_SOON -Method POST

Write-Host "Stack rebuild triggered successfully! Checking availablity of the new version"

Start-Sleep -Seconds 5

$url = "friendship.lesterserver.de"
$interval = 2

while ($true) {
    $response = Invoke-WebRequest -Uri $url
    $responseCode = $response.StatusCode
    Write-Host "Response Code: $responseCode"
    
    if ($responseCode -eq 200) {
        break
    }
    
    Start-Sleep -Seconds $interval
}
Write-Host "Woohoo we are live!"

$frames = @(
@"
         
         
         
         
         
         
         
         
                                                       .''.;.
                                                   00  .',.',
                                                  /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
    
    
    
    
    
    
 
 
                                                       .''.;.
                                                   00  .',.',
            \                            /        /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
     
     
     
     
     
     
  
  
                                                       .''.;.
           \                              /        00  .',.',
            \            \               /        /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
     
     
     
     
     
     
  
  
          \                                            .''.;.
           \            \                 /X        00  .',.',
            \            \               /        /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
     
     
     
     
     
     
  
  
        XX\            \                   #           .''.;.
           \            \                 #S#       00  .',.',
            \        \   \               / #      /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
     
     
     
     
     
     
  
        vv            \
       >oo<            \                  $#$          .''.;.
        ^^ \        \   \                $#$#$      00  .',.',
            \        \   \     |         /$#$     /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
       
       
       
       
       
                
    ~@~*~@~     
  ~*~@~*~@~*~     \   \
  ~*~@smd@~*~      \   \       |          #$#$#        .''.;.
  ~*~@~*~@~*~       \   \      |         #$#$#$#   00  .',.',
    ~@~*~@~ \        \   \     |  /      /#$#$#   /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
        
        
        
        
        
                \    X
    ~@~*~@~      \   \         |      
  ~*~@~*~@~*~     \   \        |     /
  ~*~@smd@~*~      \   \       |    /     #$#$#        .''.;.
  ~*~@~*~@~*~       \   \      |   /     #$#$#$#   00  .',.',
    ~@~*~@~ \        \   \     |  /      /#$#$#   /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
         
                               X
                               |
              \     ***        |         X
               \   *****       |        /
                \   ***        |       /
    ~@~*~@~      \   \         |      /
  ~*~@~*~@~*~     \   \        |     /
  ~*~@smd@~*~      \   \       |    /     #$#$#        .''.;.
  ~*~@~*~@~*~       \   \      |   /     #$#$#$#   00  .',.',
    ~@~*~@~ \        \   \     |  /      /#$#$#   /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
                             'o'o'
           XX               o'o'o'o      ^,^,^
             \               'o'o'     ^,^,^,^,^
              \     ***        |       ^,^,^,^,^
               \   *****       |        /^,^,^
                \   ***        |       /
    ~@~*~@~      \   \         |      /
  ~*~@~*~@~*~     \   \        |     /
  ~*~@smd@~*~      \   \       |    /     #$#$#        .''.;.
  ~*~@~*~@~*~       \   \      |   /     #$#$#$#   00  .',.',
    ~@~*~@~ \        \   \     |  /      /#$#$#   /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@,
@"
         .* *.               'o'o'
         *. .*              o'o'o'o      ^,^,^
           * \               'o'o'     ^,^,^,^,^
              \     ***        |       ^,^,^,^,^
               \   *****       |        /^,^,^
                \   ***        |       /
    ~@~*~@~      \   \         |      /
  ~*~@~*~@~*~     \   \        |     /
  ~*~@smd@~*~      \   \       |    /     #$#$#        .''.;.
  ~*~@~*~@~*~       \   \      |   /     #$#$#$#   00  .',.',
    ~@~*~@~ \        \   \     |  /      /#$#$#   /|||  '.,'
_____________\________\___\____|_/______/_________|\/\___||______
"@
)

$interval = 25

foreach ($frame in $frames) {
        Clear-Host
        Write-Host $frame
        Start-Sleep -Milliseconds $interval
}