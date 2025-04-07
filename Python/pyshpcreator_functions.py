"""  Pyshpcreator functions """

import os
import paramiko
import filecmp
import copy
from glob import glob
from configparser import ConfigParser, NoSectionError
from markdown2 import markdown
import pygments #for color highlighting; include code_highlight.css!
import requests
from bs4 import BeautifulSoup
from time import sleep
from pyshpcreator_add_quick_links import AddQuickLinks
from pyshpcreator_check_links import CheckLinks
from pyshpcreator_upload import Upload

class PyshpreatorFunctions:
    def __init__(self, queue_2_main, queue_2_gui):
        self.queue_2_main = queue_2_main
        self.queue_2_gui = queue_2_gui
        self.config_file = "pyshpcreator.conf"
        self.progress_char = '.'
        self.hp_was_created = False
        self.hp_dir_name = ''
        self.hp_dir_index = ''
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.script_dir) # Set working directory to script's directory
        self.parsed_data = self.parse_main_config_file(queue_2_gui)
        if self.parsed_data == -1:
            return None
        self.hp_names = self.get_hp_names(self.parsed_data)
        text = "Homepage names detected:\n" + '\n'.join(self.hp_names)
        self.queue_2_gui.put(text)
        self.archives_clist = []
        self.archives_flist = []

    def parse_main_config_file(self, queue_2_gui):
        """ parse the main config file in the PYSHPCREATOR directory (max 9 entries)
            return 2 dim directory with hp_data blacklist and css_data """
        parser_local = ConfigParser()
        read_files = parser_local.read(self.config_file) #return list of files
        if not parser_local.read(self.config_file):
            print("Failed to read " + self.config_file)
            text = self.config_file + " file in PYSHPCREATOR directory is missing!!"
            queue_2_gui.put(text)
            return -1
        section_list = parser_local.sections()
        parsed_data = {key: {} for key in section_list} # 2 dim dict from section list
        for key1 in parsed_data:
            for key2 in parser_local[key1]:
                parsed_data[key1].update( {key2 : parser_local.get(key1,key2)} )
        return parsed_data

    def get_hp_names(self, parsed_data_local):
        """ retreive the homepage names from parsed data """
        hp_names=[]
        for key in parsed_data_local:
            if "HOMEPAGE" in key:
                hp_names.append(parsed_data_local[key]['hp_dir_name'])
        return hp_names

    def walk_directories(self, hp_dir_name, blacklist):
        """ walk thru directories and create directory list
            and send dir_list to gui """
        # parse hp root directory (level 1)
        os.chdir(hp_dir_name)
        dir_list_1 = next(os.walk(hp_dir_name))[1]
        for item in blacklist:
            try:
                dir_list_1.remove(item)
            except:
                continue
        dir_list_1.sort()                   # alphabetical sort
        # parse second level
        dir_list_2 = []
        for i in range(len(dir_list_1)):
            dir_name = hp_dir_name + '/' + dir_list_1[i]
            os.chdir(dir_name)
            dir_list_2.append(next(os.walk(dir_name))[1])
            for item in blacklist:
                try:
                    dir_list_2[i].remove(item)
                except:
                    continue
        for i in range(len(dir_list_1)):         # alphabetical sort
            for j in range(len(dir_list_2[i])):
                dir_list_2[i].sort()
        # parse third level
        dir_list_3 = p = [[] for x in range(len(dir_list_1))]
        for i in range(len(dir_list_1)):
            nr_dirs_l2_i = len(dir_list_2[i])
            for j in range (nr_dirs_l2_i):
                dir_name = hp_dir_name + '/' + dir_list_1[i] + '/' + dir_list_2[i][j]
                os.chdir(dir_name)
                dir_list_3[i].append(next(os.walk(dir_name))[1])
                for item in blacklist:
                    try:
                        dir_list_3[i][j].remove(item)
                    except:
                        continue
        for i in range(len(dir_list_1)):   # alphabetical sort
            for j in range(len(dir_list_2[i])):
                dir_list_3[i][j].sort()
        os.chdir(hp_dir_name)
        dir_list = [dir_list_1, dir_list_2, dir_list_3]
        return  dir_list # return directory list

    def generate_css(self, parsed_data_css, hp_dir_name):
        """ css generator using config file and css_template.css. """
        os.chdir(hp_dir_name)
        # open template file
        try:
            css_template = open('css_template.css', 'r')
        except IOError:
            error_text = "Cannot open css.template.css\n"
            print(error_text, end='')
            self.queue_2_gui.put(error_text)
            return -1
        try:
            css = open('index.css', 'w')
        except IOError:
            error_text = "Cannot write to index.css\n"
            print(error_text, end='')
            self.queue_2_gui.put(error_text)
            return -1
        page_colors = []
        page_colors.append(parsed_data_css['pagecolor0'].split(','))
        page_colors.append(parsed_data_css['pagecolor1'].split(','))
        page_colors.append(parsed_data_css['pagecolor2'].split(','))
        page_colors.append(parsed_data_css['pagecolor3'].split(','))
        page_colors.append(parsed_data_css['pagecolor4'].split(','))
        page_colors.append(parsed_data_css['pagecolor5'].split(','))
        page_colors.append(parsed_data_css['pagecolor6'].split(','))
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

    def create_index_file(self, md_file, level, dir_nr_l0, dir_nr_l1, dir_nr_l2, dir_list):
        """ create the file "index.html" from md-file and data from dir_list """
        html = []
        hp_title = 'default'
        hp_keywords = ''
        hp_sidebar = []
        hp_content = ''
        hp_lup = ''
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
        for i in range(len(dir_list[0])): # dirs in level 1
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
                    ar = ''
                    for item in self.archives_flist:
                        if (item[-1]) == dir_list[1][dir_nr_l0][i]:
                            ar = ' id="ar"'
                    html.append('  <li{0} ><a href="{1}/index.html" title="{1}">{1}</'
                                'a></li>\n'.format(ar, str(dir_list[1][dir_nr_l1][i])))
            if (level == 2) or (level == 3):
                html.append('  <li class = "sbact"><a href="../index.html" title='
                            '"{0}">{0}</a></li>'
                            '\n'.format(str(dir_list[0][dir_nr_l0]))) # back to level 1
                for i in range(len(dir_list[1][dir_nr_l0])):
                    if level == 2:
                        ar = ''
                        for item in self.archives_flist:
                            if (item[-1]) == dir_list[1][dir_nr_l0][i]:
                                ar = ' id="ar"'
                        if i == dir_nr_l1:  # mark active sidebar item
                            html.append('  <li class = "sbact"{0} '.format(ar))
                        else:
                            html.append('  <li ')
                        html.append('><a href="../{0}/index.html" title="{0}">{0}</a>'
                                    '</li>\n'.format(str(dir_list[1][dir_nr_l0][i])))
                        for j in range(len(dir_list[2][dir_nr_l0][dir_nr_l1])):
                            ar = ''
                            for item in self.archives_flist:
                                if (item[-1]) == dir_list[2][dir_nr_l0][dir_nr_l1][j]:
                                    ar = ' id="ar"'
                            if i == dir_nr_l1:  # mark active sidebar item
                                html.append('  <li class = "sbact"{0} '.format(ar))
                                html.append('><a href="{0}/index.html" title="{0}">{0}</a>'
                                            '</li>\n'.format(str(dir_list[2][dir_nr_l0][dir_nr_l1][j])))
                    if level == 3:
                        ar = ''
                        for item in self.archives_flist:
                            if (item[-1]) == dir_list[1][dir_nr_l0][i]:
                                ar = ' id="ar"'
                        if i == dir_nr_l1:  # mark active sidebar item
                            html.append('  <li class = "sbact"{0} '.format(ar))
                        else:
                            html.append('  <li ')
                        html.append('><a href="../../{0}/index.html" title="{0}">{0}</a>'
                                    '</li>\n'.format(str(dir_list[1][dir_nr_l0][i])))
                        for j in range(len(dir_list[2][dir_nr_l0][dir_nr_l1])):
                            ar = ''
                            for item in self.archives_flist:
                                if (item[-1]) == dir_list[2][dir_nr_l0][dir_nr_l1][j]:
                                    ar = ' id="ar"'
                            if i == dir_nr_l1:
                                if j == dir_nr_l2:  # mark active sidebar item
                                    html.append('  <li class = "sbact"{0} '.format(ar))
                                else:
                                    html.append('  <li ')
                                html.append('><a href="../{0}/index.html" title="{0}">{0}</a>'
                                            '</li>\n'.format(str(dir_list[2][dir_nr_l0][dir_nr_l1][j])))
            # add sidebar items from md file
            for i in range(len(hp_sidebar)):
                print("???????????????????????????????????????????")
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

    def generate_sitemap(self, hp_dir_name, dir_list):
        """ generate sitemap """
        os.chdir(hp_dir_name)
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
                  '| [/](index.html "starting page") | <pre></pre> | '
                  'starting page |\n'
                  '| [/disclaimer.html](disclaimer.html "disclaimer") | <pre>'
                  '</pre> | disclaimer and copyright |\n'
                  '| [/news.html](news.html "News") | <pre></pre> | '
                  'news |\n'
                  '| [/sitemap.html](sitemap.html "this page") | <pre>'
                  '</pre> | this page |\n')
        for i in range(len(dir_list[0])):
            f_sm.write('| <hr /> | <pre>        </pre> | <hr /> |\n'
                      '| [/{0}]({0}/index.html "{0}") | <pre></pre> | {0}'
                      ' |\n'.format(dir_list[0][i].replace('_', r'\_')))
            for j in range(len(dir_list[1][i])):
                f_sm.write('| [&#8239;&#8239;&#8239;&#8239;&#8239;&#8239;/{0}]'
                          '({1}/{0}/index.html "{0}") | <pre></pre> | {0} |\n'
                          .format(dir_list[1][i][j].replace('_', r'\_'),
                                  dir_list[0][i].replace('_', r'\_')))
                for k in range(len(dir_list[2][i][j])):
                    f_sm.write('| [&#8239;&#8239;&#8239;&#8239;&#8239;&#8239;'
                              '&#8239;&#8239;&#8239;&#8239;&#8239;&#8239;/{0}]'
                              '({2}/{1}/{0}/index.html "{0}") | <pre></pre> | {0} |\n'
                              .format(dir_list[2][i][j][k].replace('_', r'\_'),
                                      dir_list[1][i][j].replace('_', r'\_'),
                                      dir_list[0][i].replace('_', r'\_')))
        f_sm.write('<br />\n[CONTENT_END]')
        f_sm.close()

    def generate_index_files(self, hp_dir_name, dir_list):
        """ homepage generator: walk thru all dirs and create all index_files """
        # first root dir
        os.chdir(hp_dir_name)
        print(hp_dir_name)
        text = "Creating Homepage:\n"
        print(text)
        self.queue_2_gui.put(text)
        md_file_list = glob('*.md')
        if 'news.md' in md_file_list:
            self.create_index_file('news.md', 0, 0, 0, 0, dir_list)
            md_file_list.remove('news.md')
        if 'sitemap.md' in md_file_list:
            self.create_index_file('sitemap.md', 0, 0, 0, 0, dir_list)
            md_file_list.remove('sitemap.md')
        if 'disclaimer.md' in md_file_list:
            self.create_index_file('disclaimer.md', 0, 0, 0, 0, dir_list)
            md_file_list.remove('disclaimer.md')
        if len(md_file_list) != 1:
            print("Error: no md file or more than one md file (except news.md,"
                  "sitemap.md, disclaimer.md and css.md) in ", hp_dir_name)
        try:
            md_file = md_file_list[0]
        except IndexError:
            error_text = "IndexError in generate(hp)\n"
            print(error_text, end='')
            self.queue_2_gui.put(error_text)
            return -1
        self.create_index_file(md_file, 0, 0, 0, 0, dir_list)
        # create index files in level 1
        for i in range(len(dir_list[0])):
            print(self.progress_char,end='')
            self.queue_2_gui.put(self.progress_char)
            os.chdir(hp_dir_name + '/' + dir_list[0][i])
            md_file = dir_list[0][i]+'.md'
            md_file_list = glob('*.md')
            if md_file not in md_file_list:
                text = "Error: no valid md file '" + md_file + "' in " + os.getcwd()
                print(text)
                self.queue_2_gui.put(text)
            else:
                self.create_index_file(md_file, 1, i, i, 0, dir_list)
        # create index files in level 2
        for i in range(len(dir_list[0])):
            for j in range(len(dir_list[1][i])):
                print(self.progress_char,end='')
                self.queue_2_gui.put(self.progress_char)
                os.chdir(hp_dir_name + '/' + dir_list[0][i] + '/'
                        + dir_list[1][i][j])
                md_file = dir_list[1][i][j]+'.md'
                md_file_list = glob('*.md')
                if md_file not in md_file_list:
                    text = "Error: no valid md file '" + md_file + "' in " + os.getcwd()
                    self.queue_2_gui.put(text)
                else:
                    self.create_index_file(md_file, 2, i, j, 0, dir_list)
        # create index files in level 3
        for i in range(len(dir_list[0])):
            for j in range(len(dir_list[1][i])):
                for k in range(len(dir_list[2][i][j])):
                    print(self.progress_char,end='')
                    self.queue_2_gui.put(self.progress_char)
                    os.chdir(hp_dir_name + '/' + dir_list[0][i] + '/'
                        + dir_list[1][i][j] + '/' + dir_list[2][i][j][k])
                    md_file = dir_list[2][i][j][k]+'.md'
                    md_file_list = glob('*.md')
                    if md_file not in md_file_list:
                        text = "Error: no valid md file '" + md_file + "' in " + os.getcwd()
                        print(text)
                        self.queue_2_gui.put(text)
                    else:
                        self.create_index_file(md_file, 3, i, j, k, dir_list)
        text = "\nHomepage created!\n"
        print(text)
        self.queue_2_gui.put(text)

    def sync_dir(self, sftp, local_dir, remote_dir):
        if not remote_dir.endswith('/'):
            remote_dir += '/'
        if not local_dir.endswith('/'):
            local_dir += '/'
        try:                                # Ensure remote directory exists
            sftp.stat(remote_dir)
            print(f"Remote directory exists: {remote_dir}")
        except FileNotFoundError:
            print(f"Remote directory does not exist: {remote_dir}")
            sftp.mkdir(remote_dir)
        except Exception as e:
            print(f"Error checking remote directory: {e}")
            return
        local_files = os.listdir(local_dir) # Compare local and remote directories
        print(f"Local files: {local_files}")
        try:
            remote_files = sftp.listdir(remote_dir)
            print(f"Remote files: {remote_files}")
        except Exception as e:
            print(f"Error listing remote directory: {e}")
            return
        for file in local_files:            # Upload new and modified files
            local_path = os.path.join(local_dir, file)
            remote_path = remote_dir + file
            if os.path.isdir(local_path):
                self.sync_dir(local_path, remote_path)
            else:
                try:
                    upload_file = False
                    if file not in remote_files:
                        upload_file = True
                    else:
                        local_stat = os.stat(local_path)
                        remote_stat = sftp.stat(remote_path)
                        if local_stat.st_size != remote_stat.st_size or local_stat.st_mtime > remote_stat.st_mtime:
                            upload_file = True
                    if upload_file:
                        print(f"Uploading file: {local_path} to {remote_path}")
                        sftp.put(local_path, remote_path)
                except Exception as e:
                    print(f"Error uploading file {local_path} to {remote_path}: {e}")
        for file in remote_files:  # Remove files if only in the remote directory
            remote_path = remote_dir + file
            local_path = os.path.join(local_dir, file)
            if file not in local_files:
                try:
                    if sftp.stat(remote_path).st_mode & 0o40000:  # Check if it's a directory
                        print(f"Removing remote directory: {remote_path}")
                        sftp.rmdir(remote_path)
                    else:
                        print(f"Removing remote file: {remote_path}")
                        sftp.remove(remote_path)
                except Exception as e:
                    print(f"Error removing remote file or directory {remote_path}: {e}")

    def create_hp(self, parsed_data_local, chosen_hp_dir_name, chosen_hp_dir_index):
        """ create homepage for chosen hp_directory_name
            first check if local config file """
        parser_local = ConfigParser()
        try:
            self.hp_dir_name = chosen_hp_dir_name
            self.hp_dir_index = chosen_hp_dir_index
            os.chdir(self.hp_dir_name)
            if not parser_local.read(self.config_file):  # check if local config file
                text = f"{self.config_file} is missing in {os.getcwd()}\ndefault data from PYSHPCREATOR directory is used\n"
                print(text)
                self.queue_2_gui.put(text)
                try:
                    blacklist = parsed_data_local['BLACKLIST']['blacklist'].split(',')
                except KeyError:
                    text = "No 'BLACKLIST' key in parsed_data_local\n"
                    print(text)
                    self.queue_2_gui.put(text)
                    blacklist = []
            else:
                try:
                    blacklist = parser_local.get('BLACKLIST', 'blacklist').split(',')
                except NoSectionError:
                    text = f"No section: 'BLACKLIST' in {self.config_file}\nUsing default blacklist from parsed_data_local\n"
                    print(text)
                    self.queue_2_gui.put(text)
                    try:
                        blacklist = parsed_data_local['BLACKLIST']['blacklist'].split(',')
                    except KeyError:
                        text = "No 'BLACKLIST' key in parsed_data_local\n"
                        print(text)
                        self.queue_2_gui.put(text)
                        blacklist = []
                for key in parsed_data_local['CSS']:
                    try:
                        parsed_data_local['CSS'][key] = parser_local.get('CSS', key)
                    except NoSectionError:
                        text = f"No section: 'CSS' in {self.config_file}\nUsing default CSS from parsed_data_local\n"
                        print(text)
                        self.queue_2_gui.put(text)
            self.generate_css(parsed_data_local['CSS'], self.hp_dir_name)
            dir_list = self.walk_directories(self.hp_dir_name, blacklist)
            self.move_archive_files_to_end(self.hp_dir_name, dir_list)
            self.archive_list = self.create_archive_list(self.hp_dir_name, dir_list)
            self.send_2_gui_dir_lists(self.hp_dir_name, dir_list)
            self.generate_sitemap(self.hp_dir_name, dir_list)
            self.generate_index_files(self.hp_dir_name, dir_list)
            self.hp_was_created = True
        except (ValueError,IndexError):
            pass

    def quick_links(self, hp_dir_name, filename):
        aql = AddQuickLinks(hp_dir_name, filename)
        aql.add_quick_links()

    def check_links(self, local_dir):
        os.chdir(self.script_dir)
        text = f"Checking links in all HTML files in folder {local_dir}.\n" \
                "This may take some time!\n"
        self.queue_2_gui.put(text)
        cl = CheckLinks(local_dir)
        text = cl.check_links()
        self.queue_2_gui.put(text)

    def upload(self, parsed_data_local):
        if self.hp_was_created:
            index = str(int(self.hp_dir_index)+1)
            url = parsed_data_local[f"HOMEPAGE_{index}"]["url"]
            login = parsed_data_local[f"HOMEPAGE_{index}"]["login"]
            password = parsed_data_local[f"HOMEPAGE_{index}"]["password"]
            sport = parsed_data_local[f"HOMEPAGE_{index}"]["port"]
            source = self.hp_dir_name
            destination = parsed_data_local[f"HOMEPAGE_{index}"]["destination"]
            text = f"Connecting to {url} with username {login}\n" \
                    "Please wait while uploading\nThis will take some time!"
            self.queue_2_gui.put(text)
            up = Upload(self.hp_dir_name, destination, url, login, password, sport)
            text = up.upload()
            self.queue_2_gui.put(text)
            self.hp_was_created = False
        else:
            text = "No homepage created yet!\nPlease create a homepage first!\n"
            print(text)
            self.queue_2_gui.put(text)


