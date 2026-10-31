import os
import os.path
import re
import subprocess

import sublime
import sublime_plugin


class PrettyPrintLuaCommand(sublime_plugin.TextCommand):
    """
    Replaces the selected text(s) with a pretty printed version
    """

    def run(self, edit):
        view = self.view

        for s in view.sel():
            if s.empty():
                continue

            txt = view.substr(s)
            self.prettyPrint(edit, s, txt)

    def prettyPrint(self, edit, selection, txt):
        view = self.view

        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        settings = view.settings()
        indent = (
            settings.get("translate_tabs_to_spaces")
            and settings.get("tab_size") * " "
            or "\t"
        )
        indent = "--indentation='" + indent + "'"
        file_name = view.file_name()
        cwd = os.path.dirname(os.path.realpath(file_name)) if file_name else None
        popen = subprocess.Popen(
            ["glualint", indent, "--pretty-print"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=False,
            startupinfo=startupinfo,
            cwd=cwd,
        )

        try:
            output, _errs = popen.communicate(input=txt.encode("utf-8"), timeout=10)
            output = output.replace(b"\r", b"")
            self.insertPrettyPrinted(edit, selection, output.decode("utf-8"))
        except subprocess.TimeoutExpired:
            popen.kill()
            sublime.status_message("The glualint process froze!")
        except subprocess.SubprocessError:
            sublime.status_message("Unable to pretty print code!")

    def insertPrettyPrinted(self, edit, selection, text):
        view = self.view
        beginLine = view.substr(view.line(selection.begin()))
        whitespace = re.match(r"\s*", beginLine).group()
        indented = text.replace("\n", "\n" + whitespace)
        indented = re.sub(r"\n(\s)+\n", "\n\n", indented)

        view.replace(edit, selection, indented)
