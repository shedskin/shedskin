class C:
    async def m(self, x):
        async for i in x:
            pass
        async with x as y:
            pass
        return await x

print('x')

#*ERROR* 69.py:2: 'async def' is not supported
