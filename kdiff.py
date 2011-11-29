import sublime, sublime_plugin  

import subprocess
import os.path
import os

# Extends TextCommand so that run() receives a View to modify.  
# class DuplicateCommand(sublime_plugin.TextCommand):  
#     def run(self, view, args):  
#         print "duplicate"
#         # Walk through each region in the selection  
#         for region in view.sel():  
#             # Only interested in empty regions, otherwise they may span multiple  
#             # lines, which doesn't make sense for this command.  
#             if region.empty():  
#                 # Expand the region to the full line it resides on, excluding the newline  
#                 line = view.line(region)  
#                 # Extract the string for the line, and add a newline  
#                 lineContents = view.substr(line) + '\n'  
#                 # Add the text at the beginning of the line  
#                 view.insert(line.begin(), lineContents)

def debug_print(str):
    print "KDIFF", str


g_fname_last = None
g_fname_current = None

g_default_path_windows = "\"C:\\Program Files\\KDiff3\\kdiff3.exe\""
g_default_path_windowsx64 = "C:\\Program Files (x86)\\KDiff3\\kdiff3.exe"
g_default_path_osx = "/Application/kdiff3.app/somethingsomething"
g_default_locations = [g_default_path_windows, g_default_path_windowsx64, g_default_path_osx]

def is_osx():
    if hasattr(os, 'uname'):
        debug_print(os.uname())
        return "Darwin" in os.uname()
    else:
        return False

class kdiff_monitor(sublime_plugin.EventListener):
    def __init__(self):
        global g_fname_last, g_fname_current
        g_fname_last = None
        g_fname_current = None

    def on_activated(self, view):
        global g_fname_last, g_fname_current
        # debug_print("ACTIVATED: %s" % (view.file_name()))
        
        if not view.file_name() is None and (view.file_name() != g_fname_current):
            g_fname_last = g_fname_current
            g_fname_current = view.file_name()
        # debug_print("current: %s   last:%s" % ( g_fname_last, g_fname_current   ))



class kdiffChangeExecutablePathCommand(sublime_plugin.WindowCommand):
    def run(self):
        debug_print("ChangeExecutablePathCommand")
        self.window.show_input_panel('Full path of kdiff executable', '', self.on_done,
            self.on_change, self.on_cancel)

    def on_done(self, input):
        settings = sublime.load_settings(__name__ + '.sublime-settings')
        if len(input) == 0:
            # debug_print("length %d" % len(input))
            settings.set('executable_path', None)
            sublime.save_settings(__name__ + '.sublime-settings')
            sublime.status_message('Kdiff path cleared')
        else:
            is_file = os.path.isfile(input)
            if not is_file:
                executable_path = settings.get('executable_path', [])
                sublime.status_message('Invalid Kdiff path ' + input + '. Path still set to ' + executable_path)
            else:
                executable_path = settings.get('executable_path', [])
                if not executable_path:
                    if is_osx():
                        executable_path = g_default_path_osx
                    else:
                        executable_path = g_default_path_windows
                executable_path = input
                settings.set('executable_path', executable_path)
                sublime.save_settings(__name__ + '.sublime-settings')
                sublime.status_message('Kdiff path set to ' + input)

    def on_change(self, input):
        pass

    def on_cancel(self):
        pass


class kdiffRunCommand(sublime_plugin.TextCommand):

    def run(self, args):  
        # view = self.view
        global g_fname_last, g_fname_current
        is_osx()
        
        if g_fname_last is None:
            debug_print("current: %s   last:%s" % ( g_fname_last, g_fname_current   ))
            debug_print("error: cannot compare, last file is none")
            sublime.status_message("error: cannot compare, last file is none")
        elif g_fname_current is None:
            debug_print("current: %s   last:%s" % ( g_fname_last, g_fname_current   ))
            debug_print("error: cannot compare, current file is none")
            sublime.status_message("error: cannot compare, current file is none")
        else:
            settings = sublime.load_settings(__name__ + '.sublime-settings')
            executable_path = settings.get('executable_path', None)
            if executable_path is None:
                for p in g_default_locations:
                    if os.path.isfile(p):
                        executable_path = p
                        debug_print("using default path '%s'" % p)
                        break
            is_file = os.path.isfile(executable_path)

            if not is_file:
                err_msg = 'Invalid Kdiff path ' + executable_path + '. Please make sure Kdiff is installed run Kdiff : Update Path'
                debug_print(err_msg)
                sublime.status_message(err_msg)
            else:
                os_command = executable_path

                sublime.status_message('Comparing current file with ' + g_fname_last)
                debug_print("Comparing current: %s   last:%s" % (g_fname_last, g_fname_current))

                if is_osx():
                    subprocess.Popen([os_command, g_fname_last, g_fname_current])
                else:
                    #windows
                    os_args = "\"%s\" \"%s\"" %  (g_fname_last, g_fname_current)
                    # os.spawnlp(os.P_NOWAIT, os_command, "kdiff", os_args)

                    command_line = "\"%s\" %s" % (os_command, os_args)
                    
                    # print "SYSTEM:", os.system(command_line)
                    subprocess.Popen(command_line)
                    # debug_print(command_line)
                    # debug_print(os_command)
                    # debug_print(os_args)
