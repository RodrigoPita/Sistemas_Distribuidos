# Servidor de calculadora usando RPyC
import rpyc
from rpyc.utils.server import ThreadedServer

class Calculadora(rpyc.Service):
	'''Classe que oferece operacoes matematicas basicas'''
	exposed_aux=10
	def on_connect(self, conx):
		print("Conexao estabelecida.")
	def on_disconnect(self, conx):
		print("Conexao encerrada.")
	def exposed_soma(self, a, b):
		return a+b
	def exposed_sub (self, a, b):
		return a-b
	def exposed_mult (self, a, b):
		return a*b
	def exposed_div (self, a, b):
		return a/b

calculadora = ThreadedServer(Calculadora, port=10000)
calculadora.start()