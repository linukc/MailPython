from libc.stdlib cimport malloc

cdef class Matrix:
    cdef double** mas
    cdef int row_size ,column_size

    def __init__(self, data):
        cdef int i,j
        cdef int r = len(data)
        cdef int c = len(data[0])
        self.row_size = r
        self.column_size = c

        self.mas = <double**> malloc(sizeof(double*)*r)
        for i in range(r):
            self.mas[i] = <double*> malloc(sizeof(double)*c)
            for j in range(c):
                self.mas[i][j] = data[i][j]


    def __str__(self):
        cdef int r = self.row_size
        cdef int c = self.column_size
        cdef int i,j
        text = ""
        for i in range(r):
            text = text + "| "
            for j in range(c):
                text = text + str(self.mas[i][j]) + " "
            text = text + '|\n'
        return text


    def __repr__(self):
        return f"Matrix {self.row_size}x{self.column_size}:\n{self.__str__()}"


    cpdef Matrix sum(Matrix m1, Matrix m2):
        cdef int i,j
        cdef int r = m1.row_size
        cdef int c = m1.column_size
        cdef double** itog = <double**> malloc(sizeof(double*)*r)

        for i in range(r):
            itog[i] = <double*> malloc(sizeof(double) * c)
            for j in range(c):
                itog[i][j] = m1.mas[i][j] + m2.mas[i][j]

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper


    cpdef Matrix mul(Matrix m1, Matrix m2):
        cdef int i,j,k
        cdef double res
        cdef int r = m1.row_size
        cdef int c = m2.column_size
        cdef int q = m1.column_size
        cdef double** itog = <double**> malloc(sizeof(double*)*r)

        for i in range(r):
            itog[i] = <double*> malloc(sizeof(double) * c)
            for j in range(c):
                res = 0
                for k in range(q):
                    res = res + m1.mas[i][k] * m2.mas[k][j]
                itog[i][j] = res

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper


    cpdef Matrix mul_by_number(Matrix m, int number):
        cdef int i, j
        cdef int r = m.row_size
        cdef int c = m.column_size
        cdef double ** itog = <double**> malloc(sizeof(double*) * r)

        for i in range(r):
            itog[i] = < double * > malloc(sizeof(double) * c)
            for j in range(c):
                itog[i][j] = m.mas[i][j]*number

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper


    cpdef Matrix div_by_number(Matrix m, int number):
        cdef int i, j
        cdef int r = m.row_size
        cdef int c = m.column_size
        cdef double ** itog = <double**> malloc(sizeof(double*) * r)

        for i in range(r):
            itog[i] = < double * > malloc(sizeof(double) * c)
            for j in range(c):
                itog[i][j] = m.mas[i][j] / number

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper


    cpdef Matrix transpose(Matrix m):
        cdef int i, j
        cdef int c = m.row_size
        cdef int r = m.column_size
        cdef double ** itog = <double**> malloc(sizeof(double*) * r)

        for i in range(r):
            itog[i] = <double*> malloc(sizeof(double) * c)
            for j in range(c):
                itog[i][j] = m.mas[j][i]

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper

    def have(Matrix m, int number):
        cdef int i,j
        cdef int r = m.row_size
        cdef int c = m.column_size

        for i in range(r):
            for j in range(c):
                if m.mas[i][j] == number:
                    return True


    def get(Matrix m, tuple coordinates):
        cdef int x = coordinates[0]
        cdef int y = coordinates[1]
        if (x < m.row_size) and (y < m.column_size):
            return m.mas[x][y]










