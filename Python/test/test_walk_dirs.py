import os
import copy

def walk_directories(hp_dir_name, blacklist):
    """ walk thru directories and create directory list """
    # parse hp root directory (level 1)
    os.chdir(hp_dir_name)
    dir_list_1 = next(os.walk(hp_dir_name))[1]
    for item in blacklist:
        try:
            dir_list_1.remove(item)
        except:
            continue
    dir_list_1.sort()  # alphabetical sort
    # parse second level
    dir_list_2 = []
    for i in range(len(dir_list_1)):
        dir_name = os.path.join(hp_dir_name, dir_list_1[i])
        os.chdir(dir_name)
        sub_dirs = next(os.walk(dir_name))[1]
        for item in blacklist:
            try:
                sub_dirs.remove(item)
            except:
                continue
        dir_list_2.append(sub_dirs)
    for i in range(len(dir_list_1)):  # alphabetical sort
        for j in range(len(dir_list_2[i])):
            dir_list_2[i].sort()
    # parse third level
    dir_list_3 = [[] for _ in range(len(dir_list_1))]
    for i in range(len(dir_list_1)):
        nr_dirs_l2_i = len(dir_list_2[i])
        for j in range(nr_dirs_l2_i):
            dir_name = os.path.join(hp_dir_name, dir_list_1[i], dir_list_2[i][j])
            os.chdir(dir_name)
            sub_dirs = next(os.walk(dir_name))[1]
            for item in blacklist:
                try:
                    sub_dirs.remove(item)
                except:
                    continue
            dir_list_3[i].append(sub_dirs)
    for i in range(len(dir_list_1)):  # alphabetical sort
        for j in range(len(dir_list_2[i])):
            dir_list_3[i][j].sort()
    os.chdir(hp_dir_name)
    return [dir_list_1, dir_list_2, dir_list_3]  # return directory list

def print_dir_list(dir_list):
    """ print directory list """
    text = "\n--------------------------------\n"
    for i in range(len(dir_list[0])):
        text += f"{dir_list[0][i]}\n"
        for j in range(len(dir_list[1][i])):
            text += f"    {dir_list[1][i][j]}\n"
            for k in range(len(dir_list[2][i][j])):
                text += f"        {dir_list[2][i][j][k]}\n"
    text += "--------------------------------\n"
    print(text)

def move_archive_files_to_end(hp_dir_name, dir_list):
    """ A file named 'archive' in the folder marks it as old.
        Move archive folders at the end of the list. """
    to_move = []
    for i in range(len(dir_list[0])):
        for j in range(len(dir_list[1][i])):
            dir_name = os.path.join(hp_dir_name, dir_list[0][i], dir_list[1][i][j])       
            os.chdir(dir_name)
            files = next(os.walk(dir_name))[2]
            if "archive" in files:
                to_move.append((i, j, dir_list[1][i][j]))
    for item in to_move:
        index = dir_list[1][item[0]].index(item[2])
        dir_list[1][item[0]].remove(item[2])
        dir_list[1][item[0]].append(item[2])
        subdir = dir_list[2][item[0]].pop(index)
        dir_list[2][item[0]].append(subdir)
    to_move = []        
    for i in range(len(dir_list[0])):
        for j in range(len(dir_list[1][i])):
            for k in range(len(dir_list[2][i][j])):
                dir_name = os.path.join(hp_dir_name, dir_list[0][i], dir_list[1][i][j], dir_list[2][i][j][k])
                print(dir_name)
                os.chdir(dir_name)
                files = next(os.walk(dir_name))[2]
                if "archive" in files:
                    to_move.append((i, j, k, dir_list[2][i][j][k]))
    for item in to_move:    
            print(f"Item {item}")
            dir_list[2][item[0]][item[1]].remove(item[3])
            dir_list[2][item[0]][item[1]].append(item[3])

def create_archive_list(hp_dir_name, dir_list):
    """ Create a list similar to dir_list with idle items.
        Mark places with archive folders with letter 'a' """
    archive_list = copy.deepcopy(dir_list)  # create a copy of the directory list
    for i in range(len(archive_list[0])): # clear the archive list
        archive_list[0][i] = ""
        for j in range(len(archive_list[1][i])):
            archive_list[1][i][j] = ""
            for k in range(len(archive_list[2][i][j])):
                archive_list[2][i][j][k] = ""    
    for i in range(len(dir_list[0])):     # create the new archive list
        for j in range(len(dir_list[1][i])):
            dir_name = os.path.join(hp_dir_name, dir_list[0][i], dir_list[1][i][j])            
            os.chdir(dir_name)
            files = next(os.walk(dir_name))[2]
            if "archive" in files:
                archive_list[1][i][j] = "a"
            for k in range(len(dir_list[2][i][j])):
                dir_name = os.path.join(hp_dir_name, dir_list[0][i], dir_list[1][i][j], dir_list[2][i][j][k])                
                os.chdir(dir_name)
                files = next(os.walk(dir_name))[2]
                if "archive" in files:
                    archive_list[2][i][j][k] = "a"
    return archive_list

blacklist = ["svg", "draft", "blender", "png", "pdf", "stl", "ino", "asm", "gpx", "wip", "kicad", "arduino", "3d", "download", "mp4", "code", "f_asm", "pc_qt", "txt", "old", "movie", "wav", "crela", "hack", "zip", "gc", "odt", "ods", "git", ".vscode", ".git", "waste_collection", "laser_cutter", ".gitignore"]

hp_dir_name = "/savit/www.weigu"  

dir_list = walk_directories(hp_dir_name, blacklist)
move_archive_files_to_end(hp_dir_name, dir_list)
print_dir_list(dir_list)
archive_list = create_archive_list(hp_dir_name, dir_list)
print(archive_list)
