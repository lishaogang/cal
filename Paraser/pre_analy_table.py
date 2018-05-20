from Paraser.production_tools import *
from Paraser.read_grammar import *
import copy
import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

T = {}
N = {}
pros = {}

def hasTerminal(symbols):
	for i in symbols:
		if i.getType() == i.TERMINAL:
			return True
	return False
	
def deduceToNone():
	productions = copy.deepcopy(pros)
	ε_table = {}
	for s in N.keys():
		ε_table[s] = 'uncertain'
	for s in T.keys():
		ε_table[s] = False
	ε_table['ε'] = True
	for key,pro_of_T in productions.items():
		back = copy.deepcopy(pro_of_T)
		for pro in pro_of_T:
			right = pro.getRightPart()
			if right == [T['ε']]:
				ε_table[pro.left.name] = True
				back = []
				break
			if hasTerminal(right):
				back.remove(pro)
		productions[key] = back
		if back == [] and ε_table[pro.left.name] == 'uncertain':
			ε_table[pro.left.name] = False
		
	
	for key,pro_of_T in productions.items():
		
		#ε_table[pro.left.name]为False时,不会进入下一个for
		for pro in pro_of_T:
			right = pro.getRightPart()
			ε_table[pro.left.name] = True
			for s in right:
				if ε_table[s.name] is not True :
					ε_table[pro.left.name] = 'uncertain'
					break
			if ε_table[pro.left.name] is True:
				break
		if ε_table[pro.left.name] == 'uncertain':
			ε_table[pro.left.name] = False
		
			
	return ε_table
	
def next_symbol(symbols):
	try:
		return next(symbols)
	except StopIteration:
		return T['ε']

def mergeSet(self,other):
	
	for i in other:
		self.add(i)

def first(symbol):
	"""
	symbol 类型为Terminal | NonTerminal
	此函数计算symbol的first集,	返回一个set,其元素为符号名,字符串类型
	(1) 若 symbol为Terminal,则first(symbol) = {symbol}
	(2) 若 symbol -*-> ε, 则 ε ∈ first(symbol)
	(3) 若 symbol -*-> aβ, 则 a ∈ first(symbol)
	(4) '#' ∈ first(起始符)
	"""
	
	#(1)
	if symbol.getType() == symbol.TERMINAL:
		return set([symbol.name])
	firsts = set()
	for pro in pros[symbol.name]:
		#(2)
		if pro.getRightPart() == [T['ε']]:
			firsts.add(T['ε'].name)
		#(3)
		else:
			for s in pro.getRightPart():
				t = first(s)
				mergeSet(firsts,t)
				if T['ε'] not in t:
					break
	return firsts
	


def follow(symbol):
	"""
	symbol,类型为Terminal | NonTerminal
	此函数计算symbol的follow集,返回一个set,其元素为符号名,字符串类型
	(1)若 A-->αBβ,则first(β)-{ε}∈follow(B) B≠ε
	(2)当 β-*->ε , 则follow(A)∈follow(B)
	(3)ε 不属于 follow 集
	"""
	#终结符的follow集为自身,此处即是(2)处递归调用的边界
	if symbol.getType() == symbol.TERMINAL:
		return set([symbol.name])
	#结果
	follows = set()
	#可推出ε的非终结符表
	ε_table = deduceToNone()
	#pros: {NonTerminal:[rules]......}
	
	#遍历每一个非终结符对应的产生式,例如 {'E': [(1) E--> + T E, (2) E--> ε],key1:value1,......}
	#则pro_of_T 一次为各个非终结符对应的产生式列表
	for pro_of_T in pros.values():
		for pro in pro_of_T:
			#获取产生式的右部,getRightPart()返回值为列表,不可做next()的参数
			right = pro.iterableRight()
			#定位symbol后面的符号next_s,并根据(1)(2)求follow集
			for s in right:
				if s == symbol:
					next_s = next_symbol(right)
					#(1)
					mergeSet(follows,first(next_s)-{T['ε']})
					
					#(2) 下一个符号是ε或者可以推导至ε,
					#并且本条产生是左部非当前所follow集合求的symbol
					if (next_s.isEpsilon() or (not next_s.isTerminal()) and ε_table[next_s.name] is True)\
						and \
						pro.getLeftPart() != s:
						mergeSet(follows,follow(pro.getLeftPart()))
	
	if symbol.isStart():
		follows.add(T['#'].name)
	return follows
					
def select(pro):
	"""
	pro: A-->α
	返回一个set,其元素为符号名,字符串类型
	(1)若α -*/-> ε, 则select(A-->α)=First(α) 
	(2)若α -*-> ε,  则select(A-->α)=First(α)-{ε} ∪ Follow(A) 
	(3)select集不含ε
	
	"""
	ε_table = deduceToNone()
	right = pro.getRightPart()
	right_to_none = True
	selects = set()
	for s in right:
		if ε_table[s.name] is False:
			right_to_none = False
			break
	
	for s in right:
		t = first(s)
		mergeSet(selects,t)
		if T['ε'] not in t:
			break
	selects = selects - {T['ε'].name}
	if right_to_none is True:
		mergeSet(selects,follow(pro.getLeftPart()))
	
	return selects

def initTable(path):
	table = {}
	global T,N,pros
	T,N,pros= readGrammar(path)
	for non_ter_symbol in N:
		table[non_ter_symbol] = {}
		for ter_symbol in T:
			table[non_ter_symbol][ter_symbol] = None
	return table
	
def getTable(path):
	"""
	pro: left-->[symbols]
	selects = [names of Terminal] ,select(pro)
	firsts = [name of Terminal]	  ,first(symbol)
	follows = [name of Terminal]  ,follow(symbol)
	"""
	pre_analy_table = initTable(path)
	select_of_pro = set()
	for non_ter_symbol,pro_of_T in pros.items():
		for pro in pro_of_T:
			select_of_pro = select(pro)
			right = pro.getRightPartInString()
			for ter_symbol in select_of_pro:
				pre_analy_table[non_ter_symbol][ter_symbol] = right[::-1]
	return pre_analy_table

def getSymbols():
	return T,N

def getProductions():
	return pros
if __name__ == '__main__':
	pre = getTable('g.gram')
	print(N)
	print(T)
	
	print()
	print(N)
	print('first ',N['S'],':',first(N['S']))
	print('first ',N['E'],':',first(N['E']))
	print('first ',N['T'],':',first(N['T']))
	print('first ',N['X'],':',first(N['X']))
	print('first ',N['F'],':',first(N['F']))
	print(deduceToNone())
	print(pros)
	print('follow ',N['S'],':',follow(N['S']))
	print('follow ',N['E'],':',follow(N['E']))
	print('follow ',N['T'],':',follow(N['T']))
	print('follow ',N['X'],':',follow(N['X']))
	print('follow ',N['F'],':',follow(N['F']))
	print()
	for pro_of_T in pros.values():
		for pro in pro_of_T:
			print('select ',pro,':',select(pro))
	print()
	
	end = '|'
	
	for non_ter_symbol, ter_and_rule in pre.items():
		print(non_ter_symbol,ter_and_rule)
	
	