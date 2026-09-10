def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

def loop(n):
    i = 0
    total = 0
    while i < n:
        total = total + i * 2
        i = i + 1
    return total

def greet(name, times):
    s = ''
    while times > 0:
        s = s + 'hello ' + name + '! '
        times = times - 1
    return s

print(fib(20))
print(loop(300000))
print(greet('world', 3))
