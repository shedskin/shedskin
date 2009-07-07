import pp, sys, random
import go

NPROCESSES = int(sys.argv[1])

job_server = pp.Server()
job_server.set_ncpus(NPROCESSES)

def go_job(history, i, n):
    import go
    return go.pgo(history, i, n)

def versus_cpu():
    board = go.Board()
    while True:
        if board.lastmove != go.PASS:
            print board.__repr__()
        pos = board.random_move()
        if pos == go.PASS:
            print 'I pass.'
        else:
            print 'thinking..'

            jobs = []
            for i in range(NPROCESSES):
                jobs.append(job_server.submit(go_job, (board.history, i, NPROCESSES)))

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
