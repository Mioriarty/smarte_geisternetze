from enum import auto
import os
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Style
import xtf_png
from opencv_playground import loopOverImages
from findingProcessor import processFindings
from PIL import ImageTk, Image
import threading
files_selected = []
runningThread = None


def browseFiles():
    global files_selected

    filenames = filedialog.askopenfilenames(initialdir="/",
                                            title="Select a .xtf File",
                                            filetypes=[("eXtendedTritonFormat",
                                                        "*.xtf")])
    files_selected += filenames
    files_selected = list(dict.fromkeys(files_selected))
    if len(files_selected) != 0:
        start_process.configure(state="normal")
    build_label_text()


def build_label_text():
    selected_files_text = str(len(files_selected)) + " files selected: "
    for fileloc in files_selected:
        filename = fileloc.split('/')[-1]
        selected_files_text = selected_files_text + "\n" + filename
    selected_files_label.configure(text=selected_files_text)


def start_processing():
    global runningThread

    if runningThread == None or runningThread.is_alive():
        runningThread = threading.Thread(target=processing)
        runningThread.start()
        start_process.configure(state='disabled')


def processing():
    if not os.path.isdir('application\\out'):
        os.mkdir(path='application\\out')
    if not os.path.isdir('application\\temp'):
        os.mkdir(path='application\\temp')

    for file in files_selected:
        foldername = file.split('/')[-1].split('.')[0]
        out_folder_loc = 'application\\out\\' + foldername
        temp_folder_loc = 'application\\temp\\' + foldername

        if not os.path.isdir(out_folder_loc):
            os.mkdir(path=out_folder_loc)
        if not os.path.isdir(temp_folder_loc):
            os.mkdir(path=temp_folder_loc)

        slice_name = temp_folder_loc + '\\' + foldername + '.png'
        xtf_png.xtf2png(file, slice_name, True, True)

        findings = loopOverImages(
            temp_folder_loc + '\\')
        processFindings(findings, file, out_folder_loc)
    start_process.configure(state='normal')


def delete_selection():
    global files_selected

    files_selected = []
    start_process.configure(state='disabled')
    build_label_text()


if __name__ == '__main__':
    root = Tk()
    root.title('Geisternetz Finder')
    root.geometry("539x360")
    root.resizable(False, False)
    root.configure(background='darkturquoise')
    bg_img = Image.open('application\\bg.png')
    bg = ImageTk.PhotoImage(bg_img)
    label = Label(root, image=bg)
    label.place(x=0, y=0)
    find_files = Button(root, text="Browse Files",
                        command=browseFiles, height=2, bg='#567', fg='White')
    find_files.grid(column=1, row=1, sticky='w', padx=10, pady=10)

    photo = ImageTk.PhotoImage(Image.open('application\\net.png'))

    start_process = Button(root, text="Find",
                           command=start_processing, bg="green", fg='White', height=2, width=10, state='disabled')
    start_process.grid(column=3, row=1, padx=10, sticky='w')

    delete_button = Button(root, text='Delete Selection',
                           comman=delete_selection, bg="red", fg='White', height=2)
    delete_button.grid(column=2, row=1, pady=10)

    selected_files_label = Label(root,
                                 text="",
                                 width=0, height=4,
                                 fg="blue",
                                 anchor='w',
                                 justify=CENTER)
    build_label_text()
    selected_files_label.grid(columnspan=3, row=2, padx=10, sticky='w')

    mainloop()
