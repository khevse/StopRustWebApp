import sublime, sublime_plugin
from os import sep as path_separator
from os.path import exists as exists_path, isfile
import subprocess, signal
import os
import re

class StopWebAppCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        path_to_file = self.view.file_name().split(path_separator)
        file_name = path_to_file[-1]

        if file_name.endswith('.rs'):
            self.__stop_rust_app(path_to_file)
        elif file_name.endswith('.js'):
            self.__stop_nodejs_app(path_to_file)
        elif file_name.endswith('.go'):
            self.__stop_go_app(path_to_file)

    def __stop_go_app(self, path_to_file):
        EXTENTION = '.go'

        while len(path_to_file)>2:
            path_to_file.pop()
            directory = path_separator.join(path_to_file)

            has_files = False
            for file_name in os.listdir(directory):
                if not isfile(file_name) or not file_name.endswith(EXTENTION):
                    continue

                has_files = True
                name_without_extention = file_name[:-len(EXTENTION)]
                self.__kill_process(name_without_extention, with_excepton = False)
                print(name_without_extention)

            if not has_files:
                break

    def __stop_nodejs_app(self, path_to_file):
        # Other version:
        # use supervisor (https://github.com/petruisfan/node-supervisor)
        self.__kill_process('node')

    def __stop_rust_app(self, path_to_file):
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
                        break

            if project_name is None:
                return

            path_to_debug_app = path_separator.join( [path_to_dir, "target","debug", project_name] )

            if not exists_path(path_to_debug_app):
                return

            self.__kill_process(project_name)
            break

    def __kill_process(self, process_name, with_excepton = True):
        if sublime.platform() == "windows":
            subprocess.call('taskkill -f /im {0}.exe'.format(process_name), shell=True)
        else:
            p = subprocess.Popen("ps -A|grep " + process_name,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                               )
            out, err = p.communicate()
            if not err is None:
                raise str(err)

            process_pid = None
            for line in out.splitlines():
                substrs = line.split(None, 3)
                if len(substrs) < 3:
                    continue

                pid = int(substrs[0]);
                name = substrs[3].decode('utf-8');
                if name == process_name:
                    process_pid = pid
                    break

            if with_excepton and process_pid is None:
                raise Exception('Process "{0}" not found.'.format(process_name))

            if not process_pid is None:
                os.kill(process_pid, signal.SIGKILL)

            # Other version:
            # subprocess.call("killall " + project_name, shell=True)