###### Helper functions ######################################################

    def get_coordinates_of_archive_files(self, data, coordinates=[]):
        if isinstance(data, list):
            for index, item in enumerate(data):
                self.get_coordinates_of_archive_files(item, coordinates + [index])
        else:
            if data == "a":
                self.archives_clist.append(coordinates)

    def create_archive_list(self, hp_dir_name, dir_list):
        """ Create a list similar to dir_list with idle items.
            Mark places with archive folders with letter 'a' """
        a_list = copy.deepcopy(dir_list)  # create a copy of the directory list
        for i in range(len(a_list[0])): # clear the archive list
            a_list[0][i] = ""
            for j in range(len(a_list[1][i])):
                a_list[1][i][j] = ""
                for k in range(len(a_list[2][i][j])):
                    a_list[2][i][j][k] = ""
        for i in range(len(dir_list[0])):     # create the new archive list
            for j in range(len(dir_list[1][i])):
                dir_name = os.path.join(hp_dir_name, dir_list[0][i], dir_list[1][i][j])
                os.chdir(dir_name)
                files = next(os.walk(dir_name))[2]
                if "archive" in files:
                    a_list[1][i][j] = "a"
                for k in range(len(dir_list[2][i][j])):
                    dir_name = os.path.join(hp_dir_name, dir_list[0][i], dir_list[1][i][j], dir_list[2][i][j][k])
                    os.chdir(dir_name)
                    files = next(os.walk(dir_name))[2]
                    if "archive" in files:
                        a_list[2][i][j][k] = "a"
        self.get_coordinates_of_archive_files(a_list)
        ac_list = self.archives_clist
        af_list = copy.deepcopy(ac_list)  # create a copy of the directory n
        for i in range (len(ac_list)):
            if len(ac_list[i]) == 3:
                filename = dir_list[ac_list[i][0]][ac_list[i][1]][ac_list[i][2]]
                #print(filename)
                af_list[i].append(filename)
            if len(ac_list[i]) == 4:
                filename = dir_list[ac_list[i][0]][ac_list[i][1]][ac_list[i][2]][ac_list[i][3]]
                #print(filename)
                af_list[i].append(filename)
                self.archives_flist = af_list
        return af_list

    def move_archive_files_to_end(self, hp_dir_name, dir_list):
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
                    #print(dir_name)
                    os.chdir(dir_name)
                    files = next(os.walk(dir_name))[2]
                    if "archive" in files:
                        to_move.append((i, j, k, dir_list[2][i][j][k]))
        for item in to_move:
                #print(f"Item {item}")
                dir_list[2][item[0]][item[1]].remove(item[3])
                dir_list[2][item[0]][item[1]].append(item[3])

    def send_2_gui_dir_lists(self, hp_dir_name, dir_list):
        """ Get directory list, check links list and list for
            quick links list and send to Gui """
        # Directory list for GUI window
        text = "--------------------------------\n"
        for i in range(len(dir_list[0])):
            text = text + (dir_list[0][i]) + '\n'
            for j in range(len(dir_list[1][i])):
                text = text + '    {0}'.format(dir_list[1][i][j]) + '\n'
                for k in range(len(dir_list[2][i][j])):
                    text = text + '        {0}'.format(dir_list[2][i][j][k]) + '\n'
        text = text + "--------------------------------\n"
        self.queue_2_gui.put(text)
        # File list for quick links combobox
        text = "File_list_4_quick_links:"
        for i in range(len(dir_list[0])):
            text = text + '\n' + (dir_list[0][i]) + ".md"
            for j in range(len(dir_list[1][i])):
                text = text + '\n' + '    {0}'.format(dir_list[1][i][j]) + ".md"
                for k in range(len(dir_list[2][i][j])):
                    text = text + '\n' + '        {0}'.format(dir_list[2][i][j][k]) + ".md"
        self.queue_2_gui.put(text)
        # Directory list for links checker combobox
        text = "Dir_list_4_links_2_check:"
        for i in range(len(dir_list[0])):
            text = text + '\n' + hp_dir_name + "/" + (dir_list[0][i])
        self.queue_2_gui.put(text)

