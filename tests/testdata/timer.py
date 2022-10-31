from __future__ import print_function

class TimingOut(object):
    def fire_timer(self):
        print('timer')
        return True

def timeout_add(timeout_ms, obj):
    return 42
