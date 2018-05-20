from Grammar_Tools.production_tools import *
from Grammar_Tools.read_grammar import *
import copy
class PreAnalyTable():
	def __init__(self,path):
		self.T = {}
		self.N = {}
		self.pros = {}
		self.table = {}
		self.loadGrammar(path)

	def hasTerminal(self,symbols):
		for i in symbols:
			if i.getType() == i.TERMINAL:
				return True
		return False
		
	def deduceToNone(self):
		productions = copy.deepcopy(self.pros)
		ε_table = {}
		for s in self.N.keys():
			ε_table[s] = 'uncertain'
		for s in self.T.keys():
			ε_table[s] = False
		ε_table['ε'] = True
		for key,pro_of_T in productions.items():
			back = copy.deepcopy(pro_of_T)
			for pro in pro_of_T:
				right = pro.getRightPart()
				if right == [self.T['ε']]:
					ε_table[pro.left.name] = True
					back = []
					break
				if self.hasTerminal(right):
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
		
	def next_symbol(self,symbols):
		try:
			return next(symbols)
		except StopIteration:
			return self.T['ε']

	def mergeSet(self,des,src):
		
		for i in src:
			des.add(i)

	def first(self,symbol):
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
		for pro in self.pros[symbol.name]:
			#(2)
			if pro.getRightPart() == [self.T['ε']]:
				firsts.add(self.T['ε'].name)
			#(3)
			else:
				for s in pro.getRightPart():
					t = self.first(s)
					self.mergeSet(firsts,t)
					if self.T['ε'] not in t:
						break
		return firsts
		


	def follow(self,symbol):
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
		ε_table = self.deduceToNone()
		#pros: {NonTerminal:[rules]......}
		
		#遍历每一个非终结符对应的产生式,例如 {'E': [(1) E--> + T E, (2) E--> ε],key1:value1,......}
		#则pro_of_T 一次为各个非终结符对应的产生式列表
		for pro_of_T in self.pros.values():
			for pro in pro_of_T:
				#获取产生式的右部,getRightPart()返回值为列表,不可做next()的参数
				right = pro.iterableRight()
				#定位symbol后面的符号next_s,并根据(1)(2)求follow集
				for s in right:
					if s == symbol:
						next_s = self.next_symbol(right)
						#(1)
						self.mergeSet(follows,self.first(next_s)-{self.T['ε']})
						
						#(2) 下一个符号是ε或者可以推导至ε,
						#并且本条产生是左部非当前所follow集合求的symbol
						if (next_s.isEpsilon() or (not next_s.isTerminal()) and ε_table[next_s.name] is True)\
							and \
							pro.getLeftPart() != s:
							self.mergeSet(follows,self.follow(pro.getLeftPart()))
		
		if symbol.isStart():
			follows.add(self.T['#'].name)
		return follows
						
	def select(self,pro):
		"""
		pro: A-->α
		返回一个set,其元素为符号名,字符串类型
		(1)若α -*/-> ε, 则select(A-->α)=First(α) 
		(2)若α -*-> ε,  则select(A-->α)=First(α)-{ε} ∪ Follow(A) 
		(3)select集不含ε
		
		"""
		ε_table = self.deduceToNone()
		right = pro.getRightPart()
		right_to_none = True
		selects = set()
		for s in right:
			if ε_table[s.name] is False:
				right_to_none = False
				break
		
		for s in right:
			t = self.first(s)
			self.mergeSet(selects,t)
			if self.T['ε'] not in t:
				break
		selects = selects - {self.T['ε'].name}
		if right_to_none is True:
			self.mergeSet(selects,self.follow(pro.getLeftPart()))
		
		return selects

	def loadGrammar(self,path):
		reader = GrammarReader()
		self.T,self.N,self.pros = reader.readGrammar(path)
		for non_ter_symbol in self.N:
			self.table[non_ter_symbol] = {}
			for ter_symbol in self.T:
				self.table[non_ter_symbol][ter_symbol] = None
		
	def getTable(self):
		"""
		pro: left-->[symbols]
		selects = [names of Terminal] ,select(pro)
		firsts = [name of Terminal]	  ,first(symbol)
		follows = [name of Terminal]  ,follow(symbol)
		"""

		select_of_pro = set()
		for non_ter_symbol,pro_of_T in self.pros.items():
			for pro in pro_of_T:
				select_of_pro = self.select(pro)
				right = pro.getRightPartInString()
				for ter_symbol in select_of_pro:
					self.table[non_ter_symbol][ter_symbol] = right[::-1]
		return self.table

	def getSymbols(self):
		return self.T,self.N

	def getProductions(self):
		return self.pros
if __name__ == '__main__':
	table = PreAnalyTable('g.gram')
	pre = table.getTable()
	print(table.N)
	print(table.T)
	
	print()
	print('first ',table.N['S'],':',table.first(table.N['S']))
	print('first ',table.N['E'],':',table.first(table.N['E']))
	print('first ',table.N['T'],':',table.first(table.N['T']))
	print('first ',table.N['X'],':',table.first(table.N['X']))
	print('first ',table.N['F'],':',table.first(table.N['F']))
	print(table.deduceToNone())
	print(table.pros)
	print('follow ',table.N['S'],':',table.follow(table.N['S']))
	print('follow ',table.N['E'],':',table.follow(table.N['E']))
	print('follow ',table.N['T'],':',table.follow(table.N['T']))
	print('follow ',table.N['X'],':',table.follow(table.N['X']))
	print('follow ',table.N['F'],':',table.follow(table.N['F']))
	print()
	for pro_of_T in table.pros.values():
		for pro in pro_of_T:
			print('select ',pro,':',table.select(pro))
	print()
	
	end = '|'
	
	for non_ter_symbol, ter_and_rule in pre.items():
		print(non_ter_symbol,ter_and_rule)
	
	