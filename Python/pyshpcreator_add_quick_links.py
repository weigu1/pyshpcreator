#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# add quick links from subcharter headings (h3 ###)

import os
import sys

class AddQuickLinks:
    """ Add quick links from subchapter headings (h3 ###) to an md file """
    def __init__(self, hp_dir_name, filename):
        self.hp_dir_name = hp_dir_name
        self.filename = filename

    def get_path(self):
        os.chdir(self.hp_dir_name)
        try:
            for dirpath, dirnames, filenames in os.walk("."):
                for filename in [f for f in filenames if f.endswith(self.filename)]:
                    filename_w_path = self.hp_dir_name + os.path.join(dirpath, filename)[2:]
                    return filename_w_path
        except:
            return -1

    def get_subchapters(self, filename_w_path):
        subchapters = []
        count = 0
        with open(filename_w_path, 'r') as fh:
            line = fh.readline()
            while line != '':
                if line.find('### ') == 0:
                    pos = line.find('<')
                    if  pos != -1:
                        line = line[0:pos-1] + '\n'
                    count += 1
                    subchapters.append(line)
                line = fh.readline()
        return count, subchapters

    def format_subchapters_2_content(self, subchapters):
        for i in range(len(subchapters)):
            subchapters[i] = subchapters[i].replace('### ','+ [')
            subchapters[i] = subchapters[i].replace('\n','](#link_' + str(i) + ')\n')

    def create_new_file_content(self,subchapters, filename_w_path):
        count = 0
        new_file_content = ''
        with open(filename_w_path, 'r') as fh:
            line = fh.readline()
            while line != '':
                if line.find('### ') == 0:
                    newline = line.replace('### ','<div id=link_' + str(count) + '></div>\n\n### ')
                    count += 1
                elif line.find('last updated') == 0:
                    newline = line.replace('\n','\n\n### Quick links\n\n')
                    for item in subchapters:
                        newline = newline + item
                else:
                    newline = line
                new_file_content += newline
                line = fh.readline()
        return new_file_content

    def clear_old_quick_links(self, filename_w_path):
        count = 0
        clear_flag = 0
        new_file_content_cleared = ''
        with open(filename_w_path, 'r') as fh:
            line = fh.readline()
            while line != '':
                if line.find('### Quick links') == 0:
                    clear_flag = 1
                    print("There are already links and they will be cleared!")
                line = fh.readline()
        if clear_flag == 1:
            with open(filename_w_path, 'r') as fh:
                line = fh.readline()
                while line != '':
                    if line.find('<div') == 0:
                        newline = line[0:0]
                        line = fh.readline()
                        newline = line[0:0]
                    elif line.find('### Quick links') == 0:
                        newline = line[0:0]
                        line = fh.readline()
                        newline = line[0:0]
                        line = fh.readline()
                        while line.find('+ ') == 0:
                            newline = line[0:0]
                            line = fh.readline()
                        newline = line[0:0]
                    else:
                        newline = line
                    new_file_content_cleared += newline
                    line = fh.readline()
            return new_file_content_cleared
        else:
            return '-1'

    def add_quick_links(self):
        if self.hp_dir_name[:-1] != '/':
                self.hp_dir_name += '/'
        self.filename = self.filename.lstrip()
        filename_w_path = self.get_path()
        print("filename_w_path: ", filename_w_path)
        if filename_w_path == -1:
            print("File not found")
            return
        else:
            print("filename: ", filename_w_path)
            #check if we have to clear file (contains already subchapters)
            new_file_content_cleared = self.clear_old_quick_links(filename_w_path)
            if new_file_content_cleared != '-1':
                with open(filename_w_path, 'w') as fh:
                    fh.write(new_file_content_cleared)
            else:
                print("Nothing to clear")
            count,subchapters = self.get_subchapters(filename_w_path)
            #print (count,'  ',subchapters)
            #print("---------------------------------------------------------------")
            self.format_subchapters_2_content(subchapters)
            #print ("subchapters\n",subchapters)
            #print("---------------------------------------------------------------")
            new_file_content = self.create_new_file_content(subchapters, filename_w_path)
            #print (new_file_content)
            with open(filename_w_path, 'w') as fh:
                fh.write(new_file_content)


### main ####
def main():
    """setup and start mainloop"""
    print ('Argument list: ', sys.argv)
    hp_dir_name = "/savit/www.weigu/"
    filename = "pico_pio.md"
    if len(sys.argv) == 3:
        hp_dir_name = sys.argv[1]
        filename = sys.argv[2]
    aql = AddQuickLinks(hp_dir_name, filename)
    aql.add_quick_links()

if __name__ == '__main__':
    main()











