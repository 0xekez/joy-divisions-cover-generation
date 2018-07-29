# take filenames and output filename
def images_to_video(filenames, output, fps):
    '''
    builds a video from a list of images
    IN: list of filenames for images, where to output, , frames per second
    OUT: filename for output video
    '''
    from cv2 import VideoWriter, VideoWriter_fourcc, imread, destroyAllWindows

    print("CREATING VIDEO")
    fourcc = VideoWriter_fourcc(*'mp4v')
    vid = None
    for file in filenames:
        img = imread(file)
        # now that we have an image we can setup vid
        if vid is None:
            size = img.shape[1], img.shape[0]
            print("SIZE:\t{}".format(size))
            # false for is_color
            vid = VideoWriter(output, fourcc, float(fps), size)

        vid.write(img)

    vid.release()
    destroyAllWindows()
    return output


def add_audio(video, audio):
    '''
    combines audio and visual channels into new .mp4
    IN: video filename, audio filename
    OUT: saves a video to auio_+video_filename
    WARNING: this is where code is bad, you need ffmpeg installed for it to work
    '''
    import subprocess
    print("ADDING AUDIO")
    cmd = "ffmpeg -i {} -i {} -vcodec copy audio_{}".format(video, audio, video)
    print("CALLING\t{}".format(cmd))
    subprocess.call(cmd, shell=True)


# duration specifies the number of seconds between frames
# lowest supported value is 0.1 I think
def create_gif(filenames, output, duration):
    '''
    IN: filenames to build gif from, where to save gif, time between frames
    OUT: saves a .gif to the requested output
    '''
    import imageio
    print("BUILDING GIF")
    images = []
    for file in filenames:
        images.append(imageio.imread(file))
    imageio.mimsave(output, images, duration=duration)


def video_from_folder(folder, output, fps):
    '''
    builds a video from all the .pngs in a folder
    IN: folder, output location, frames per second
    OUT: save location
    '''
    print("GETTING .PNG FROM:\t{}".format(folder))
    import os
    filenames = os.listdir(folder)

    for fichier in filenames[:]:  # filelist[:] makes a copy of filelist.
        if not(fichier.endswith(".png")):
            filenames.remove(fichier)

    from cv2 import VideoWriter, VideoWriter_fourcc, imread, destroyAllWindows

    print("CREATING VIDEO")
    fourcc = VideoWriter_fourcc(*'mp4v')
    vid = None
    for file in filenames:
        img = imread("{}/{}".format(folder, file))
        # now that we have an image we can setup vid
        if vid is None:
            size = img.shape[1], img.shape[0]
            print("SIZE:\t{}".format(size))
            # false for is_color
            vid = VideoWriter(output, fourcc, float(fps), size)

        vid.write(img)

    vid.release()
    destroyAllWindows()
    return output

# output = video_from_folder('covers', 'ultralight.mp4', 30)
# add_audio("ultralight.mp4", "ultralight.wav")
