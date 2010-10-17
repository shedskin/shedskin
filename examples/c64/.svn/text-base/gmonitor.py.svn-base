#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

# ShedSkin stub

class Controls(object):
	def __init__(self, C64):
		self.C64 = C64

	def handle_key_press(self, keycode):
		#n = gtk.gdk.keyval_name(keycode)
		#if len(n) == 1:
		n = keycode
		return self.C64.CIA1.handle_key_press(n)

	def handle_key_release(self, keycode):
		#n = gtk.gdk.keyval_name(keycode)
		#if len(n) == 1:
		n = keycode
		return self.C64.CIA1.handle_key_release(n)
