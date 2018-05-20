class BaseSymbol():
	"""
	终结符和非终结符的基类
	"""
	TERMINAL = 'TERMINAL'
	NON_TERMINAL = 'NON-TERMINAL'
	def __init__(self,name):
		"""
		(0)name, 该符号的名字 如非终结符S的名字为'S'
		(1)约定使用大写字母表示非终结符，小写字母表示终结符
		(2)约定符号的名字大小写和符号大小写一致
		"""
		self.name = name
		self.type = None
	
	def isTerminal(self):
		return self.type == self.TERMINAL
	def isEpsilon(self):
		return self.name == 'ε'
	
	def getType(self):
		"""
		返回:符号的类型，终结符 | 非终结符
		"""
		return self.type
		
	def __hash__(self):
		return hash((self.name,self.type))
	def __eq__(self,other):
		return self.type == other.type and self.name == other.name
		
	def __repr__(self):
		return self.name
	
		
class NonTerminal(BaseSymbol):
	def __init__(self,name,start = False):
		self.name = name
		self.type = BaseSymbol.NON_TERMINAL
		self.start = start
	def isStart(self):
		return self.start
	
class Terminal(BaseSymbol):
	def __init__(self,name):
		self.name = name
		self.type = BaseSymbol.TERMINAL
	

class Production():
	"""
	产生式，由左部与右部组成
	如 S-->aA
	(0)类变量 count 计数产生式数目
	(1)产生式结构： NonTerminal --> [Terminal|NonTerminal[,...]]
	"""
	count = 0
	def __init__(self,left, right = []):
		"""
		(0)产生式的左部为一个非终结符
		(1)右部为一个符号列表
		(2)每条产生式有一个编号，编号唯一，依次递增
		"""
		self.left = left
		self.right = right
		self.No = Production.count
		Production.count += 1

	def iterableRight(self):
		"""
		产生一个生成器，用以迭代产生式的右部
		"""
		for s in self.right:
			yield s
	
	def getLeftPart(self):
		return self.left
	
	def getRightPart(self):
		return self.right
	def getRightPartInString(self):
		right = []
		for i in self.right:
			right.append(i.name)
		return right
		
	def getNo(self):
		return self.No
	
	def __eq__(self,other):
		return self.left == other.left and self.right == other.right
	def __repr__(self):
		items = ''
		i = 0
		while i < len(self.right):
			items += ' '+self.right[i].name
			i += 1
		return '('+str(self.No)+') '+self.left.name+'-->'+items
	
	def toString(self):
		return self.__repr__()
		
	def print(self,prefix=''):
		items = ''
		i = 0
		while i < len(self.right):
			items += self.right[i].name+' '
			i += 1
		print('('+str(self.No)+')'+self.left.name,'-->',items)

class Chain():
	"""
	类链表，只能在末尾插入节点
	"""
	class Node():
		"""
		链的节点，由数据域 data 和指针域 next 组成
		"""
		def __init__(self, data,next = None):
			self.data = data
			self.next = next
		def __repr__(self):
			return self.data.__str__()
		
	def __init__(self,data):
		"""
		(0)head 头指针
		(1)tail 尾指针
		(2)初始化时插入一个数据域为data的节点
		"""
		self.head = self.Node(data)
		self.tail = self.head
	
	def append(self,data=None):
		"""
		在末尾插入数据域为data的节点
		"""
		p = self.head
		while p.next != None:
			p = p.next
		
		t = self.Node(data,p.next)
		p.next = t
		self.tail = t
		
	def next(self):
		"""
		产生一个生成器，用以迭代
		"""
		p = self.head
		while p != None:
			yield p
			p = p.next
		
	
	def print(self):
		p = self.head
		while p != None:
			print(p.data)
			p = p.next
		
		
if __name__ == '__main__':
	S = NonTerminal('S')
	A = NonTerminal('A')
	A1 = NonTerminal('A')
	a = Terminal('a')
	proS1 = Production(S,[a,A])
	p = Production(S,[a,A1])
	proS2 = Production(S,[a,S])
	proA = Production(A,[a])
	l1 = [S,A]
	l2 = [S,A]
	l3 = [S,A1]
	print(l1 == l3)
	print(p == proS1,p == proS2)
	print(A == A1)
	
	ps = Chain(proS1)
	ps.append(proS2)
	ps.append(proA)
	for i in proS1.nextInRight():
		print(i.getType(),i)
	for i in ps.next():
		print(i)
	