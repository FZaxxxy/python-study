'''
    python study
特殊变量类型:NoneType只有唯一值None
查询类型函数:type()
bool类型中True和Flase首字母必须大写
类型转换:int(),float()直接截断小数位不是四舍五入
round()四舍五入输出int型
//表示除后向下取整，**表示幂
在运算过程中只要出现一个浮点数，其结果一定也是浮点数
len()获取字符串长度
python中字符串下标为负合法,arr[-1]等价于arr[len(arr)-1]
但如果这个负数超过了该字符串的长度就会报错
获取子字符串s1=s[a:b:c],a代表起始下标,b代表终止下标,c代表步长(不加则默认1),区间为左闭右开
arr[::-1]表示字符串反转,同样的可以设置反转的步长类似arr[4:1:-2]
不能通过s[0]这样直接更改字符串的元素
输出函数print()输出完后自动换行
eg: 有a,b,c三个变量,print(a,b,c)表示的意思是输出这三个变量中间存在空格
如果不要空格print(a+b+c),但必须要求a,b,c都是string类型
强制类型转换str(a)转换为string类型
输入函数s=input("打印在shell中的文字"),此时在shell输入,enter键截断,
并将输入的值以string类型赋给s
print(f'{a*b} is a*b')叫做fprint,''内的内容显示什么输出什么 (即一定为string类型),{}内的内容则先按其类型计算后再输出类型值
not即为否,not(2<3)返回值为False
A or B,当A和B均为False返回False,否则返回True
A and B,当A和B均为True返回True,否则返回False
if else 通过后续代码行的缩进来明确是否在同一模块
if下的else写作elif
range(6)表示依次从0到5
同样有range(start,stop,step)区间左闭右开
eg:for n in range(5):
   for ch in s:此处s为一个字符串
in关键字,if(ch in 'iu')判断ch是不是iu的子串
用关键字def来定义函数
eg: def func(a,b):
    return a+b
函数的参数可以有默认值,eg:def func(a,b=1):
无return返回None,有return返回return后面的值
lambda函数,eg:func=lambda a,b:a+b(2,3)返回5
lambda函数可以作为参数传入其他函数,eg:func1(func2)
eg:def do_twice(n,fn):
    return fn(fn(n))
do_twice(3,lambda x:x+1)返回5
tuples元组,eg:tuple=(1,2,3),tuple[0]返回1,tuple[0]=5报错
元组内可有任意类型元素,包括元组,eg:tuple=(1,2,(3,4)),tuple[2][0]返回3
tuples[0:2]返回(1,2),tuples[0:2:2]返回(1,)左闭右开
单元素元组必须加逗号,eg:tuple=(1,)
List列表,eg:list=[1,2,3],list[0]=5,此时list变为[5,2,3]
和tuple不同,列表内的元素可以被修改,eg:list[0]=5
列表的函数有append()在列表末尾添加元素,eg:list.append(4),list变为[1,2,3,4]
注意每次append只能添加1个元素
Lnew=L[:]表示将L的所有元素赋给Lnew,此时Lnew和L是两个不同的列表,修改L不会影响Lnew
Lnew=L表示将L的所有元素赋给Lnew,此时Lnew和L是同一个列表,修改L会影响Lnew
eg: L=[1,2,3],Lnew=L,L.append(4),此时Lnew也变为[1,2,3,4]
L.clear()清空列表,eg:L.clear(),此时L变为[]
L.pop()删除列表末尾元素,eg:L.pop(),此时L变为[1,2],还会返回被删除的元素3
L.pop(0)删除列表第一个元素,eg:L.pop(0),此时L变为[2,3]
del L[0]删除列表第一个元素,eg:del L[0],此时L变为[2,3]
L.remove(2)删除列表中第一个值为2的元素,eg:L.remove(2),此时L变为[1,3]
list comprehension列表生成式,eg:[x**2 for x in range(5)]返回[0,1,4,9,16]
条件附加在for后面,eg:[x**2 for x in range(5) if x%2==0]返回[0,4,16]
list comprehension内可以写任何可以遍历的对象,eg:[x**2 for x in 'hello']返回[0,1,4,9,16]
字符串里为数字,每位数字占一个字符
函数中的default参数,def func(a,b=1)中b为default参数,调用func(2)时,b的值为1,调用func(2,3)时,b的值为3
默认参数必须放在非默认参数的后面,eg:def func(a=1,b)会报错
在调用函数可以使用关键字参数,eg:func(b=3,a=2)返回5
异常处理:try和except,作用类似于if和else,如果在try下出现异常会执行except语句
通过对异常状况的分类可以实现执行不同的except语句
try也可以与else和finally配合使用,只有try中语句正常时才执行else,无论try是否执行finally都会执行
raise关键字抛出自定义错误,即在发生这种类型错误时输出自定义内容








'''
