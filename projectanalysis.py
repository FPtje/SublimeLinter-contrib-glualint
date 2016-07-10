import sublime, sublime_plugin, os.path

class AnalyseGlobalsLuaCommand(sublime_plugin.TextCommand):
    """
    Finds all globals in the project
    """
    def run(self, edit):
        view = self.view
        path = self.projectPath(view)

        import subprocess
        import os

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        print(["glualint", " --analyse-globals", path])
        popen = subprocess.Popen(["glualint", "--analyse-globals", path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=startupinfo
        )

        try:
            output, errs = popen.communicate(input="", timeout=20)

            newView = view.window().new_file()
            newView.set_name("Found globals")
            # newView.set_syntax_file("Packages/Default/Find Results.hidden-tmLanguage")
            newView.set_scratch(True)
            newView.run_command("analyse_globals_lua_insert", {'text': output, 'path': path})
            newView.set_read_only(True)
        except subprocess.TimeoutExpired:
            popen.kill()
            sublime.status_message("The glualint process froze!")
        except subprocess.SubprocessError:
            sublime.status_message("Unable to pretty find globals!")


    def projectPath(self, view):
        window = view.window()
        folders = window.folders()
        filename = os.path.realpath(view.file_name())

        if filename is None:
            sublime.status_message("This file is not part of a project in the sidebar!")
            return

        for folder in folders:
            if filename.startswith(os.path.realpath(folder)):
                return folder

        sublime.status_message("This file is not part of a project in the sidebar!")



class AnalyseGlobalsLuaInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, text="", path="unknown"):
        self.view.insert(edit, self.view.text_point(0, 0), "Globals found in " + path + ":\n\n" + ("No globals found" if text == "" else text))
