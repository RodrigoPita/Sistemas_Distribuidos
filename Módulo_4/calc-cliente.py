# Cliente de calculadora usando RPyC
import rpyc

calc = rpyc.connect('localhost', 10000)
print(calc.root.aux)
while True:
	op = input("Digite uma operacao(+,-,*,/, ou 'fim' para terminar):")
	if op == 'fim':
		calc.close()
		break
	arg1 = int(input("Arg 1:"))
	arg2 = int(input("Arg 2:"))
	if op == '+':
		soma = calc.root.soma(arg1, arg2)
		print(soma)
	elif op == '-':
		sub = calc.root.sub(arg1, arg2)
		print(sub)
	elif op == '*':
		mult = calc.root.mult(arg1, arg2)
		print(mult)
	elif op == '/':
		div = calc.root.div(arg1, arg2)
		print(div)
