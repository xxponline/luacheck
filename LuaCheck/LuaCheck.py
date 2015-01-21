import sublime, sublime_plugin
import subprocess
import string
import re
import io

class luacheckCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# v = self.view
		# pt1 = 0
		# # Example comment to see how it looks like
		# pt2 = pt1 + v.insert(edit, pt1, "This is a comment\n")
		# pt3 = pt2 + v.insert(edit, pt2, "This is a string\n")
		# v.add_regions('foo_comment', [sublime.Region(pt1, pt2)], 'comment')
		# v.add_regions('foo_string', [sublime.Region(pt2, pt3)], 'string')
		luacPath = sublime.load_settings("Preferences.sublime-settings").get("luacheck_luacPath")
		if luacPath == None:
			sublime.error_message("luac Path is not define!")
			return

		if self.view.is_dirty():
			sublime.error_message("file not save!")
			return
		file_name = self.view.file_name()
		if (file_name == None) or (not file_name.endswith(".lua")):
			sublime.status_message("this file is not lua file")
			return

		old_regions = self.view.get_regions("err_line_sign")
		self.view.add_regions('err_line_sign', old_regions, '')
		checkProcess = subprocess.Popen([luacPath,"-p",file_name],stderr=subprocess.PIPE)
		checkProcess.wait()
		if checkProcess.returncode == 0:
			self.view.erase_regions('err_line_sign')
			sublime.status_message("greate!")
		else:
			err_text = io.TextIOWrapper(checkProcess.stderr,
                       newline=None).read()
			pattern = re.compile("".join([file_name,":(\d+):","(.+)"]))
			match = pattern.search(err_text)
			err_line , err_info = match.groups()
			err_line_num = int(err_line)
			self.view.run_command("goto_line", {"line": err_line_num})
			pt = self.view.text_point(err_line_num - 1, 0)
			err_line_r = self.view.line(pt)
			self.view.add_regions('err_line_sign', [err_line_r], 'string' , 'bookmark' , sublime.DRAW_OUTLINED)
			sublime.status_message(err_info)