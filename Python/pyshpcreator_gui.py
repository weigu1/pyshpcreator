from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from time import strftime, localtime
import queue

class GUI:
    def __init__(self, flags_2_main, queue_2_main, queue_2_gui):
        self.standard_font = ["Helvetica", 12, "bold"]
        self.textbox_font = ["Courier", 12, "bold"]
        self.welcome_txt = "Hello to PYSHPCREATOR V3.0 (2024)"
        self.hp_dir_names = [""]
        self.quick_links_files = [""]
        self.check_links_dirs = [""]
        self.flags_2_main = flags_2_main
        self.queue_2_main = queue_2_main
        self.queue_2_gui = queue_2_gui
         # Dictionary for widget texts (inside:message)
        self.widget_texts_dict = {"PYthon Simple HomePage CREATOR": "",       # 0, 0 title
                                  "Create homepage!" : "Creating homepage!",  # 1, 1 button
                                  "Homepage directory" : "",                  # 2, 1 label
                                  "Create quick links": "Create quick links", # 3, 2 button
                                  "Quick links file" : "",                    # 4, 2 label
                                  "Check links": "Check links",               # 5, 3 button
                                  "Check links folder" : "",                  # 6, 3 label
                                  "Upload homepage!" : "Uploading homepage!", # 7, 4 button
                                  "Clear Textwindow" : "",                    # 8, 5 button
                                  "Quit" : ""}                                # 9, 6 button
        self.widget_texts_list = list(self.widget_texts_dict.keys())
        self.progress_char= '.'
        self.padx = 5
        self.pady = 5
        self.ipady = 7
        self.button_width_wide = 45
        self.button_width_normal = 30
        self.button_width_small = 15
        self.text_win_width = 100
        self.text_win_height = 20
        self.end = END

    def set_flag(self, flag, message):
        flag.set()
        self.txt_win.insert(self.end, f"{message}\n")

    def check_queue_from_main(self):
        try:

            message = self.queue_2_gui.get_nowait()
            if len(message) == 1:
                self.txt_win.insert(self.end, message)
            else:
                self.txt_win.insert(self.end, f"{message}\n")
            self.txt_win.see("end")
            message = message.split('\n')
            if message[0] == "Homepage names detected:":
                self.hp_dir_names = message[1:]
                #print(self.hp_dir_names)
                try:
                    self.combobox_hpdir['values'] = self.hp_dir_names
                    self.combobox_hpdir.current(0)
                except:
                    pass
            if message[0] == "File_list_4_quick_links:":
                self.quick_links_files = message[1:]
                #print(self.quick_links_files)
                try:
                    self.combobox_quick_links['values'] = self.quick_links_files
                    self.combobox_quick_links.current(0)
                except:
                    pass

            if message[0] == "Dir_list_4_links_2_check:":
                self.check_links_dirs = message[1:]
                #print(self.check_links_dirs)
                try:
                    self.combobox_check_links['values'] = self.check_links_dirs
                    self.combobox_check_links.current(0)
                except:
                    pass
        except queue.Empty:
            pass
        self.mainWin.after(100, self.check_queue_from_main)  # Check the queue again after 100ms

    def on_butt_create_pressed(self):
        text = self.hp_dir_name.get()
        index = self.combobox_hpdir.current()
        self.txt_win.insert(self.end, f"Chosen homepage directory name: {text}\n")
        text = f"hp_dir_name:\n{text}\n{index}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main
        self.set_flag(self.flags_2_main[0], self.widget_texts_dict[self.widget_texts_list[2]])

    def on_butt_quick_links_pressed(self):
        text = self.quick_links_file.get()
        index = self.combobox_quick_links.current()
        self.txt_win.insert(self.end, f"Chosen quick links file name: {text}\n")
        text = f"quick_links_file_name:\n{text}\n{index}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main
        self.set_flag(self.flags_2_main[1], self.widget_texts_dict[self.widget_texts_list[3]])

    def on_butt_check_links_pressed(self):
        text = self.check_links_dir.get()
        index = self.combobox_check_links.current()
        #self.txt_win.insert(self.end, f"Chosen check links directory name: {text}\n")
        text = f"check_links_dir_name:\n{text}\n{index}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main
        self.set_flag(self.flags_2_main[2], self.widget_texts_dict[self.widget_texts_list[5]]),

    def clear_textwindow(self):
        self.txt_win.delete(1.0, END)

    def on_closing(self):
        self.flags_2_main[4].set()  # Set the exit flag to stop the main loop
        self.mainWin.destroy()

    def init_ttk_styles(self):
        self.s = ttk.Style()
        #frames
        self.s.configure("all.TFrame",
                         background="lightgrey")
        self.s.configure("test.TFrame",
                         background="grey")
        #widgets
        self.s.configure("default.TLabel", background="lightgrey",
                         font=self.standard_font)
        self.s.configure("time.TLabel",
                         background="lightgrey",
                         font=self.standard_font)
        self.s.configure("default.TEntry",
                         background="lightgray",
                         font=self.standard_font)
        self.s.configure("default.TCombobox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("default.TSpinbox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("important.TButton",
                         background="lightgreen",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.configure("default.TButton",
                         background="lightgrey",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.map("important.TButton",
                   background = [("active", 'lawngreen')])

    def FontSizeUpdate(self):
        FSize = self.FSize.get()
        self.standard_font[1]=int(FSize)
        self.textbox_font[1]=int(FSize)
        print(self.standard_font)
        self.s.configure("default.TLabel", font=self.standard_font)
        self.s.configure("time.TLabel", font=self.standard_font)
        self.s.configure("default.TEntry", font=self.standard_font)
        self.s.configure("default.TButton", font=self.standard_font)
        self.s.configure("important.TButton", font=self.standard_font)
        self.s.configure("default.TCombobox", font=self.standard_font)
        self.s.configure("default.TSpinbox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=int(FSize)*1.5)
        self.txt_win.config(font=self.textbox_font)
        self.combobox_hpdir.config(font=self.standard_font)
        self.combobox_quick_links.config(font=self.standard_font)
        self.combobox_check_links.config(font=self.standard_font)
        self.spinb_fontsize.config(font=self.standard_font)

    def UpdateTime(self):
        ftime = strftime("%d.%m.%y %H:%M:%S", localtime())
        rtctime = strftime("%Y %m %d %H %M %S", localtime())
        intyear = str(int(rtctime[0:4])-1892)
        rtctimecorr = intyear[0:4]+rtctime[4:]
        self.label_time['text'] = ftime
        self.label_time.after(1000, self.UpdateTime)

    def run(self):
        self.mainWin = Tk()
        self.init_ttk_styles()
        self.FSize = StringVar()
        self.FSize.set("12")
        self.hp_dir_name = StringVar()
        self.hp_dir_name.set(self.hp_dir_names[0])
        self.check_links_dir = StringVar()
        self.check_links_dir.set(self.check_links_dirs[0])
        self.quick_links_file = StringVar()
        self.quick_links_file.set(self.quick_links_files[0])
        self.mainWin.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle win close event
        self.mainWin.after(100, self.check_queue_from_main)  # Periodically check GUI queue
        self.mainWin.title(self.widget_texts_list[0])
        self.mainWin.columnconfigure(0, weight=1)
        self.mainWin.rowconfigure(0, weight=1)
        # frame Main +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Main = ttk.Frame(self.mainWin, borderwidth=10, relief='ridge',
                                   padding="10 10 20 20", style = "all.TFrame")
        self.frame_Main.grid(column=0, row=0, sticky=(W, N, E, S))
        for column in range(1,3): # 2 columns
            self.frame_Main.columnconfigure(column, weight=1)
        for row in range(1,5):    # 4 rows
            self.frame_Main.rowconfigure(row, weight=1)

        # frame Header: Image with time and fontsize spinbox +++++++++++++++++++
        self.frame_Header = ttk.Frame(self.frame_Main, borderwidth=3, relief='groove',
                                      padding="10 10 20 20", style="all.TFrame")
        self.frame_Header.grid(column=1, row=1, columnspan=2, sticky=(N,W,E))
        for column in range(1,4): # 3 columns
            self.frame_Header.columnconfigure(column, weight=1)
        for row in range(1,4):    # 3 rows
            self.frame_Header.rowconfigure(row, weight=1)
        self.imageL1 = PhotoImage(file='pyshpcreator.png')
        self.label_png = ttk.Label(self.frame_Header, text="",
                                   image=self.imageL1,
                                   style="default.TLabel")
        self.label_png.grid(column=1, row=2, columnspan=3, sticky=N)
        self.label_time = ttk.Label(self.frame_Header, text="",
                                    justify='right',
                                    style="time.TLabel")
        self.label_time.grid(ipady=self.ipady, column=3, row=1, sticky=(N,E))
        self.frame_Fontsize = ttk.Frame(self.frame_Header, style="all.TFrame")
        self.frame_Fontsize.grid(column=3, row=3, sticky=(E,N))
        self.label_fontsize = ttk.Label(self.frame_Fontsize,
                                        text="Fontsize: ",
                                        style="default.TLabel")
        self.label_fontsize.grid(column=1, row=1,sticky=(E))
        self.spinb_fontsize = ttk.Spinbox(self.frame_Fontsize,from_=6, to=24,
                                          textvariable=self.FSize,
                                          command=self.FontSizeUpdate, width=4,
                                          justify='center',
                                          font=self.standard_font,
                                          style="default.TSpinbox")
        self.spinb_fontsize.grid(column=2, row=1, sticky=(E))

        # frame Create, Links, Upload) +++++++++++++++++++++++++++++++++++++++
        self.frame_Create = ttk.Frame(self.frame_Main,borderwidth=3, relief='groove',
                                      padding="10 10 20 20", style = "all.TFrame")
        self.frame_Create.grid(column=1, row=2, columnspan=2, sticky=(W,E))
        for column in range(1,3):
            self.frame_Create.columnconfigure(column, weight=1)
        for row in range(1,3):
            self.frame_Create.rowconfigure(row, weight=1)
        # 1 Button
        self.butt_create = ttk.Button(self.frame_Create,
                                      text=self.widget_texts_list[1],
                                      command=self.on_butt_create_pressed,
                                      width=self.button_width_normal,
                                      style="important.TButton")
        self.butt_create.grid(ipady=self.ipady, column=1, row=1, sticky=(W))
        # 1 Frame with Combobox and Label
        self.frame_Hpdir = ttk.Frame(self.frame_Create, style="all.TFrame")
        self.frame_Hpdir.grid(column=1, row=2, sticky=(W))
        self.label_hpdir = ttk.Label(self.frame_Hpdir,
                                     text=self.widget_texts_list[2],
                                     style="default.TLabel")
        self.label_hpdir.grid(column=1, row=1, sticky=(N,W,E))
        self.combobox_hpdir = ttk.Combobox(self.frame_Hpdir,
                                           width=self.button_width_normal,
                                           textvariable=self.hp_dir_name,
                                           font=self.standard_font,
                                           style="default.TCombobox")
        self.combobox_hpdir.grid(ipady=self.ipady, column=1, row=2, sticky=(S,W))
        self.combobox_hpdir['values'] = self.hp_dir_names
        self.combobox_hpdir.current()
        # 2 Button
        self.butt_quick_links = ttk.Button(self.frame_Create,
                                           text=self.widget_texts_list[3],
                                           command=self.on_butt_quick_links_pressed,
                                           width=self.button_width_normal,
                                           style="default.TButton")
        self.butt_quick_links.grid(ipady=self.ipady, column=2, row=1, sticky=(S,W))
        # 2 Frame with Combobox and Label
        self.frame_Quick = ttk.Frame(self.frame_Create, style="all.TFrame")
        self.frame_Quick.grid(column=2, row=2, sticky=(W))
        self.label_quick_links = ttk.Label(self.frame_Quick,
                                           text=self.widget_texts_list[4],
                                           style="default.TLabel")
        self.label_quick_links.grid(column=1, row=1, sticky=(N,W,E))
        self.combobox_quick_links = ttk.Combobox(self.frame_Quick,
                                                 width=self.button_width_normal,
                                                 textvariable=self.quick_links_file,
                                                 font=self.standard_font,
                                                 style="default.TCombobox")
        self.combobox_quick_links.grid(ipady=self.ipady, column=1, row=2, sticky=(S,W))
        self.combobox_quick_links['values'] = self.hp_dir_names
        self.combobox_quick_links.current()
        # 3 Button
        self.butt_check_links = ttk.Button(self.frame_Create,
                                           text=self.widget_texts_list[5],
                                           command=self.on_butt_check_links_pressed,
                                           width=self.button_width_normal,
                                           style="default.TButton")
        self.butt_check_links.grid(ipady=self.ipady, column=3, row=1, sticky=(S,W))
        # 3 Frame with Combobox and Label
        self.frame_Check = ttk.Frame(self.frame_Create, style="all.TFrame")
        self.frame_Check.grid(column=3, row=2, sticky=(W,E))
        self.label_check_links = ttk.Label(self.frame_Check,
                                           text=self.widget_texts_list[6],
                                           style="default.TLabel")
        self.label_check_links.grid(column=1, row=1, sticky=(N,W,E))
        self.combobox_check_links = ttk.Combobox(self.frame_Check,
                                                 width=self.button_width_normal,
                                                 textvariable=self.check_links_dir,
                                                 font=self.standard_font,
                                                 style="default.TCombobox")
        self.combobox_check_links.grid(ipady=self.ipady, column=1, row=2, sticky=(S,W))
        self.combobox_check_links['values'] = self.hp_dir_names
        self.combobox_check_links.current()
        # 4 Button
        self.butt_upload = ttk.Button(self.frame_Create,
                                      text=self.widget_texts_list[7],
                                      command=lambda: self.set_flag(self.flags_2_main[3],
                                      self.widget_texts_dict[self.widget_texts_list[7]]),
                                      width=self.button_width_normal,
                                      style="important.TButton")
        self.butt_upload.grid(ipady=self.ipady, column=4, row=1, sticky=(W,E))

        # frame Textbox +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Textbox = ttk.Frame(self.frame_Main,  style="all.TFrame")
        self.frame_Textbox.grid(column=1, row=3, columnspan=2,  sticky=(W,E))
        for column in range(1,3): # 2 columns
            self.frame_Textbox.columnconfigure(column, weight=10)
        for row in range(1,3):    # 2 rows
            self.frame_Textbox.rowconfigure(row, weight=10)
        self.txt_win = Text(self.frame_Textbox,
                            font=self.textbox_font,
                            state='normal',
                            width = self.text_win_width,
                            height = self.text_win_height)
        self.txt_win.grid(column=1, row=1, sticky=(N,S,E))
        self.txt_win.insert(END, self.welcome_txt + "\n\n")
        self.scrollbar = ttk.Scrollbar(self.frame_Textbox, orient=VERTICAL,
                                       command=self.txt_win.yview)
        self.scrollbar.grid(column=2, row=1, sticky=(N,S,W))
        self.txt_win.configure(yscrollcommand=self.scrollbar.set)
        self.butt_clear_win = ttk.Button(self.frame_Textbox,
                                         text=self.widget_texts_list[8],
                                         command=self.clear_textwindow,
                                         width=self.button_width_wide,
                                         style="default.TButton")
        self.butt_clear_win.grid(ipady=self.ipady, column=1, row=2, columnspan=2, sticky=(S))

        # frame Footer: Quit ++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Footer = ttk.Frame(self.frame_Main,  borderwidth=3,
                                      padding="10 10 10 10", relief='groove',
                                      style="all.TFrame")
        self.frame_Footer.grid(column=1, row=4, columnspan=2,  sticky=(S,W,E))
        for column in range(1,3): # 2 columns
            self.frame_Footer.columnconfigure(column, weight=1)
        for row in range(1,2):    # 1 rows
            self.frame_Footer.rowconfigure(row, weight=1)
        self.butt_quit = ttk.Button(self.frame_Footer,
                                    text=self.widget_texts_list[9],
                                    command=self.on_closing,
                                    width=self.button_width_normal,
                                    style="default.TButton")
        self.butt_quit.grid(ipady=self.ipady, column=2, row=1,sticky=(S,E))

        self.UpdateTime()
        self.combobox_hpdir.configure(font=self.standard_font)

        # Padding
        for child in self.frame_Main.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Fontsize.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Create.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Hpdir.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Textbox.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Footer.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)



        self.mainWin.mainloop()

def start_gui(flags_2_main, queue_2_main, queue_2_gui):
    gui = GUI(flags_2_main, queue_2_main, queue_2_gui)
    gui.run()
