import sublime, sublime_plugin
from os import sep as path_separator
from os.path import exists as exists_path
import subprocess, signal
import os
import re

class StopRustWebAppCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        path_to_file = self.view.file_name().split(path_separator)
        is_win_os = sublime.platform() == "windows";

        while len(path_to_file) > 0:
            path_to_file.pop()
            path_to_dir = path_separator.join(path_to_file)
            path_to_toml = path_to_dir + path_separator + "Cargo.toml"

            if not exists_path(path_to_toml):
                continue

            project_name = None

            with open(path_to_toml, 'r') as file_toml:
                for text in file_toml:

                    # find text: name = "
                    compare = re.search( 'name([^\w])+', text)
                    if compare is None:
                        continue

                    start_name_pos = compare.end()
                    end_name_pos = text.find('"', start_name_pos)

                    if end_name_pos > 0:
                        project_name = text[start_name_pos:end_name_pos]
                        project_name += ".exe" if is_win_os else ""
                        break

            if project_name is None:
                return

            path_to_debug_app = path_separator.join( [path_to_dir, "target","debug", project_name] )

            if not exists_path(path_to_debug_app):
                return

            if is_win_os:
                subprocess.call("taskkill -f /im " + project_name, shell=True)

            else:
                subprocess.call("killall " + project_name, shell=True)

            break