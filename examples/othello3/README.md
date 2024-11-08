# othello3

advanced othello move generator.

note that building may take a long time (an hour on my system):

```
shedskin build --nobounds --nowrap othello3
build/othello3
```

to compare speed with bitboard implementation:

```
shedskin build --nobounds --nowrap --int64 ref
build/ref
```
