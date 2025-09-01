import threading

C = [1, 2, 3, 4]


def test_gl_1(A: list):
    for _ in range(len(A)):
        print(A.pop())


def test_gl_2(A: list):
    for _ in range(len(A)):
        print(A.pop())


t1 = threading.Thread(target=test_gl_1, args=(C,))
t2 = threading.Thread(target=test_gl_2, args=(C,))

while C != []:
    t1.start()
    t2.start()

    t1.join()
    t2.join()


