#the lexer turn  CHARACTER STREAM into WORD STREAM
#the valid input of characters are divided into such 3 types:
#	1. alphabet
#	2. number
#	3. symbol

class Lexer():
	def __init__(self, input=None):
		self.input = input
		self.length = len(input) if input is not None else 0
		self.p = -1
	def setInput(self,input):
		self.input = input
		self.length = len(input) if input is not None else 0
		self.p = -1
	
	def nextChar(self):
		self.p += 1
		return self.input[self.p] if self.p < self.length else None
	
	def back(self):
		self.p -= 1
		
	def next(self):
		c = self.nextChar();
		while c == ' ':
			c = self.nextChar()
		if c is None:
			print(self.input,self.p)
			return None
			
		if c.isdigit() or c == 'e':
			return self.digit(c)
		
		if c.isalpha():
			return self.variableOrFunction(c)
		
		
		return self.operator(c)
		
	def variableOrFunction(self,s):
		c = self.nextChar()
		if c is not None and c.isalpha():
			return self.function(s+c)
		self.back()
		return self.variable(s)
	
	def function(self,s):
		c = self.nextChar()
		while c is not None and c.isalpha():
			s += c
			c = self.nextChar()
		self.back()
		return {'type':'FUNCTION','value':s}

		
	def variable(self,s):
		c = self.nextChar()
		while c is not None and c.isdigit():
			s += c
			c = self.nextChar()
		self.back()
		return {'type':'VARIABLE','value':s}
		
	def digit(self,s):
		if s == 'e':
			return {'type':'CONSTANT','value':s}
		c = self.nextChar()
		while c is not None and c.isdigit():
			s += c
			c = self.nextChar()
		self.back()
		return {'type':'CONSTANT','value':s}
		
	def operator(self,s):
		return {'type':'OPERATOR','value':s}
		
if __name__ == '__main__':
		s = '2x+3*4+e^22.2'
		s1 = 'x^2+e^x+3/4+2.22+x^(e^x)'
		s2 = 'xxxxx+sin n+3 + log( a ) / e^x'
		input = 'i+i#'
		l = Lexer(input)
		c = l.next()
		while c is not None:
			print(c)
			c = l.next()
	