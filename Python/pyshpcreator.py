#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

""" Simple html/css homepage creator using markdown """
###############################################################################
#
#  pyshpcreator.py
#
#  Version 3.0 2025-03
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

# We got sometimes an error from Paramiko when access times of files are
# corrupt (year > 2100). Open the file with touch to change this:
# find . -atime -0 -exec touch {} +    (ev. exchange atime with ctime or mtime)

import threading
import os
#from sftpclone import sftpclone
from time import gmtime, strftime, localtime, sleep
import queue
from pyshpcreator_gui import start_gui, GUI
from pyshpcreator_functions import PyshpreatorFunctions

def main_loop(pshpf, flags_2_main, queue_2_main, queue_2_gui):
    hp_dir_name = ""
    try:
        while not flags_2_main[4].is_set():  # Check the exit flag

            if flags_2_main[0].is_set():
                if chosen_hp_dir_name != "":
                    pshpf.create_hp(pshpf.parsed_data, chosen_hp_dir_name, chosen_hp_dir_index)
                    flags_2_main[0].clear()
            if flags_2_main[1].is_set():
                if chosen_quick_links_file_name != "":
                    pshpf.quick_links(hp_dir_name, chosen_quick_links_file_name)
                    flags_2_main[1].clear()
            if flags_2_main[2].is_set():
                if chosen_check_links_dir_name != "":
                    pshpf.check_links(chosen_check_links_dir_name)
                    flags_2_main[2].clear()
            if flags_2_main[3].is_set():
                pshpf.upload(pshpf.parsed_data)
                flags_2_main[3].clear()
            try:
                chosen_hp_dir_name = ""
                chosen_quick_links_file_name = ""
                chosen_check_links_dir_name = ""
                message = queue_2_main.get_nowait()
                message = message.split('\n')
                #print(f"Received text from gui: {message}")
                if message[0] == "hp_dir_name:":
                    chosen_hp_dir_name = message[1]
                    hp_dir_name = chosen_hp_dir_name
                    chosen_hp_dir_index = message[2]
                if message[0] == "quick_links_file_name:":
                    chosen_quick_links_file_name = message[1]
                    chosen_quick_links_index = message[2]
                if message[0] == "check_links_dir_name:":
                    chosen_check_links_dir_name = message[1]
                    chosen_check_links_index = message[2]
            except queue.Empty:
                pass
            sleep(0.1)
    except KeyboardInterrupt:
        print("Keyboard interrupt by user")
    print("closed by GUI")

def main():
    """setup and start mainloop"""
    print("Program started! Version 3.0 (2025)")
    flag_create = threading.Event()   # Create Event objects to signal between threads
    flag_quick_links = threading.Event()
    flag_check_links = threading.Event()
    flag_upload = threading.Event()
    flag_exit = threading.Event()     # Exit flag
    flags_2_main = [flag_create, flag_quick_links, flag_check_links, flag_upload, flag_exit]
    queue_2_main = queue.Queue()      # Create a queue for communication from GUI to main_loop
    queue_2_gui = queue.Queue()       # Create a queue for communication from main_loop to GUI
    pshpf = PyshpreatorFunctions(queue_2_main, queue_2_gui)
    gui_thread = threading.Thread(target=start_gui,     # Create GUI thread
                                  args=(flags_2_main, queue_2_main, queue_2_gui))
    main_thread = threading.Thread(target=main_loop,    # Create main_loop thread
                                   args=(pshpf, flags_2_main, queue_2_main, queue_2_gui))
    gui_thread.start()                # Start both threads
    main_thread.start()
    gui_thread.join()                 # Wait for both threads to complete
    main_thread.join()

if __name__ == '__main__':
    main()