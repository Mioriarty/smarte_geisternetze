from PIL import Image
import glob,os

def saveImgFromDir2png(url):
    files = glob.glob(url + "*.gif") 

    for imageFile in files:
        print()
        filepath,filename = os.path.split(imageFile)
        filterame,exts = os.path.splitext(filename)
        print ("Processing: " + imageFile,filterame)
        im = Image.open(imageFile)
        im.save( './res/training_gif_and_png'+filterame+'.png','PNG')

if __name__ == '__main__':
    saveImgFromDir2png("./res/training_gif_and_png")