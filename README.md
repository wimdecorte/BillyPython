# BillyPython
Driving Billy Bass from FileMaker with a Raspberry PI, python version

This is a project from the FileMaker Devcon 2018 (Dallas, TX).
It demonstrates how to read data from FileMaker through the Data API.  Runs on Raspberry Pi with Raspbian, and drives a Billy Bass singing fish.

Uses: https://github.com/davidhamann/python-fmrest as the wrapper around the FMS Data API.

There are 3 branches to this project:
- Master: uses the visemes as returned from AWS Polly to determine when the mouth should move
- AudioSample: uses the amplitude of the audio to determine when the mouth should move
- pacat: aborted attempt to use the 'pacat' command line to listen to the audio as it was played.

The project is packaged a a Visual Studio 2017 project but you do not need to use Visual Studio.  You can use your favorite text editor.

The good stuff is in the "BillyPython" subfolder.
Change the .ini file to point to your server and your file.
Also change the ini file with values that work best for your Billy Bass.  You can use the two test pything scripts to target just the mouth and just the head/body to find out what combination of frequency, speed and duration works best.
