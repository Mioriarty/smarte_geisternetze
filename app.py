import multiprocessing
import os
from tkinter import *
from tkinter import filedialog
import xtf_png
from opencv_playground import loopOverImages
from findingProcessor import processFindings
from PIL import ImageTk, Image
import threading
import shutil
from marker2shp import marker2shp

# selected xtf file names will be populated into this array
files_selected = []
# runningThread = None

##### Functions definitions for GUI #####

# open file browser, lists selected files in file array
# global variable defined outside function, call it by global
def browseFiles():
    global files_selected

    filenames = filedialog.askopenfilenames(initialdir="/",
                                            title="Select a .xtf File",
                                            filetypes=[("eXtendedTritonFormat",
                                                        "*.xtf")])
    files_selected += filenames
    # eliminate double-selected files
    files_selected = list(dict.fromkeys(files_selected))

    # set process state to normal if file(s) are selected
    if len(files_selected) != 0:
        start_process.configure(state="normal")
    # update label text
    build_label_text()

# text that appears in label for selected files
def build_label_text():
    selected_files_text = str(len(files_selected)) + " files selected: "
    for fileloc in files_selected:
        filename = fileloc.split('/')[-1]
        selected_files_text = selected_files_text + "\n" + filename
    selected_files_label.configure(text=selected_files_text)

# multithreading processing
def start_processing():
    runningThread = threading.Thread(target=processing, args=(start_process, status_label,))
    runningThread.start()
    start_process.configure(state='disabled')

# starts process when pressing enter
# checks if button is not disabled (check state is normal)
def press_enter(event=None):
    if start_process.cget('state') == 'normal':
        start_processing()

# needs start and process state label as input
# check if directory/folder structure is correct (out, temp folders there, if not, create it)
def processing(start_process_button, status_label):
    if not os.path.isdir('out'):
        os.mkdir(path='out')
    if not os.path.isdir('temp'):
        os.mkdir(path='temp')

# this will be done fr every file selected:
# if out/temp exists, delete and create new, empty
# create folder according to xtf filename
    for file in files_selected:
        foldername = file.split('/')[-1].split('.')[0]
        out_folder_loc = 'out/' + foldername
        temp_folder_loc = 'temp/' + foldername

        # delete folder despite there's stuff in it (shutil rmtree)
        if os.path.isdir(out_folder_loc):
            try:
                shutil.rmtree(out_folder_loc)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        os.mkdir(path=out_folder_loc)
        if os.path.isdir(temp_folder_loc):
            try:
                shutil.rmtree(temp_folder_loc)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        os.mkdir(path=temp_folder_loc)

        # place status label (.grid), display text status
        status_label.grid(column=4, columnspan=4, row=1, padx=10, sticky='e')
        status_label.configure(text='{}\nReading xtf file and slicing... (1/3)'.format(foldername))

        # calls funtion that does the slicing of .xtf into .png
        slice_name = temp_folder_loc + '/' + foldername + '.png'
        xtf_png.xtf2png(file, slice_name, True, True)
    
        # display text status
        status_label.configure(text='{}\nFinding anomalies... (2/3)'.format(foldername))

        # loops over sliced .pngs (opencv_playground.py) 
        # and do filtering/edge detection, creating marker files, images (findingProcessor.py)
        findings = loopOverImages(
            temp_folder_loc + '/')
        # display process state
        status_label.configure(text='{}\nCreating output files... (3/3)'.format(foldername))
        processFindings(findings, file, out_folder_loc)

        # convert/export xml markers to excel
        marker2shp(out_folder_loc + "/marker.xml", out_folder_loc +
                   "/marker.shp", out_folder_loc + "/marker.xlsx")

    # put button/s to state normal again, display 'Done' msg
    start_process_button.configure(state='normal')
    status_label.configure(text='Done!')


# if button 'delete' pressed, empties array of selectied .xtf files, puts state to disabled
def delete_selection():
    global files_selected

    files_selected = []
    start_process.configure(state='disabled')
    build_label_text()

# run script/start GUI
if __name__ == '__main__':
    multiprocessing.freeze_support()

    # library for GUI
    root = Tk()

    # add title/icon, adjust etc to GUI
    root.title('Ghostnetbusters')
    ico = Image.open('ghostnetbusters.jpg')

    # conert .jpg to .ico
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(False, photo)

    # GUI window size, not resizable
    root.geometry("539x360")
    root.resizable(False, False)
    # root.configure(background='darkturquoise')

    # add background image -> change, not free to use
    bg_img = Image.open('bg.jpg')
    bg = ImageTk.PhotoImage(bg_img)
    label = Label(root, image=bg)
    label.place(x=0, y=0)

    # create buttons to do some action and add function to it
    # functions are defined above
    # browse for files
    find_files = Button(root, text="Browse Files",
                        command=browseFiles, height=2, bg='#567', fg='White')

    # create grid to place buttons
    find_files.grid(column=1, row=1, sticky='w', padx=10, pady=10)

    # run process/script to screen xtf files
    start_process = Button(root, text="Find",
                           command=start_processing, bg="green", fg='White', height=2, width=10, state='disabled')
    start_process.grid(column=3, row=1, padx=10, sticky='w')

    # press enter to start
    root.bind('<Return>', press_enter)

    # delete selection of browsed files
    delete_button = Button(root, text='Delete Selection',
                           command=delete_selection, bg="red", fg='White', height=2)
    delete_button.grid(column=2, row=1, pady=10)

    # lists text with selected files
    selected_files_label = Label(root,
                                 text="",
                                 width=0, height=4,
                                 fg="blue",
                                 anchor='w',
                                 justify=CENTER)

    # creates above text in array
    build_label_text()
    selected_files_label.grid(columnspan=3, row=2, padx=10, sticky='w')

    # adds processing status (print messages)
    status_label = Label(root,
                        text="",
                        width=0, height=4,
                        fg="blue",
                        anchor='w',
                        justify=CENTER)

    # all things added to root will be run(?)
    mainloop()
    # pyinstaller -F --noconsole  app.py