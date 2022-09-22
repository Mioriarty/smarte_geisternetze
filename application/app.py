from enum import auto
import os
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Style
import xtf_png
# äimport findingProcessor

files_selected = []
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
    global isRunning

    if not isRunning:
        if not os.path.isdir('application\\out'):
            os.mkdir(path='application\\out')
        isRunning = True
        for file in files_selected:
            foldername = file.split('/')[-1].split('.')[0]
            os.mkdir(path='application\\' + foldername)
            slice_name = 'application\\' + foldername + '\\' + foldername + '.png'
            xtf_png.xtf2png(file, slice_name, False, True)

            findings = []
            #findingProcessor.processFindings(findings, file, 'application\\out')

    isRunning = False


def delete_selection():
    global files_selected

    files_selected = []
    start_process.configure(state='disabled')
    build_label_text()


#Root
root = Tk()
root.title('Geisternetz Finder')
root.geometry("500x250")
root.resizable(False, False) 
root.configure(background='darkturquoise')

# Buttons
style = Style()
style.configure('TButton', font =
               ('calibri', 20, 'bold'),
                    borderwidth = '4')
style.map('TButton', foreground = [('active', '!disabled', 'green')],
                     background = [('active', 'black')])
find_files = Button(root, text="Browse Files", command=browseFiles)
find_files.grid(column=1, row=1, sticky='w',pady = 10, padx=10)

start_process = Button(root, text="Analyze",
                       command=start_processing, state='disabled')
start_process.grid(column=3, row=1,padx = 10,sticky='w')

delete_button = Button(root, text='Delete Selection',
                       comman=delete_selection, bg="red")
delete_button.grid(column=2, row=1,pady = 10)

selected_files_label = Label(root,
                             text="",
                             width=0, height=4,
                             fg="blue",
                             anchor='w',
                             justify=CENTER)
build_label_text()
selected_files_label.grid(columnspan=3, row=2,padx=10)

mainloop()
