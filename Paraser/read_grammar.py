# -*- coding:utf-8 -*-
from Paraser.production_tools import *

T = {}
N = {}
pros = {}
def check(line,region):
	"""
	region  终结符/非终结描述符区域 | 产生式描述区域
	终结符/非终结描述符区域		<% [termi|non-terminal] %>
	产生式描述区域				<% [non-terminal[-->]{termi|non-terminal}%>
	此函数，判断改行是否符合region区域的规则
	若符合，则返回改行
	否则，退出程序
	"""
	global N,T
	line = line.replace(' ','')
	#是否以 <% 开头 并以 %>结尾
	if len(line) < 5 or line[0:2] != '<%' or line[-2:] != '%>':
		exit('Bad Grammar Description-'+line+'- <<')

	#产生式左部是否为 N--> , 右部符号是否在符号表 T+V中
	elif region == 'RULE':
		if len(line) < 9 or line[2] not in N.keys() or line[3:6] != '-->':
			exit('Bad Grammar Description '+line+' in '+region)
		
		for rs in line[6:-2].split('|'):
			for symbol in rs.split(','):
				if symbol not in list(N.keys())+list(T.keys()):
					exit('Bad Grammar Description '+line+' in '+region+' for undefined symbol:"'+symbol+'"')

def strip(line):
	"""
	去除空白符
	"""
	line = line.replace('\t','')
	line = line.replace('\n','')
	line = line.replace(' ','')
	return line

def readGrammar(path,mode='r',encoding='UTF-8'):
	"""
	读取描述文件内容,该文件按非结符声明区域，非终结符声明区域，产生式声明区域
	(1)如下描述排列,不允许出现空行, t : 终结符， n : 非终结符
	规定S为起始符,#为结束标志
	<T
		{<% [t] %>}
		
	T>
	<N
		{<% [n] %>}
	N>
	<rules
		{<% n-->{t|n[,{t|n}]}{'|'t|n[,{t|n}]}%>}
	rules>
	
	(2)返回数据T，N，productions
	T : {'name':Terminal}
	N : {'name':NonTerminal}
	productions: {'name':[rule[,...]]}
	"""
	script = open(path,mode=mode,encoding=encoding)
	global N,T,pros
	
	#识别终结符
	for line in script:
		line = strip(line)
		if line == '<T':
			break
	for line in script:
		line = strip(line)
		if line == 'T>':
			break
		check(line,'SYMBOL')
		
		T[line[2:-2]] = Terminal(line[2:-2])
	#识别非终结符
	for line in script:
		line = strip(line)
		if line == '<N':
			break
	for line in script:
		line = strip(line)
		
		if line == 'N>':
			break
		check(line,'SYMBOL')
		start = True if line[2] == 'S' else False
		N[line[2]] = NonTerminal(line[2],start)
		pros[line[2]] = []
	#识别产生式
	for line in script:
		line = strip(line)
		if line == '<rules':
			break
	for line in script:
		line = strip(line)
		if line == 'rules>':
			break
		check(line,'RULE')
		rights = []
		for rs in line[6:-2].split('|'):
			for symbol in rs.split(','):
				try:
					rights.append(T[symbol])
				except KeyError:
					rights.append(N[symbol])
			pros[line[2]].append(Production(N[line[2]], rights))
			rights = []
			
		
	script.close()
	return T,N,pros

if __name__ == '__main__':
	ts,ns,ps=readGrammar('g.gram')
	for i in ts.values():
		print('type:',type(i),i)
	for i in ns.values():
		print('type:',type(i),i)
	for i in ps:
		print('type:',type(i),i)
	print(pros)
	for s,rs in ps.items():
		for r in rs:
			right = r.getRightPartInString()
			print(s,right[::-1])
			for i in right:
				print(i,type(i))
	
	