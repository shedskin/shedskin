import os

class GetoptError(Exception):
    def __init__(self, msg, opt=''):
        self.msg = msg
        self.opt = opt

class error(GetoptError):
    pass

def getopt(args, shortopts, longopts = []):
    return ([('',)], [''])

def gnu_getopt(args, shortopts, longopts = []):
    return ([('',)], [''])

def do_longs(opts, opt, longopts, args):
    return ([('',)], [''])

def long_has_args(opt, longopts):
    return True, ''

def do_shorts(opts, optstring, shortopts, args):
    return ([('',)], [''])

def short_has_arg(opt, shortopts):
    return True
