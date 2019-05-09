import timeit

mycode = '''
m1 = Matrix([[1,2,3,4,5],[5,4,3,4,5]])
m2 = Matrix([[3,2,4],[3,2,4],[3,2,4],[3,2,4],[3,2,4]])
m3 = Matrix.mul(m1,m2)
'''

mysetup = 'from mod1 import Matrix'
cy = timeit.timeit(
    setup=mysetup,
    stmt=mycode,
    number=1000
)
mycode = '''
m1 = Matrix([[1,2,3,4,5],[5,4,3,4,5]])
m2 = Matrix([[3,2,4],[3,2,4],[3,2,4],[3,2,4],[3,2,4]])
m3 = m1*m2
'''
mysetup = 'from mod1py import Matrix'
py = timeit.timeit(
    setup=mysetup,
    stmt=mycode,
    number=1000
)

print(cy,py)
print(f'Cython is {py/cy}x faster')