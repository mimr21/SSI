import nexmo
import random



def main(tokenEnviar, numero):
	client = nexmo.Client(key='06b932d7', secret='d6cwUZDsyWBTZSlS')
	try:
		client.send_message({
		    'from': 'Vonage APIs',
		    'to': numero,
		    'text': 'Ola este é o token '+tokenEnviar,
		})
		return True
	except:
		print("falha no envio da mensagem")
		return False

if __name__ == '__main__':
    main(tokenEnviar,numero)