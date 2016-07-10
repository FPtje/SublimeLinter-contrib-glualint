import sublime, sublime_plugin, os.path, re

def projectPath(view):
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

class AnalyseGlobalsLuaCommand(sublime_plugin.TextCommand):
    """
    Finds all globals in the project
    """
    def run(self, edit):
        view = self.view
        path = projectPath(view)

        import subprocess
        import os

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

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
            newView.run_command("lua_insert", {'text': output, 'path': path})
        except subprocess.TimeoutExpired:
            popen.kill()
            sublime.status_message("The glualint process froze!")
        except subprocess.SubprocessError:
            sublime.status_message("Unable to pretty find globals!")


class LintProjectLuaCommand(sublime_plugin.TextCommand):
    """
    Give lint messages for all files in a project
    """
    def run(self, edit):
        view = self.view
        path = projectPath(view)

        import subprocess
        import os



        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        popen = subprocess.Popen(["glualint", path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=startupinfo
        )

        try:
            output, errs = popen.communicate(input="", timeout=20)

            res = self.prettyPrintMessages(output)

            newView = view.window().new_file()
            newView.set_name("Lint messages")
            # newView.set_syntax_file("Packages/Default/Find Results.hidden-tmLanguage")
            newView.set_scratch(True)
            newView.run_command("lua_insert", {'text': res, 'path': path})
        except subprocess.TimeoutExpired:
            popen.kill()
            sublime.status_message("The glualint process froze!")
        except subprocess.SubprocessError:
            sublime.status_message("Unable to lint project!")

    def prettyPrintMessages(self, output):
        pattern = re.compile('(.+?): (\[((?P<error>Error)|(?P<warning>Warning))\] .*)')
        res = []

        # Contains file names on every even index
        # warnings/errors on all even indices
        filesNWarnings = re.findall(pattern, output)

        lastFile = ''
        for i in range(0, len(filesNWarnings)):
            file = filesNWarnings[i][0]
            message = filesNWarnings[i][1]

            if file != lastFile:
                res.append("")
                res.append(file + ":")
                lastFile = file

            res.append("    " + message)

        return "\n".join(res)


class LuaInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, text="", path="unknown"):
        self.view.insert(edit, self.view.text_point(0, 0), "Linter messages of " + path + ":\n\n" + ("No lint messages" if text == "" else text))
