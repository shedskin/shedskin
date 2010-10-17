#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import gobject

class Timer(object):
	def fire_timer(self):
		return True

def timeout_add(timeout_ms, obj):
	return gobject.timeout_add(timeout_ms, obj.fire_timer)

def timeout_remove(ID):
	return gobject.source_remove(ID)
