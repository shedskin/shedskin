#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

#import gobject

class Timer(object):
	def fire_timer(self):
		return True

def timeout_add(timeout_ms, obj):
	pass # FIXME return gobject.timeout_add(timeout_ms, fn)
	return 42

def timeout_remove(ID):
	pass # FIXME
	#return gobject.source_remove(ID)
