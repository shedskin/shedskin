#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import sys

def unpack_unsigned(value):
	return value

def to_signed_byte(value):
	return value if value < 0x80 else -(256 - value)

class StatusDialog(gtk.Dialog):
	def __init__(self, *args, **kwargs):
		gtk.Dialog.__init__(self, *args, **kwargs)
		self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
		self.controls = {}
		for ID in ["A", "X", "Y", "SP", "PC"]:
			self.add_line(ID)

	def add_line(self, ID):
		box = gtk.HBox()
		label = gtk.Label(ID)
		self.size_group.add_widget(label)
		control = gtk.Label()
		box.pack_start(label, False, False)
		box.pack_start(control, True, True)
		self.vbox.pack_start(box, False, False)
		self.controls[ID] = control
		return control

	def set_value(self, ID, value):
		v = unpack_unsigned(value)
		text = "$%04X=%r=%r" % (v, v, to_signed_byte(value) if ID != "PC" else value)
		self.controls[ID].set_text(text)

class Controls(gtk.VBox):
	def __init__(self, c64):
		gtk.VBox.__init__(self)
		self.C64 = c64
		self.status_dialog = None
		status_button = gtk.Button("_Status")
		status_button.connect("clicked", self.show_status)
		pause_button = gtk.Button("_Pause")
		pause_button.connect("clicked", self.pause_CPU)
		read_memory_button = gtk.Button("_Read Memory...")
		read_memory_button.connect("clicked", self.dump_memory)
		self.pack_start(status_button, False)
		self.pack_start(pause_button, False)
		self.pack_start(read_memory_button, False)
		self.show_all()

	def show_status(self, *args, **kwargs):
		toplevel_widget = self.get_toplevel()
		if self.status_dialog is None:
			self.status_dialog = StatusDialog(parent = toplevel_widget)
			def unset_status_dialog(*args, **kwargs):
				self.status_dialog = None
			self.status_dialog.set_transient_for(toplevel_widget)
			self.status_dialog.connect("delete-event", unset_status_dialog)
			self.status_dialog.show_all()
			gobject.timeout_add(50, self.update_status) # FIXME don't do that too often.

		self.update_status()

	def pause_CPU(self, widget, *args, **kwargs):
		# FIXME abstract that properly.
		C64 = self.C64
		if C64.CPU_clock:
			gobject.source_remove(C64.CPU_clock)
			widget.set_label("_Continue")
			C64.CPU_clock = None
		else:
			C64.CPU_clock = gobject.timeout_add(10, C64.iterate)
			widget.set_label("_Pause")

	def dump_memory(self, *args, **kwargs):
		MMU = self.C64.CPU.MMU
		address = 0x300
		sys.stdout.write("(%04X) " % address)
		for c in MMU.read_memory(address, 10):
			v = (c)
			sys.stdout.write("%02X " % v)
		sys.stdout.write("\n")

	def update_status(self):
		C64 = self.C64
		for register in ["A", "X", "Y", "SP", "PC"]:
			self.status_dialog.set_value(register, C64.CPU.read_register(register))
		return True

	def handle_key_press(self, keycode):
		n = gtk.gdk.keyval_name(keycode)
		#if len(n) == 1:
		#	n = keycode
		return self.C64.CIA1.handle_key_press(n)

	def handle_key_release(self, keycode):
		n = gtk.gdk.keyval_name(keycode)
		#if len(n) == 1:
		#	n = keycode
		return self.C64.CIA1.handle_key_release(n)
