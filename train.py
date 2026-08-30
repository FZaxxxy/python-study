def remove_all(n,L):
    for i in L:
        if i==n:
            L.remove(i)
    return L
L=[1,2,3]
n=input("请输入一个整数:")
n=int(n)
remove_all(n,L)
print(L)






