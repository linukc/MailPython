class Matrix(object):
    def __init__(self, matrix):
        self.matrix = matrix

    def __mul__(self, other):
        res = 0
        itog = []
        itog_all = []

        for i in range(len(self.matrix)):
            itog = []
            res = 0
            for j in range(len(other.matrix[0])):
                for k in range(len(self.matrix[0])):
                    res = res + self.matrix[i][k]*other.matrix[k][j]
                itog.append(res)
                res = 0
            itog_all.append(itog)

        return Matrix(itog_all)

    def __str__(self):
        r = len(self.matrix)
        c = len(self.matrix[0])
        text = ""
        for i in range(r):
            text = text + "| "
            for j in range(c):
                text = text + str(self.matrix[i][j]) + " "
            text = text + '|\n'
        return text

