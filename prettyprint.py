import sublime, sublime_plugin

class PrettyPrintLuaCommand(sublime_plugin.TextCommand):
    """
    Replaces the selected text(s) with a pretty printed version
    """
    def run(self, edit):
        view = self.view

        for s in view.sel():
            if s.empty(): continue

            txt = view.substr(s)
            self.prettyPrint(edit, s, txt)

    def prettyPrint(self, edit, selection, txt):
        import subprocess
        import os
        view = self.view

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        settings = view.settings()
        indent = settings.get('translate_tabs_to_spaces') and settings.get('tab_size') * ' ' or '\t'
        indent = "--indentation='" + indent + "'"
        popen = subprocess.Popen(["glualint", indent, "--pretty-print"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=startupinfo
        )

        try:
            output, errs = popen.communicate(input=txt, timeout=10)
            self.insertPrettyPrinted(edit, selection, output)
        except subprocess.TimeoutExpired:
            popen.kill()
            sublime.status_message("The glualint process froze!")
        except subprocess.SubprocessError:
            sublime.status_message("Unable to pretty print code!")

    def insertPrettyPrinted(self, edit, selection, text):
        import re
        view = self.view
        beginLine = view.substr(view.line(selection.begin()))
        whitespace = re.match(r"\s*", beginLine).group()
        indented = text.replace("\n", "\n" + whitespace)

        view.replace(edit, selection, indented)
