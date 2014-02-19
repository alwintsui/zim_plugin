# -*- coding: utf-8 -*-

# Copyright 2014 Alwin Tsui <alwintsui@gmail.com>
# License:  same as zim (gpl)
# Usage: copy lines_arrange.py to directory zim/plugins/ 
#        sudo cp lines_arrange.py "$(dirname $(python -c 'import zim;print zim.__file__'))/plugins"

from __future__ import with_statement

import gtk

from zim.plugins import PluginClass
from zim.gui.widgets import ui_environment, MessageDialog

import logging
logger = logging.getLogger('zim.plugins.lines_arrange')

ui_xml = '''
<ui>
	<menubar name='menubar'>
		<menu action='format_menu'>
			<placeholder name='plugin_items'>
				<menuitem action='indent_selected_lines'/>
				<menuitem action='delete_blank_lines'/>
				<menuitem action='reduce_blank_lines'/>
				<menuitem action='sort_selected_lines'/>
			</placeholder>
		</menu>
	</menubar>
</ui>
'''

# in oder to provide dynamic key binding assignment the initiation is made in the plugin class
ui_actions = (
	# name, stock id, label, accelerator, tooltip, read only
	('indent_selected_lines', None, _('_Indent Lines'), '<ctrl><shift>I', '', False),
	('delete_blank_lines', None, _('_Delete Blank Lines'), '<ctrl><shift>D', _('Delete all blank lines'), False),
	('reduce_blank_lines', None, _('_Reduce Blank Lines'), '<ctrl><shift>R', _('Reduce many blank lines into only one'), False),
	('sort_selected_lines', 'gtk-sort-ascending', _('_Sort Lines'), '', '', False),
		# T: menu item for insert clipboard plugin
)


class LineArrangePlugin(PluginClass):
	'''FIXME'''

	plugin_info = {
		'name': _('Line Arrangement'), # T: plugin name
		'description': _('''\
This plugin arranges selected lines by functions:
1. to indent (and strip space charaters at the right and the left of) each line with the same indent level as the first selected line; 

2. to delete all blank lines of the selected lines;

3. to reduce all continous blank lines selected into only one.

4. to sort lines in alphabetical order, if the list is already sorted the order will be reversed (like 'Line Sorter' plugin); 
'''), # T: plugin description
		'author': 'Alwin Tsui <alwintsui@gmail.com>',
		'help': 'Plugins:Line Arrangement|Line Sorter',
	}

	def __init__(self, ui):
		PluginClass.__init__(self, ui)

	def initialize_ui(self, ui):
		if self.ui.ui_type == 'gtk':
			self.ui.add_actions(ui_actions, self)
			self.ui.add_ui(ui_xml, self)
	def get_selected_lines(self):
		buffer = self.ui.mainwindow.pageview.view.get_buffer()
		try:
			sel_start, sel_end = buffer.get_selection_bounds()
		except ValueError:
			MessageDialog(self.ui,
				_('Please select more than one line of text, first.')).run()
			return None
		first_lineno = sel_start.get_line()
		last_lineno = sel_end.get_line()

		with buffer.user_action:
			iter_end_line = buffer.get_iter_at_line(last_lineno)
			iter_end_line.forward_line() # include \n at end of line
			if iter_end_line.is_end() and not iter_end_line.starts_line():
				# no \n at end of buffer, insert it
				buffer.insert(iter_end_line, '\n')
				iter_end_line = buffer.get_end_iter()
			iter_begin_line = buffer.get_iter_at_line(first_lineno)
			lines = []
			for line_nr in range(first_lineno, last_lineno+1):
				start, end = buffer.get_line_bounds(line_nr)
				text = buffer.get_text(start, end)
				tree = buffer.get_parsetree(bounds=(start, end))
				lines.append((text, tree))
			buffer.delete(iter_begin_line, iter_end_line)
			self.mybuffer=buffer
			return lines

	def sort_selected_lines(self):
		lines=self.get_selected_lines()
		if not lines: return
		# sort this list of tuples, sort will look at first element of the tuple
		sorted_lines = sorted(lines, key=lambda lines: lines[0].lower().strip())
		# checks whether the list is sorted "a -> z", if so reverses its order
		if lines == sorted_lines:
			sorted_lines.reverse()
			# logger.debug("Sorted lines: %s",  sorted_lines)
		for line in sorted_lines: #sorted_lines:
			self.mybuffer.insert_parsetree_at_cursor(line[1])

	def indent_selected_lines(self):
		buffer = self.ui.mainwindow.pageview.view.get_buffer()
		try:
			sel_start, sel_end = buffer.get_selection_bounds()
			first_lineno = sel_start.get_line()
			last_lineno = sel_end.get_line()
		except ValueError:
			first_lineno = 0
			last_lineno = buffer.get_end_iter().get_line()

		with buffer.user_action:
			# Get the first indent
			ind_lev=buffer.get_indent(first_lineno)
			for line_nr in range(first_lineno, last_lineno+1):
				buffer.set_indent(line_nr,ind_lev) #same as the first
				start, end = buffer.get_line_bounds(line_nr)
				text = buffer.get_text(start, end)
				buffer.delete(start, end)
				buffer.insert_at_cursor(text.strip()+'\n') #strip

	def delete_blank_lines(self):
		lines=self.get_selected_lines()
		if not lines: return
		for line in lines:
			if (not line[0]) or line[0].isspace(): continue
			self.mybuffer.insert_parsetree_at_cursor(line[1])

	def reduce_blank_lines(self):
		lines=self.get_selected_lines()
		if not lines: return
		lastbk = False
		for line in lines:
			if (not line[0]) or line[0].isspace():
				if lastbk:
					continue
				else:
					lastbk=True
			else:
				lastbk= False
			self.mybuffer.insert_parsetree_at_cursor(line[1])
