#   The MIT License (MIT)

#   Copyright (c) 2014 Maximilien Riehl <max@riehl.io>

#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:

#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.

import os
import subprocess
import sys
import threading
import fcntl
import errno
import select

import sublime
import sublime_plugin

global panel  # ugly - but view.get_output_panel recreates the output panel
              # each time it is called, which sucks
panel = None

if sys.version_info < (3, 3):
    raise RuntimeError('EasyPyb is only compatible with Sublime Text 3')


def defer_with_progress(args, cwd=None):
    thread = threading.Thread(
        target=spawn_command_with_realtime_output, args=(args, cwd))
    thread.start()
    ThreadProgress(thread, 'PyBuilder running', 'PyBuilder finished')


def spawn_command_with_realtime_output(args, cwd):
    child = subprocess.Popen(
        args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    flag_fd_as_async(child.stdout)
    flag_fd_as_async(child.stderr)

    while True:
        select.select([child.stdout, child.stderr], [], [])

        stdout = read_async(child.stdout)
        stderr = read_async(child.stderr)

        if stdout:
            scratch(stdout.decode('utf-8'))
        if stderr:
            scratch(stderr.decode('utf-8'))

        finished = child.poll() is not None

        if finished:
            return


def flag_fd_as_async(fd):
    fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(
        fd, fcntl.F_GETFL) | os.O_NONBLOCK)


def read_async(fd):
    try:
        return fd.read()
    except IOError as e:
        if e.errno != errno.EAGAIN:
            raise e
        else:
            return ''


def plugin_loaded():
    pass


def plugin_unloaded():
    pass


def run_pybuilder():
    window = sublime.active_window()
    view = window.active_view()
    interpreter = view.settings().get('python_interpreter')
    if not interpreter:
        sublime.error_message('No configured python_interpreter')
        return
    project_root = view.settings().get('project_root')
    if not project_root:
        sublime.error_message('No configured project_root')
        return
    bin_dir = os.path.dirname(interpreter)
    pyb_script = os.path.join(bin_dir, 'pyb')
    scratch('Build started...\n', new_panel=True)

    defer_with_progress([pyb_script], cwd=project_root)


def scratch(text, new_panel=False):
    global panel
    if new_panel:
        window = sublime.active_window()
        panel = window.get_output_panel("easypyb")
    sublime.active_window().run_command('scratch_text', {'text': text})


class EasyPybRun(sublime_plugin.ApplicationCommand):

    def run(self):
        sublime.set_timeout(run_pybuilder, 0)


class ScratchText(sublime_plugin.TextCommand):

    def run(self, edit, text):
        window = sublime.active_window()
        panel.insert(edit, panel.size(), text)
        panel.show(panel.size())
        panel_active = panel.id() == window.active_view().id()
        if not panel_active:
            window.run_command("show_panel", {"panel": "output.easypyb"})


class ThreadProgress():

    """
    Animates an indicator, [=   ], in the status area while a thread runs
    Conveniently grabbed and modified from the Package Control source (MIT
    licensed) but not considered a "substantial portion".
    """

    def __init__(self, thread, message, success_message):
        self.thread = thread
        self.message = message
        self.success_message = success_message
        self.addend = 1
        self.size = 8
        sublime.set_timeout(lambda: self.run(0), 100)

    def run(self, i):
        if not self.thread.is_alive():
            if hasattr(self.thread, 'result') and not self.thread.result:
                sublime.status_message('')
                return
            sublime.status_message(self.success_message)
            return

        before = i % self.size
        after = (self.size - 1) - before

        sublime.status_message('%s [%s=%s]' %
                              (self.message, ' ' * before, ' ' * after))

        if not after:
            self.addend = -1
        if not before:
            self.addend = 1
        i += self.addend
        sublime.set_timeout(lambda: self.run(i), 100)
