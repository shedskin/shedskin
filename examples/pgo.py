import pp, sys, random
import go

MAXPROCESSES = int(sys.argv[1])

job_server = pp.Server()
job_server.set_ncpus(MAXPROCESSES)

def go_job(history, options):
    import go
    return go.pgo(history, options)

def versus_cpu():
    board = go.Board()
    while True:
        if board.lastmove != go.PASS:
            print board.__repr__()
        options = [pos for pos in board.empties if board.legal_move(pos) and board.useful_move(pos)]
        if not options:
            print 'I pass.'
            pos = go.PASS
        else:
            nprocesses = min(MAXPROCESSES, (len(options)/8)+1)
            print 'thinking.. (%d)' % nprocesses
            jobs = []
            for i in range(nprocesses):
                jobs.append(job_server.submit(go_job, (board.history, options[i::nprocesses])))
            result = [job() for job in jobs]
            pos, score = max(result, key=lambda x: x[1])
            print 'I move here:', go.to_xy(pos) 

        board.play_move(pos)
        if board.finished:
            break
        if board.lastmove != go.PASS:
            print board.__repr__()
        pos = go.user_move(board)
        board.play_move(pos)
        if board.finished:
            break

    print 'WHITE:', board.score(go.WHITE)
    print 'BLACK:', board.score(go.BLACK)

if __name__ == '__main__':
    random.seed(1)
    try:
        versus_cpu()
    except EOFError:
        pass
