#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Simple html/css homepage creator using markdown """
###############################################################################
#
#  pyshpcreator.py
#
#  Version 2.0 2020-08 (checked with pylint)
#
#  Copyright 2016 weigu <weigu@weigu.lu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
###############################################################################

# We got sometimes an error from Paramiko when access times of files are corrupt
# (year > 2100). Open the file with touch to change this:
# find . -atime -0 -exec touch {} +    (ev. exchange atime with ctime or mtime)

from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from os import chdir, walk, getcwd
from glob import glob
import threading
from markdown2 import markdown
import pygments #for color highlightning; include code_highlight.css!
from configparser import ConfigParser
from sftpclone import sftpclone
from time import gmtime, strftime, localtime, sleep

#---- class GUI ----------------------------------------------------------------

class GUI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self) # Tkinter canvas
        self.daemon = True # so it will be killed with the main thread!
        self.start()
        self.standard_font = ["Helvetica", 12, "bold"]
        self.textbox_font = ["Courier", 12, "bold"]
        self.hp_dir_names = []
        self.flag_exit = False
        self.flag_create = False
        self.flag_upload = False
        self.padx = 5
        self.pady = 5
        self.ipady = 7
        self.button_width = 40 # width of 4 buttons (Asyn, Get, Set, Function)
        self.button_width_small = 25
    def callback(self):        
        self.flag_exit = True
        print("callback")
    
    def create(self):
        self.flag_create = True
        
    def upload(self):
        self.flag_upload = True
        
    def clear_textwindow(self):
        self.txt_win.delete(1.0, END) 

    def init_ttk_styles(self):
        self.s = ttk.Style()
        #frames
        self.s.configure("all.TFrame", background="lightgrey")
        self.s.configure("test.TFrame", background="grey")
        #widgets
        self.s.configure("default.TLabel", background="lightgrey",
                         font=self.standard_font)
        self.s.configure("time.TLabel", background="lightgrey",
                         font=self.standard_font)

        self.s.configure("default.TEntry", background="lightgray",
                         font=self.standard_font)        
        self.s.configure("default.TCombobox", font=self.standard_font,
                         background="lightgrey", fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("default.TSpinbox", font=self.standard_font,
                         background="lightgrey", fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("important.TButton", background="lightgreen",
                         font=self.standard_font, borderwidth=5)
        self.s.configure("default.TButton", background="lightgrey",
                         font=self.standard_font, borderwidth=5)
        self.s.map("important.TButton",background = [("active", 'lawngreen')])

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
        self.s.configure("default.TSpinbox", font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=int(FSize)*1.5)
        self.txt_win.config(font=self.textbox_font)
        self.combobox_hpdir.config(font=self.standard_font)
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
        self.mainWin.protocol("WM_DELETE_WINDOW", self.callback)
        self.mainWin.title('PYthon Simple HomePage CREATOR')
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
        
        # frame Create (and Upload) ++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Create = ttk.Frame(self.frame_Main, style = "all.TFrame")
        self.frame_Create.grid(column=1, row=2, columnspan=2, sticky=(W,E))
        for column in range(1,3):
            self.frame_Create.columnconfigure(column, weight=1)        
        for row in range(1,3):
            self.frame_Create.rowconfigure(row, weight=1)
        self.frame_Hpdir = ttk.Frame(self.frame_Create, style="all.TFrame")
        self.frame_Hpdir.grid(column=1, row=1, sticky=(W))            
        self.label_hpdir = ttk.Label(self.frame_Hpdir,
                                     text="Choose homepage directory",
                                     style="default.TLabel")
        self.label_hpdir.grid(column=2, row=1, sticky=(E))        
        self.combobox_hpdir = ttk.Combobox(self.frame_Hpdir,
                                           width=self.button_width,                                           
                                           textvariable=self.hp_dir_name,
                                           font=self.standard_font,
                                           style="default.TCombobox") 
        self.combobox_hpdir.grid(ipady=self.ipady, column=1, row=1, sticky=(W))
        self.combobox_hpdir['values'] = self.hp_dir_names
        self.combobox_hpdir.current()
        self.butt_create = ttk.Button(self.frame_Create,
                                      text='Create homepage!',
                                      command=self.create,
                                      width=self.button_width,
                                      style="important.TButton")
        self.butt_create.grid(ipady=self.ipady, column=1, row=2, sticky=(W))        
        self.butt_upload = ttk.Button(self.frame_Create,
                                      text='Upload homepage!',
                                      command=self.upload,
                                      width=self.button_width,
                                      style="important.TButton")
        self.butt_upload.grid(ipady=self.ipady, column=2, row=2, sticky=(E))  

        # frame Textbox +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Textbox = ttk.Frame(self.frame_Main,  style="all.TFrame")
        self.frame_Textbox.grid(column=1, row=3, columnspan=2,  sticky=(W,E))
        for column in range(1,3): # 2 columns
            self.frame_Textbox.columnconfigure(column, weight=10)
        for row in range(1,3):    # 2 rows
            self.frame_Textbox.rowconfigure(row, weight=10)
        self.txt_win = Text(self.frame_Textbox,  font=self.textbox_font,
                            state='normal')        
        self.txt_win.grid(column=1, row=1, sticky=(N,S,E))
        self.txt_win.insert(END, "Hello to PYSHPCREATOR\n\n")
        self.scrollbar = ttk.Scrollbar(self.frame_Textbox, orient=VERTICAL,
                                       command=self.txt_win.yview)
        self.scrollbar.grid(column=2, row=1, sticky=(N,S,W))
        self.txt_win.configure(yscrollcommand=self.scrollbar.set)
        self.butt_clear_win = ttk.Button(self.frame_Textbox,
                                         text='Clear Textwindow',
                                         command=self.clear_textwindow,
                                         width=self.button_width,
                                         style="default.TButton")
        self.butt_clear_win.grid(ipady=self.ipady, column=1, row=2, columnspan=2, sticky=(S))        

        # frame Footer: Quit ++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Footer = ttk.Frame(self.frame_Main,  borderwidth=3,
                                      padding="10 10 20 20", relief='groove',
                                      style="all.TFrame")
        self.frame_Footer.grid(column=1, row=4, columnspan=2,  sticky=(S,W,E))
        for column in range(1,3): # 2 columns
            self.frame_Footer.columnconfigure(column, weight=1)
        for row in range(1,2):    # 1 rows
            self.frame_Footer.rowconfigure(row, weight=1)
        self.butt_quit = ttk.Button(self.frame_Footer, text='Quit',
                                    command=self.callback,                                    
                                    width=self.button_width_small,
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
        
        #self.mainWin.update_idletasks()
        self.mainWin.mainloop()

#--- functions -----------------------------------------------------------------

def walk_directories(hp_dir_name, blacklist):
    """ walk thru directories and create directory list """
    # parse hp root directory (level 1)
    chdir(hp_dir_name)    
    dir_list_1 = next(walk(hp_dir_name))[1]
    for item in blacklist:
        try:
            dir_list_1.remove(item)
        except:
            continue
    dir_list_1.sort()                   # alphabetical sort
    # parse second level
    dir_list_2 = []
    nr_dirs_l1 = len(dir_list_1)
    for i in range(nr_dirs_l1):
        dir_name = hp_dir_name + '/' + dir_list_1[i]
        chdir(dir_name)
        dir_list_2.append(next(walk(dir_name))[1])
        for item in blacklist:
            try:
                dir_list_2[i].remove(item)
            except:
                continue
    for i in range(nr_dirs_l1):         # alphabetical sort
        for j in range(len(dir_list_2[i])):
            dir_list_2[i].sort()
    # parse third level
    dir_list_3 = p = [[] for x in range(nr_dirs_l1)]   
    for i in range(nr_dirs_l1):
        nr_dirs_l2_i = len(dir_list_2[i])
        for j in range (nr_dirs_l2_i):
            dir_name = hp_dir_name + '/' + dir_list_1[i] + '/' + dir_list_2[i][j]
            chdir(dir_name)        
            dir_list_3[i].append(next(walk(dir_name))[1])
            for item in blacklist:                
                try:
                    dir_list_3[i][j].remove(item)
                except:
                    continue
    for i in range(nr_dirs_l1):   # alphabetical sort
        for j in range(len(dir_list_2[i])):
            dir_list_3[i][j].sort()
    chdir(hp_dir_name)    
    return (dir_list_1, dir_list_2, dir_list_3)

def print_dir_list(window, dir_list):
    """ print directory list """
    text1 = '---------------------------------------------------------------\n'
    print(text1)
    text = text1
    for i in range(len(dir_list[0])):        
        print (dir_list[0][i])
        text = text + (dir_list[0][i]) + '\n'
        for j in range(len(dir_list[1][i])):
            print ('    {0}'.format(dir_list[1][i][j]))
            text = text + '    {0}'.format(dir_list[1][i][j]) + '\n'
            for k in range(len(dir_list[2][i][j])):
                print ('        {0}'.format(dir_list[2][i][j][k]))
                text = text + '        {0}'.format(dir_list[2][i][j][k]) + '\n'
    text = text + text1
    print(text1)
    window.txt_win.insert(END, text)
    window.txt_win.see("end")
    window.mainWin.update_idletasks()

def create_index_file(md_file, level, dir_nr_l0, dir_nr_l1, dir_nr_l2, dir_list):
    """ create the file "index.html" from md-file and data from dir_list """    
    html = []
    hp_title = 'default'
    hp_keywords = ''
    hp_sidebar = []
    hp_content = ''
    hp_lup = ''
    nr_dirs_l1 = len(dir_list[0])
    for i in range(level):
        hp_lup = hp_lup + '../'
    # open md and html file
    try:
        f_md = open(md_file, 'r')
    except IOError:
        print('Cannot find ', md_file)
        exit()
    if md_file == 'news.md':
        fname = 'news.html'
        content_id = 'news'
    elif md_file == 'sitemap.md':
        fname = 'sitemap.html'
        content_id = 'sitemap'
    elif md_file == 'disclaimer.md':
        fname = 'disclaimer.html'
        content_id = 'disclaimer'
    else:
        fname = 'index.html'
        content_id = 'home'
    try:
        f_html = open(fname, 'w')
    except IOError:
        print('Cannot create index.html')
        exit()
    # test if one md file present
    file_list = glob('*.md')
    if len(file_list) != 1 and level != 0:
        print("Error: no md file or more than one md file in ", getcwd())
    # parse md file
    line = f_md.readline()
    while line != '':
        if line.find('[TITLE]') != -1:
            line = f_md.readline()
            hp_title = line.strip('\n')
        if line.find('[KEYWORDS]') != -1:
            line = f_md.readline()
            stop = 0
            while (line.find('[KEYWORDS_END]') == -1):
                stop += 1
                hp_keywords = hp_keywords+line.strip('\n')
                line = f_md.readline()
                if stop > 20:
                    print (' error in md file', md_file)
                    exit()
        if line.find('[SIDEBAR]') != -1:
            line = f_md.readline()
            stop = 0
            while line.find('[SIDEBAR_END]') == -1:
                hp_sidebar.append(line.strip('\n'))
                line = f_md.readline()
                if stop > 20:
                    print (' error in md file', md_file)
                    exit()
        if line.find('[CONTENT]') != -1:
            line = f_md.readline()
            stop = 0
            while line.find('[CONTENT_END]') == -1:
                hp_content = hp_content+line
                line = f_md.readline()
                if stop > 10000:
                    print (' error in md file', md_file)
                    exit()
        line = f_md.readline()
    # create head
    html.append('<!DOCTYPE html>\n\n'
                '<head>\n'
                '<title>{0}</title>\n'
                '  <meta http-equiv="Content-Type" content="text/html; charset'
                '=utf-8" />\n'
                '  <meta name="KEYWORDS" content="{2}" />\n'
                '  <meta name="viewport" content="height=device-height,' 
                'width=device-width, initial-scale=0.5, '
                'minimum-scale=0.2, maximum-scale=1.0, '
                'user-scalable=yes, target-densitydpi=device-dpi">\n'
                '  <link rel="icon" type="image/x-icon" href="{1}png/favicon.ico"'
                ' />\n'                
                '  <link rel="stylesheet" type="text/css" href="{1}index.css"'
                ' />\n'
                '</head>\n\n'.format(hp_title, hp_lup, hp_keywords))
    # create body id
    if level == 0:
        html.append('<body id="pyshp">\n\n')
    else:
        html.append('<body id="pyshp_{0}">\n\n'.format(str(dir_nr_l0 + 1)))
    # create header: picture or logo with menu bar
    html.append('<!-- Header -->\n<div id="header">\n'
                '<p id="menu0"></p>  <!-- fuer das Logo -->\n\n'
                '<ul id="menu1">\n')
    mact = ''
    if level == 0:
        mact = 'class = "mact" '
    html.append('  <li {0}id="m1home"><a href="{1}index.html" title="home"'
                '>home</a></li>\n'.format(mact, hp_lup))
    for i in range(nr_dirs_l1):
        mact = ''
        if i == dir_nr_l0 and level != 0 :  # mark act. menu (numbered 1 to x)
            mact = 'class = "mact" '
        html.append('  <li {0}id="m1{1}"><a href="{2}{3}/index.html" title='
                    '"{3}">{3}</a></li>\n'.format(mact, str(i + 1), hp_lup,
                    str(dir_list[0][i])))
    html.append('</ul><!-- menu1 -->\n</div><!-- Header -->\n')
    # create sidebar (not for main page (home))
    if level > 0:
        html.append('<!-- Sidebar -->\n<div id="csidebar_{0}">\n<br />\n<ul id'
                    '="sidebar_{0}">\n'.format(str(dir_nr_l0 + 1)))        
        if level == 1:
            html.append('  <li class = "sbact"><a href="index.html" title='
                        '"{0}">{0}</a></li>'
                        '\n'.format(str(dir_list[0][dir_nr_l0])))
            for i in range(len(dir_list[1][dir_nr_l1])):
                html.append('  <li ><a href="{0}/index.html" title="{0}">{0}</'
                            'a></li>\n'.format(str(dir_list[1][dir_nr_l1][i])))
        if (level == 2) or (level == 3):
            html.append('  <li><a href="../index.html" title="{0}">{0}</a>'
                        '</li>\n'.format(str(dir_list[0][dir_nr_l0])))
            for i in range(len(dir_list[1][dir_nr_l0])):
                if i == dir_nr_l1:  # mark active sidebar item
                    html.append('  <li class = "sbact" ')
                else:
                    html.append('  <li ')
                if level == 2:
                    html.append('><a href="../{0}/index.html" title="{0}">{0}</a>'
                            '</li>\n'.format(str(dir_list[1][dir_nr_l0][i])))
                else:
                    html.append('><a href="../../{0}/index.html" title="{0}">{0}</a>'
                            '</li>\n'.format(str(dir_list[1][dir_nr_l0][i])))
        if level == 3:
            for i in range(len(dir_list[2][dir_nr_l0][dir_nr_l1])):
                if i == dir_nr_l2:  # mark active sidebar item
                    html.append('  <li class = "sbact" ')
                else:
                    html.append('  <li ')
                html.append('><a href="../{0}/index.html" title="{0}">{0}</a>'
                            '</li>\n'.format(str(dir_list[2][dir_nr_l0][dir_nr_l1][i])))
        # add sidebar items from md file
        for i in range(len(hp_sidebar)):
            hp_sidebar[i] = hp_sidebar[i].split('  ')
            if hp_sidebar[i][0] == 1:  # mark active sidebar item
                html.append('  <li class = "sbact" ')
            else:
                html.append('  <li ')
            html.append('><a href="{0}/index.html" title="{1}">{2}</a></li>\n'.
                        format(str(hp_sidebar[i][1]), str(hp_sidebar[i][2]),
                        str(hp_sidebar[i][3])))
        # add news and sitemap and up
        html.append('  <li><a href="{0}/news.html" title="news">news</a></li>'
                    '\n'.format(hp_lup))
        html.append('  <li><a href="{0}/sitemap.html" title="sitemap">sitemap'
                    '</a></li>\n'.format(hp_lup))
        html.append('  <li class ="up"><a href="index.html" title="up">UP (if down :))         '
                    '</a></li>\n'.format(hp_lup))
        html.append('</ul>\n</div><!-- Sidebar -->\n\n')
        # content: convert md to html
        html.append('<!-- Content -->\n<div id="content_{0}">\n{1}\n</div> <!'
                    '-- Content -->\n\n'.format(str(dir_nr_l0 + 1),
                    markdown(hp_content, extras=["tables","fenced-code-blocks","markdown-in-html"])))
    else:
        html.append('<!-- Content -->\n<div id="content_{0}">\n{1}\n</div> <'
                    '!-- Content -->\n\n'.format(content_id,
                    markdown(hp_content, extras=["tables","fenced-code-blocks","markdown-in-html"])))
    # create footer (same for all pages)
    html.append('<!-- Footer -->\n'
                '<div id="footer">\n'
                '  <ul id="footerl2">\n'

                '  </ul>\n'
                '  <ul id="footerl2">\n'
#                '    <li><a href="index.html" title="UP">UP</a>(if you are'
#                ' down)</li>\n'
                '    <li><a href="{0}news.html" title="NEWS">NEWS</a></li>\n'
                '    <li><a href="{0}disclaimer.html" title="DISCLAIMER &amp;'
                ' COPYRIGHT">DISCLAIMER &amp; COPYRIGHT</a></li>\n'
                '    <li><a href="{0}sitemap.html" title="SITEMAP">SITEMAP</a'
                '></li>\n  </ul>\n'
                '  <ul id="footerl3">\n'
                '    <li>contact:</li>\n'
                '    <li><img src="{0}png/email.png" alt="Kontakt-Adresse'
                '"/></li>\n'
                '  </ul>\n'
                '</div> <!-- Footer -->\n\n'
                '</body>\n'
                '</html>'.format(hp_lup))

    f_html.write("".join(html))
    f_md.close()
    f_html.close()

def generate_sitemap(hp_dir_name, dir_list):
    chdir(hp_dir_name)
    try:
        f_sm = open('sitemap.md', 'w')
    except IOError:
        print('Cannot create sitemap.md')
        exit()
    f_sm.write('[TITLE]\n'
               'SITEMAP\n'
               '[CONTENT]\n'
               '# Sitemap\n\n'
               '|   | <pre>        </pre> |   |\n'
               '| - | - | - |\n'
               '| [/](index.html "starting page") | <pre>        </pre> | '
               'starting page |\n'
               '| [/disclaimer.html](disclaimer.html "disclaimer") | <pre>'
               '        </pre> | disclaimer and copyright |\n'
               '| [/news.html](news.html "News") | <pre>        </pre> | '
               'news |\n'
               '| [/sitemap.html](sitemap.html "this page") | <pre>'
               '        </pre> | this page |\n')
    for i in range(len(dir_list[0])):
        f_sm.write('| <hr /> | <pre>        </pre> | <hr /> |\n'
                   '| [/{0}]({0}/index.html "{0}") | <pre>        </pre> | {0}'
                   ' |\n'.format(dir_list[0][i].replace('_', '\_')))
        for j in range(len(dir_list[1][i])):
            f_sm.write('| [/{1}/{0}]({1}/{0}/index.html "{0}") | <pre>'
                       '        </pre> | {0} |\n'
                       .format(dir_list[1][i][j].replace('_', '\_'),
                       dir_list[0][i].replace('_', '\_')))
    f_sm.write('<br />\n[CONTENT_END]')
    f_sm.close()

def generate_hp(window, hp_dir_name, dir_list):
    """ homepage generator: walk thru all dirs and create all index_files """
    # first root dir
    chdir(hp_dir_name)
    print(hp_dir_name)
    md_file_list = glob('*.md')    
    if 'news.md' in md_file_list:
        create_index_file('news.md', 0, 0, 0, 0, dir_list)
        md_file_list.remove('news.md')
    if 'sitemap.md' in md_file_list:
        create_index_file('sitemap.md', 0, 0, 0, 0, dir_list)
        md_file_list.remove('sitemap.md')
    if 'disclaimer.md' in md_file_list:
        create_index_file('disclaimer.md', 0, 0, 0, 0, dir_list)
        md_file_list.remove('disclaimer.md')
    if len(md_file_list) != 1:
        print("Error: no md file or more than one md file (except news.md,"
              "sitemap.md, disclaimer.md and css.md) in ", hp_dir_name)
    try:
        md_file = md_file_list[0]
    except IndexError:
        error_text = "IndexError in generate(hp)\n"
        print(error_text, end='')
        window.txt_win.insert(END, error_text)
        window.txt_win.see("end")
        window.mainWin.update_idletasks()
        return -1
    create_index_file(md_file, 0, 0, 0, 0, dir_list)
    nr_dirs_l1 = len(dir_list[0])
    # create index files in level 1 (nr_dirs_l1)
    for i in range(nr_dirs_l1):
        chdir(hp_dir_name + '/' + dir_list[0][i])
        md_file_list = glob('*.md')
        if len(md_file_list) != 1:
            print("Error: no or more than one md file in ", getcwd())
        md_file = md_file_list[0]
        create_index_file(md_file, 1, i, i, 0, dir_list)
    # create index files in level 2 (nr_dirs_l1)
    for i in range(nr_dirs_l1):        
        for j in range(len(dir_list[1][i])):
            chdir(hp_dir_name + '/' + dir_list[0][i] + '/'
                     + dir_list[1][i][j])
            file_list = glob('*.md')
            if len(file_list) != 1:
                print("Error: no or more than one md file in ", getcwd())
            md_file = file_list[0]
            create_index_file(md_file, 2, i, j, 0, dir_list)
    # create index files in level 3
    for i in range(nr_dirs_l1):
        for j in range(len(dir_list[1][i])):
            for k in range(len(dir_list[2][i][j])):
                chdir(hp_dir_name + '/' + dir_list[0][i] + '/'
                     + dir_list[1][i][j] + '/' + dir_list[2][i][j][k])
                file_list = glob('*.md')
                if len(file_list) != 1:
                     print("Error: no or more than one md file in ", getcwd())
                md_file = file_list[0]
                create_index_file(md_file, 3, i, j, k, dir_list)
                

def generate_css(parsed_data_css, hp_dir_name):
    """ css generator using pyshpcreator.conf and css_template.css. """
    chdir(hp_dir_name)
    # open template file
    try:
        css_template = open('css_template.css', 'r')
    except IOError:
        error_text = "Cannot open css.template.css\n"
        print(error_text, end='')
        window.txt_win.insert(END, error_text)
        window.txt_win.see("end")
        window.mainWin.update_idletasks()
        return -1
    try:
        css = open('index.css', 'w')
    except IOError:
        error_text = "Cannot write to index.css\n"
        print(error_text, end='')
        window.txt_win.insert(END, error_text)
        window.txt_win.see("end")
        window.mainWin.update_idletasks()
        return -1
    page_colors = []
    page_colors.append(parsed_data_css['pagecolor0'].split(','))
    page_colors.append(parsed_data_css['pagecolor1'].split(','))
    page_colors.append(parsed_data_css['pagecolor2'].split(','))
    page_colors.append(parsed_data_css['pagecolor3'].split(','))
    page_colors.append(parsed_data_css['pagecolor4'].split(','))
    page_colors.append(parsed_data_css['pagecolor5'].split(','))
    page_colors.append(parsed_data_css['pagecolor6'].split(','))
    print(page_colors)
    menue_width = str(100-int(parsed_data_css['menue_padding_left']))
    # parse template file and create index.css
    line = css_template.readline()
    while line != '':
        line = line.replace('[HP_FONT_SIZE]', parsed_data_css['hp_font_size'])
        line = line.replace('[HP_FONT_FAMILY]', parsed_data_css['hp_font_family'])
        line = line.replace('[HP_FONT_COLOR]', parsed_data_css['hp_font_color'])
        line = line.replace('[HEADING_FONT_FAMILY]', parsed_data_css['heading_font_family'])
        line = line.replace('[HEADING_1_COLOR]', parsed_data_css['heading_1_color'])
        line = line.replace('[HEADING_2_4_COLOR]', parsed_data_css['heading_2_4_color'])
        line = line.replace('[MENUE_PADDING_LEFT]', parsed_data_css['menue_padding_left'])
        line = line.replace('[MENUE_WIDTH]', menue_width)
        line = line.replace('[MENUE_COLOR1]', parsed_data_css['menue_color1'])
        line = line.replace('[MENUE_COLOR2]', parsed_data_css['menue_color2'])
        line = line.replace('[MENUE_COLOR3]', parsed_data_css['menue_color3'])
        line = line.replace('[HP_LOGO]', parsed_data_css['hp_logo'])
        line = line.replace('[PCOLOR_DISCLAIMER]', parsed_data_css['pcolor_disclaimer'])
        line = line.replace('[PCOLOR_NEWS]', parsed_data_css['pcolor_news'])
        line = line.replace('[PCOLOR_SITEMAP]', parsed_data_css['pcolor_sitemap'])
        for i in range(7):
            line = line.replace('[PCOLOR{0}]'.format(i), page_colors[i][0])
            line = line.replace('[PCOLOR{0}_PNG1]'.format(i),
                                page_colors[i][1])
            line = line.replace('[PCOLOR{0}_PNG2]'.format(i),
                                page_colors[i][2])
            line = line.replace('[PCOLOR{0}_PNG3]'.format(i),
                                page_colors[i][3])

        css.write(line)
        line = css_template.readline()
    css.close()
    css_template.close()
    

def create(window, parser_local, parsed_data_local):
    css_data = {}
    try:
        hp_dir_name = window.hp_dir_name.get()
        chdir(hp_dir_name)
        #print(hp_dir_name)
        if not parser_local.read('pyshpcreator.conf'):
            text = "pyshpcreator.conf is missing in " + getcwd() + \
                   "\ndefault data from PYSHPCREATOR directory is used\n"
            print(text)
            window.txt_win.insert(END, text)
            window.txt_win.see("end")
            window.mainWin.update_idletasks()
            blacklist = parsed_data_local[2]
            generate_css(parsed_data_local[3], hp_dir_name)
        else:            
            blacklist = parser_local.get('GLOBAL','blacklist').split(',')
            for key in parser_local['CSS']:
                css_data.update( {key : parser_local.get('CSS',key)} )
            generate_css(css_data, hp_dir_name)
        dir_list = walk_directories(hp_dir_name, blacklist)
        print_dir_list(window, dir_list)
        generate_sitemap(hp_dir_name, dir_list)
        generate_hp(window, hp_dir_name, dir_list)    
        text = "Homepage created!\n"        
        print (text)
        window.txt_win.insert(END, text)
        window.txt_win.see("end")        
    except (ValueError,IndexError):
        text = "Homepage not created!\nWe got a value or index error"
        window.txt_win.insert(END, text)
        window.txt_win.see("end")
    window.mainWin.update_idletasks()    

def upload(window, parser_local, parsed_data_local):
    print(parsed_data_local[0])
    hp_dir_name = window.hp_dir_name.get()
    chdir(hp_dir_name)
    #print(hp_dir_name)
    index = parsed_data_local[1].index(hp_dir_name) + 1
    #print(index)
    url = parsed_data_local[0]['url_'+str(index)]    
    login = parsed_data_local[0]['login_'+str(index)]
    password = parsed_data_local[0]['pass_'+str(index)]
    sport = int(parsed_data_local[0]['port_'+str(index)])
    destination = parsed_data_local[0]['dest_'+str(index)]
    print(url)    
    print(login)
    print(password)
    print(sport)
    print(destination)
    src = hp_dir_name
    dst = destination
    Text = "Please wait while uploading\n"
    print (url,login,password,sport,destination,src)
    print(Text)
    window.txt_win.insert(END, Text)
    window.txt_win.see("end")
    window.mainWin.update_idletasks()
    print(src)    
    remote = login + ":" + password + "@" +  url + ":" + dst
    print (remote)
    sftpclone.SFTPClone(
        src,
        remote,
        #"{}:{}@mysite.example.com:./mysite".format(login, password),
        port=sport
    ).run()
    Text = "Upload done!\n"
    print (Text)
    window.txt_win.insert(END, Text)
    window.txt_win.see("end")

def parse_main_config_file(parser_local):
    """ parse the config file in the PYSHPCREATOR directory (max 9 entries)"""    
    hp_data = {}
    hp_names = []
    css_data = {}
    if not parser_local.read('pyshpcreator.conf'):
            return -1
    section_list = parser_local.sections()
    #print(section_list)
    i=1
    for item in section_list:        
        if item[0:9]=='HOMEPAGE_':
            hp_bloc_name = 'HOMEPAGE_' + str(i)
            try:
                hp_data['dir_name_'+str(i)] = parser_local.get(hp_bloc_name,'hp_dir_name')
                hp_names.append(parser_local.get(hp_bloc_name,'hp_dir_name'))
                hp_data['url_'+str(i)] = parser_local.get(hp_bloc_name,'url')
                hp_data['login_'+str(i)] = parser_local.get(hp_bloc_name,'login')
                hp_data['pass_'+str(i)] = parser_local.get(hp_bloc_name,'password')
                hp_data['port_'+str(i)] = parser_local.get(hp_bloc_name,'port')
                hp_data['dest_'+str(i)] = parser_local.get(hp_bloc_name,'destination')                
                i += 1
            except KeyError:
                print("error")
                return -1
    blacklist = parser_local.get('GLOBAL','blacklist').split(',')
    # create CSS dictionary ang get data
    for key in parser_local['CSS']:
        css_data.update( {key : parser_local.get('CSS',key)} )

    #menue_width = str(100-int(menue_padding_left))

    return(hp_data,hp_names,blacklist,css_data)

#---- MAIN --------------------------------------------------------------------

def main():
    """setup and mainloop"""
    print("Program started!")
    flag_no_main_config_file = False
    parser = ConfigParser()
    # get data from config file return tuple with
    # hp_data [0], hp_names [1], blacklist [2] and css_data [3]
    parsed_data = parse_main_config_file(parser)
    #pyshpcreator_dir = getcwd()
    if parse_main_config_file(parser) == -1:
        flag_no_main_config_file = True
        
    window = GUI()
    
    try:
        window.hp_dir_names = parsed_data[1] #hp_names
    except TypeError:
        window.hp_dir_names = ['www.weigu.lu']
    
        
    #-----------------------------------------------------------------------------
    # MAIN LOOP
    #-----------------------------------------------------------------------------
    try:
        while (window.flag_exit == False):
            #print("Main  ",end='')
            if flag_no_main_config_file == True:
                print("flag_no_main_config_file = True")
                text = "pyshpcreator.conf file in PYSHPCREATOR directory is " \
                       "missing!!"
                print(text)
                window.mainWin.update_idletasks()
                window.txt_win.insert(END, text)
                window.txt_win.see("end")
                flag_no_main_config_file = False
            
            if window.flag_create==True:                
                create(window, parser, parsed_data)
                window.flag_create=False
            if window.flag_upload==True:
                upload(window, parser, parsed_data)
                window.flag_upload=False

            sleep(0.1)

    except KeyboardInterrupt:
        print("Keyboard interrupt by user")        
    print("closed by window")
    
main()