# name clash
debug = True

class Debug:
    def debug(self, msg):
        if debug:
            print msg

Debug().debug('debug')
