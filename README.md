# Joy Division Cover Generation
![example](example.gif)


## How It Works
1. Grab amplitude date from .wav file
2. Use Pillow and some math to build images
3. Merge images to video with open cv2
4. Merge audio and video with ffmpeg - you'll need ffmpeg installed to run the code

## How To Use
1. Download to your computer
2. The params.py file has all the paramaters for the image you can adjust
3. Point the params.py file at the .wav file you want to build a video out of
4. Run waveform.py

## Notes About The Code
If I had thought about naming my files things that made sense earlier the files would be names differently, but I didn't so here is a breif explanation of where everything is:

`waveform.py` has the meat of the program. It does the image generation and calls all the other files.

`noise_gen.py` handles the stuff that doesn't respond to the amplitude data. It adds all the trailing lines to the data.

`images_to_video.py` handles converting the generated images into videos and gifs. The code is currently setup to output a .mp4 but with some minor mods it can ouput a gif.
