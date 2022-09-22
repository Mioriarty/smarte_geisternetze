import os
from tkinter import *
from tkinter import filedialog
import xtf_png

files_selected = []
count_files_selected = 0
isRunning = False


def browseFiles():
    global files_selected
    global count_files_selected

    filenames = filedialog.askopenfilenames(initialdir="/",
                                            title="Select a .xtf File",
                                            filetypes=[("eXtendedTritonFormat",
                                                        "*.xtf")])
    files_selected += filenames
    files_selected = list(dict.fromkeys(files_selected))
    count_files_selected = len(files_selected)
    build_label_text()


def build_label_text():
    selected_files_text = str(count_files_selected) + " files selected: "
    for fileloc in files_selected:
        filename = fileloc.split('/')[-1]
        selected_files_text = selected_files_text + "\n" + filename
    selected_files_label.configure(text=selected_files_text)


def start_processing():
    if not isRunning:
        for file in files_selected:
            foldername = file.split('/')[-1].split('.')[0]
            os.mkdir(path=foldername)
            slice_name = foldername + '\\' + foldername + '.png'
            xtf_png.xtf2png(file, slice_name, True, True)


root = Tk()
root.title('Geisternetz Finder')
root.geometry("500x250")
root.resizable(False, False)

find_files = Button(root, text="Browse Files", command=browseFiles)
find_files.grid(column=1, row=1, sticky='w')

start_process = Button(root, text="Analyze", command=start_processing)
start_process.grid(column=1, row=2, sticky='w')

selected_files_label = Label(root,
                             text="",
                             width=100, height=4,
                             fg="blue",
                             anchor='w',
                             justify=LEFT)
build_label_text()
selected_files_label.grid(column=1, row=3, sticky='nw')

mainloop()
