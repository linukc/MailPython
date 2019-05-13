from libc.stdlib cimport malloc

cdef class Matrix:

    cdef double ** mas
    cdef int row_size, column_size

    def __init__(self, data):
        cdef int i,j
        cdef int r = len(data)
        cdef int c = len(data[0])
        self.row_size = r
        self.column_size = c

        self.mas = <double**> malloc(sizeof(double*)*r)
        if not self.mas:
            raise MemoryError()

        for i in range(r):
            self.mas[i] = <double*> malloc(sizeof(double)*c)
            if not self.mas[i]:
                raise MemoryError()
            for j in range(c):
                self.mas[i][j] = data[i][j]

    def __repr__(self):
        cdef int r = self.row_size
        cdef int c = self.column_size
        cdef int i, j
        text = ""
        q = ""
        output = []
        for i in range(r):
            text = text + "| "
            for j in range(c):
                output.append(str(self.mas[i][j]))
            q = ' '.join(output)
            text = text + q + '|\n'
            q = ""
            output = []

        return f"Matrix {self.row_size}x{self.column_size}:\n{text}"

    def __add__(Matrix self, Matrix other):
        cdef int i,j
        cdef int r = self.row_size
        cdef int c = self.column_size
        cdef int r2 = other.row_size
        cdef int c2 = other.column_size
        if r!=r2 or c!=c2:
            raise ValueError

        cdef double** itog = <double**> malloc(sizeof(double*)*r)
        if not itog:
            raise MemoryError()

        for i in range(r):
            itog[i] = <double*> malloc(sizeof(double) * c)
            if not itog[i]:
                raise MemoryError()
            for j in range(c):
                itog[i][j] = self.mas[i][j] + other.mas[i][j]

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper


    def __mul__(Matrix self, Matrix other):
        cdef int i,j,k
        cdef double res
        cdef int r = self.row_size
        cdef int c2 = other.column_size
        cdef int r2 = other.row_size
        cdef int c1 = self.column_size
        if c1!=r2:
            raise ValueError

        cdef double** itog = <double**> malloc(sizeof(double*)*r)
        if not itog:
            raise MemoryError()

        for i in range(r):
            itog[i] = <double*> malloc(sizeof(double) * c2)
            if not itog[i]:
                raise MemoryError()
            for j in range(c2):
                res = 0
                for k in range(c1):
                    res = res + self.mas[i][k] * other.mas[k][j]
                itog[i][j] = res

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c2
        return wrapper


    def mul_by_number(Matrix self, int number):
        cdef int i, j
        cdef int r = self.row_size
        cdef int c = self.column_size
        cdef double ** itog = <double**> malloc(sizeof(double*) * r)
        if not itog:
            raise MemoryError()

        for i in range(r):
            itog[i] = < double * > malloc(sizeof(double) * c)
            if not itog[i]:
                raise MemoryError()
            for j in range(c):
                itog[i][j] = self.mas[i][j]*number

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper


    def div_by_number(Matrix self, int number):
        if number == 0:
            raise ZeroDivisionError()

        cdef int i, j
        cdef int r = self.row_size
        cdef int c = self.column_size
        cdef double ** itog = <double**> malloc(sizeof(double*) * r)
        if not itog:
            raise MemoryError()

        for i in range(r):
            itog[i] = < double * > malloc(sizeof(double) * c)
            if not itog[i]:
                raise MemoryError()
            for j in range(c):
                itog[i][j] = self.mas[i][j] / number

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper


    def transpose(Matrix self):
        cdef int i, j
        cdef int c = self.row_size
        cdef int r = self.column_size
        cdef double ** itog = <double**> malloc(sizeof(double*) * r)
        if not itog:
            raise MemoryError()

        for i in range(r):
            itog[i] = <double*> malloc(sizeof(double) * c)
            if not itog[i]:
                raise MemoryError()
            for j in range(c):
                itog[i][j] = self.mas[j][i]

        cdef Matrix wrapper = Matrix.__new__(Matrix)
        wrapper.mas = itog
        wrapper.row_size = r
        wrapper.column_size = c
        return wrapper

    def __contains__(Matrix self, int number):
        cdef int i,j
        cdef int r = self.row_size
        cdef int c = self.column_size

        for i in range(r):
            for j in range(c):
                if self.mas[i][j] == number:
                    return True
        return False


    def __getitem__(Matrix self, tuple coordinates):
        cdef int x = coordinates[0]
        cdef int y = coordinates[1]
        if (x < self.row_size) and (y < self.column_size):
            return self.mas[x][y]









