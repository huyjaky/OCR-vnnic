import threading
A = [1,2,3,4]
def test_gl_1(A:list):
    for _ in range(len(A)):
        print(A.pop())

def test_gl_2(A:list):
    for _ in range(len(A)):
        print(A.pop())

t1 = threading.Thread(target=test_gl_1, args=(A,))
t2 = threading.Thread(target=test_gl_2, args=(A,))

while A != []:
    t1.start()
    t2.start()
    t1.join()
    t2.join()
