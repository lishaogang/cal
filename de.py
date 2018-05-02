class BaseClass():
	def __init__(self, name, value, type):
		self.name = name
		self.value = value
		self.type = type
	
	def derivate(self,partial):
		pass
	
	def expression(self):
		pass

G_STATIC_COUNT = 0		

class Constant(BaseClass):
	def __init__(self,value):
		global G_STATIC_COUNT
		G_STATIC_COUNT += 1
		self.value = value
		self.name = 'CONST_' + str(G_STATIC_COUNT)
		self.type = 'CONSTANT'
	
	def derivate(self,partial):
		return Constant(0)
		
	def expression(self):
		return str(self.value)
		
class Variable(BaseClass):
	def __init__(self, name, coefficient = 1, value = None):
		self.name = name
		self.value = value
		self.coefficient = Constant(coefficient)
		self.type = 'VARIABLE'
		
	def derivate(self,partial):
		if partial.name == self.name:
			return self.coefficient
		return Constant(0)
	
	def expression(self):
		return '('+str(self.coefficient.expression())+'*'+str(self.name)+')'
		
		
def GExpressionWrapper(left, right, opType):
	#do some preparation here
	return GExpression(left,right,opType)
		
class GExpression(BaseClass):
	def __init__(self, a, b, opType):
		self.left = a
		self.right = b
		self.opType = opType
		self.type = 'EXPRESSION'
	
	def derivate(self, partial):
		if partial.type != 'VARIABLE':
			print('Error')
			return None
		if self.opType == 'plus' or self.opType == 'minus':
			return GExpressionWrapper(self.left.derivate(partial),
					self.right.derivate(partial), self.opType)
		
		if self.opType == 'multiple':
			return GExpressionWrapper(GExpressionWrapper(self.left,self.right.derivate(partial),'multiple'),
									GExpressionWrapper(self.right,self.left.derivate(partial),'multiple'),
									'plus')
		if self.opType == 'divide':
			vdu = GExpressionWrapper(self.right, self.left.derivate(partial),'multiple')
			udv = GExpressionWrapper(self.left, self.right.derivate(partial),'multiple')
			vv = GExpressionWrapper(self.right,Constant(2),'^')
			return GExpressionWrapper(GExpressionWrapper(vdu,udv,'minus'),vv,'divide')
		
		#ln(E) left operator is e, right operator is E, opType is ln
		if self.opType == 'ln':
			return GExpressionWrapper(self.right.derivate(partial),self.left,'divide')
		#loga(E) left operator is a, right operator is E, opType is log	
		if self.opType == 'log':
			return GExpressionWrapper(self.right.derivate(partial),
									GExpressionWrapper(self.right,
														GExpressionWrapper(Constant('e'),self.left,'ln'),
														'multiple'),
									'divide')
			
		
		if self.opType == '^':
			#y = u^a, assume a is  constant
			if self.left.type == 'VARIABLE' and self.right.type == 'CONSTANT':
				du = self.left.derivate(partial)
				udu = GExpressionWrapper(du,self.left,'multiple')
				base = GExpressionWrapper(Constant(self.right.value),udu,'multiple')
				return GExpressionWrapper(base,Constant(self.right.value-1),'^')
			
			#y = a^u, assume a is constant
			if self.left.type == 'CONSTANT' and self.right.type == 'VARIABLE':
				du = self.right.derivate(partial)
				ydu = GExpressionWrapper(du,self,'multiple')
				return GExpressionWrapper(GExpressionWrapper(Constant('e'),self.left,'ln'),ydu,'multiple')
														
					
	def expression(self):
		#date: 18-4-27 21:11
		#memo: expression with too much redundant brackets which needs to be fixed
		#		this maybe should be done in a independent moduel 
		l = self.left.expression() if self.left.type != 'EXPRESSION' else '(' +self.left.expression() + ')'
		r = self.right.expression() if self.right.type != 'EXPRESSION' else '(' +self.right.expression() + ')'
		
		if self.opType == 'plus':
			return '('+ l + '+' + r +')'
		if self.opType == 'minus':
			return '('+ l + '-' + r +')'
		if self.opType == 'multiple':
			return '('+l + '*' + r +')'
		if self.opType == 'divide':
			return '('+ l+ '/'+ r +')'
		if self.opType == '^':
			return '('+ l + '^' + r +')'
		if self.opType == 'ln':
			return 'ln' + r
		if self.opType == 'log':
			return 'log' + self.right.expression() + l
			
	def type(self):
		return 'OPERATION'
		
if __name__ == '__main__':
	
	a = Constant('e')
	x = Variable('X',2)
	x1 = Variable('X',3)
	apx = GExpressionWrapper(a,x,'plus')
	amx = GExpressionWrapper(a,x,'minus')
	x1dx = GExpressionWrapper(x1,x,'divide')
	xp2 = GExpressionWrapper(x,a,'^')
	apx = GExpressionWrapper(a,x,'^')
	
	dominator = GExpressionWrapper(Constant(1),GExpressionWrapper(Constant('e'),Variable('X',-1),'^'),'minus')
	
	#print(apx.derivate(x).expression())
	
	#print(apx.derivate(x).expression())
	#print(amx.derivate(x).expression())
	#print(x1dx.derivate(x).expression())
	#print(xp2.derivate(x).expression())
	
		

	dominator = GExpressionWrapper(Constant(1),
                                        GExpressionWrapper(Constant('e'),
                                                            Variable('X',-1),
                                                            '^'),
                                        'plus')
	
	numerator = Constant(1)
        
	sigmoid = GExpressionWrapper(numerator, dominator, 'divide')
        
    #sigmoid(x) = 1/(1+e^(-x))
	#sigmoid(x)dx = (e^(-x))/(1+e^(-x))^2
	
	print(sigmoid.derivate(x).expression())






