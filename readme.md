## Signal Server Example ##

This is an example WebRTC server signal implemented using Amazon Lambda. This is useful for managing WebRTC connections between two or more parties.

## Project Notes
This was developed in Python, and for Lambda this means that all package requirements must be bundled with the project. Since I use virtualenv, I'm able to package the dependencies using the directory that creates. My `package.ps1` file reflects this process.