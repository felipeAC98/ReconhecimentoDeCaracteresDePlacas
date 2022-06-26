import numpy as np
import cv2
from sklearn.neighbors import KNeighborsClassifier
import pickle
import datetime
import sys
import argparse

#==================== EDICOES BASICAS PARA A IMAGEM ====================

#PARAMETROS DE ENTRADA: imagem(imagem)

#RETORNO: imagem em tons de cinza (imagemCinza)

def editaPlaca(imagem):


	#== Deixando somente em tons de cinza
	imagemCinza = cv2.cvtColor(imagem,cv2.COLOR_BGR2GRAY)
	imagemCinza=cv2.equalizeHist(imagemCinza)
	return imagemCinza

#==================== FUNCAO DE ORDENACAO DOS CONTORNOS ====================

#PARAMETROS DE ENTRADA: contornos localizados (cnts)

#RETORNO: contornos porem agora ordenados em relacao ao eixo X (esquerda para direita)

def ordenaContornos(cnts):
	reverse = False
	i = 0
 
	boundingBoxes = [cv2.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))
 
	# retorna a lista de contornos ordenada
	return (cnts)


#==================== FUNCAO DE BUSCA DOS CARACTERES DA PLACA ==================== 


#PARAMETROS DE ENTRADA: imagem (imagem), valor divisorio da funcao thresh (threshN), numero de caracteres que se deseja encontrar (nCaracteresDesejado)

#RETORNO: a funcao retorna o numero de caracteres encontrados (numeroCaracteres) e um vetor contendo as coordenadas destes caracteres (posCaracteres)

def procuraCaracteres(imagem,threshN,nCaracteresDesejado): 


	#a funcao de threshold binariza a imagem somente deixando os pixels com 255 ou 0, o parametro threshN eh o valor de divisao para o pixel virar 0 ou 255
	_,threshold = cv2.threshold(imagem,threshN,255,cv2.THRESH_BINARY)
	contours,hierarchy= cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE) #quando no linux talvez precise adicionar mais um retorno para a funcao antes de contours
	posCaracteres=np.zeros((nCaracteresDesejado,4))
	posCaracteresTemp=[]														#Variavel que ira conter os contornos localizados na triagem inicial

	#========= buscando contorno correto da placa(sera possivelmente o maior contorno dentro da imagem)
	alturaPlaca=0
	larguraPlaca=0

	for cnt in contours:
		[x, y, w, h] = cv2.boundingRect(cnt)
		if  h>alturaPlaca:
			alturaPlaca=h
			xPlaca=x
			larguraPlaca=w
			yPlaca=y

	multiplicadorAltura=0.35
	multiplicadorLargura=0.25


	#==== Ordenando os contornos localizados
	try:
		contours=ordenaContornos(contours) #ordenando os contornos localizados
	except Exception as e:
		print(e)


	#========= Buscando os caracteres da placa

	#Esta eh somente uma triagem inicial dos contornos localizados na placa

	numeroCaracteresTemp=0
	
	for cnt in contours:

		[x,y,w,h] = cv2.boundingRect(cnt)
		
		#=== definindo o tamanho dos contornos que podem ser possiveis caracteres

		if h>=(alturaPlaca*multiplicadorAltura) and w<larguraPlaca*multiplicadorLargura:

			try:
				posCaracteresTemp.append([x,y,w,h])
			except:
				numeroCaracteresTemp=0
				break

			numeroCaracteresTemp+=1

	caracterAtual=0 #e tambem o numero de caracteres localizado
	#=== Agora eh verificado qual dos contornos realmente sao caracteres(isso eh feito com base na distancia entre um contorno e outro e seus tamanhos)

	if numeroCaracteresTemp>=7: 
		for i in range(0,numeroCaracteresTemp):
			#== Verificando se esta na primeira iteracao para comparar o contorno atual com o proximo, ambos possiveis caracteres
			if caracterAtual==0 and i<6:
				x=(int)(posCaracteresTemp[i][0])
				w=(int)(posCaracteresTemp[i][2])
				y=(int)(posCaracteresTemp[i][1])
				h=(int)(posCaracteresTemp[i][3])
				somador=1

			#== Nas demais iteraçoes ira comparar o ultimo caracter localizado com o proximo contorno(possivel caracter)
			else:
				x=(int)(posCaracteres[caracterAtual-1][0])
				w=(int)(posCaracteres[caracterAtual-1][2])
				y=(int)(posCaracteres[caracterAtual-1][1])
				h=(int)(posCaracteres[caracterAtual-1][3])
				somador=0

			#= estes multiplicador eh para dar a distancia entre o ponto inicial de um caracter ate o proximo
			multiplicadorDistancia=1.5

			#= caso seja o terceiro caracter ou o caracter seja "1" ou "I"

			if caracterAtual==3 or w*2<=posCaracteresTemp[i+somador][2]or w*1.6<posCaracteres[caracterAtual+somador-2][2]:
				multiplicadorDistancia=5
			try:	
			#== O if abaixo eh muito importante, ele compara o caracter atual com o proximo possivel caracter para ver se eh realmente um caracter ou algum contorno enganoso
			#as comparacoes que ele faz sao com base nas relacoes de posicionamento entre o caracter anterior e o proximo

				if x+multiplicadorDistancia*w>=posCaracteresTemp[i+somador][0] and (y-0.2*h)<posCaracteresTemp[i+somador][1] and (y+h*0.2)>posCaracteresTemp[i+somador][1] and ((y+h)*0.85)<(posCaracteresTemp[i+somador][1]+posCaracteresTemp[i+somador][3]) and (1.15*(y+h))>(posCaracteresTemp[i+somador][1]+posCaracteresTemp[i+somador][3]) :
				#y+h = altura do contorno (possivel caracter)
					try:
						posCaracteres[caracterAtual]=posCaracteresTemp[i]
						caracterAtual+=1
					except: #excedeu de 7 caracteres localizados
						break
						
			except:
				break

	numeroCaracteres=caracterAtual
	return numeroCaracteres,posCaracteres


#==================== FUNCAO DE PREDICAO ====================

#Função que ira predizer o caracter encontrado por meio do modelo KNN ja treinado (mas caso passe uma arvore de busca como modelo (por exemplo) tambem ira funcionar)


#PARAMETROS DE ENTRADA: imagem(imagem), posicao do caracter em questao(posCaracter), modelo treinado(modelo)

#RETORNO: Caracter predito (chr(int(predict))), score do caracter (np.amax(y_scores) )

def predicao(imagem,posCaracter,modelo):
	#==== obtendo a posicao da imagem
	x=(int)(posCaracter[0])
	y=(int)(posCaracter[1])
	w=(int)(posCaracter[2])
	h=(int)(posCaracter[3])

	#==== cortando a imagem
	caracter = imagem[y:y+h, x:x+w]
	caracterRes = cv2.resize(caracter,(7,12))
	caracterRes = caracterRes.reshape((1,84))
	caracterRes = np.float32(caracterRes)

	#==== predicao
	predict=modelo.predict(caracterRes)
	y_scores = modelo.predict_proba(caracterRes)	
	return chr(int(predict)),np.amax(y_scores)           


#==================== Função de correção da placa ====================

#devido ao fato de sabermos onde so pode ter numeros e onde so pode ter letras podemos "concertar" algumas coisas

#PARAMETROS DE ENTRADA: lista de caracteres localizados(placa)

#RETORNO: lista de caracteres ja transformados(letras + numeros)

def limparPlaca(placa):
	letras = placa[:3]
	numeros = placa[3:]

	letras = [w.replace('0', 'O') for w in letras]
	letras = [w.replace('1', 'I') for w in letras]
	letras = [w.replace('4', 'A') for w in letras]
	letras = [w.replace('6', 'G') for w in letras]
	letras = [w.replace('7', 'I') for w in letras]
	letras = [w.replace('8', 'B') for w in letras]
	letras = [w.replace('2', 'Z') for w in letras]
	letras = [w.replace('5', 'S') for w in letras]

	numeros = [w.replace('B', '8') for w in numeros]
	numeros = [w.replace('T', '1') for w in numeros]
	numeros = [w.replace('Z', '2') for w in numeros]
	numeros = [w.replace('S', '5') for w in numeros]
	numeros = [w.replace('A', '4') for w in numeros]
	numeros = [w.replace('O', '0') for w in numeros]
	numeros = [w.replace('I', '1') for w in numeros]
	numeros = [w.replace('G', '6') for w in numeros]
	numeros = [w.replace('Q', '0') for w in numeros]
	numeros = [w.replace('D', '0') for w in numeros]

	return letras + numeros

#==================== FUNCAO DE LEITURA DA PLACA ====================


#Principal funcao do algoritmo (faz a juncao das demais)

#Ela que sera chamada pelo programa externo, a mesma retorna uma lista contendo os caracteres da placa

#PARAMETROS DE ENTRADA: imagem(imagem), valor de certeza da predicao passe 6 para maior velocidade e menor precisao  7 para maior precisao e menor velocidade (certezaPredicao), o ultimo parametro eh o local onde se encontra  modelo treinado(modelo) 

#RETORNO: lista de caracteres(placa)


def leituraPlaca(imagem,certezaPredicao,modelo):
	#==== carregando o modelo que ira realizar a predição
	loaded_model = pickle.load(open(modelo, 'rb'))
	totalDeValores=imagem.shape[0]*imagem.shape[1]*imagem.shape[2]
	imagem=editaPlaca(imagem)					#recebe a imagem ja editada

	#================ Buscando os caracteres da placa


	# parametros utilizados na busca dos caracteres
	nDesejados=7								#numero de caracteres que se deseja localizar
	passo=2										#tamanho do passo do threshold para cada iteração (quanto maior mais rapido o algoritmo e menos preciso)
	nEncontrados=0								#numero de caracteres encontrados na iteração
	tentativas=0								#tentativas da placa atual
	tantativasTotais=190/passo					#tentativas totais para a placa atual
	nEncontradosM =0							#valor maximo de caracteres encontrados ate agora para esta placa
	parametroThresh=25							#Valor inicial para o ThreshHold
	maxScore=0									#Valor maximo de score para a placa	
	placaM=[]
	scoreLetras=np.zeros((7,36))
	#Neste momento eh feito a busca dos caracteres na tela por meio dos contornos para varios tons diferentes ate que se localize os 7 caracteres
	scorePlaca=0
	
	while(tentativas<tantativasTotais and scorePlaca<=certezaPredicao):
		scorePlaca=0		
		nEncontrados,posCaracteres=procuraCaracteres(imagem,parametroThresh,nDesejados)
		if (nEncontrados==nDesejados ):
			placa=[]
			for i in range(nEncontrados):
				caracter,score=predicao(imagem,posCaracteres[i],loaded_model) #aqui eh o principal, onde esta predizendo cada caracter pelo passo inferior
				valorEmAsc=ord(caracter)		
				
				if valorEmAsc<65:
					scoreLetras[i][valorEmAsc-48]+=score					  #somando o score para este caracter nesta posicao
				else:
					scoreLetras[i][valorEmAsc-55]+=score
				scorePlaca=scorePlaca+score
				placa.append(caracter)


			#para o caso de a certezaPredicao for menor que 7 e o algoritmo encontrar mais de uma placa com 7 caracteres ele ira retornar a que tiver obtido maior pontuacao
			if scorePlaca> maxScore:
				maxScore=scorePlaca
				placaM=placa

			#Sempre que forem achados 7 caracteres o valor de tentativas eh aumentado pois foi uma tentativa bem sucedida e portanto nao precisamos repetir muitas vezes este processo de localizacao de caracteres
			tentativas+=10

		parametroThresh=parametroThresh+passo
		tentativas+=1


	scorePos=[0]*7
	letra=[0]*7


	#Caso a certezaPredicao seja 7 entao sera verificado para cada posicao da placa o caracter que obteve maior pontuacao nela

	if certezaPredicao ==7:
		for i in range(0,36):
			for k in range(0,7):
				if scoreLetras[k][i]>=scorePos[k]:
					scorePos[k]=scoreLetras[k][i]
					letra[k]=i

		if placaM!=[]:
			for i in range(0,7):
				if letra[i]<10:
					placaM[i]=str(chr(letra[i]+48))
				else:
					placaM[i]=str(chr(letra[i]+55))

	placaM=limparPlaca(placaM)		
	return placaM

#=========== EXEMPLO ===========

def main():
	import datetime
		
	parser = argparse.ArgumentParser(description='args')
	parser.add_argument('--modelo')				#modelo a ser utilizado
	args = parser.parse_args()
	modelo="modelos/modeloKNN.sav"
	
	if args.modelo != None:
		modelo=str(args.modelo)
	
	inicio = datetime.datetime.now()
	#Gabarito
	placaH=['H','C','Y','2','6','8','4']
	placaP=['P','V','I','1','3','3','4']
	contaErro=0
	nPlacas=32

	for i in range(0,nPlacas):
		imagem=cv2.imread("placas/placa0"+str(i)+".jpg")
		certezaPredicao=7
		placa=leituraPlaca(imagem,certezaPredicao,modelo)
		
		if placa!=placaH and placa !=placaP:
			contaErro+=1
			print("Erro em: placas/placa0"+str(i)+".jpg")
			print(placa)
			print("\n")

	fim = datetime.datetime.now()
	print('Tempo de Execução medio: '+str((fim-inicio)/32))
	print("Total de placas: "+ str(nPlacas))
	print("Total de erros: "+ str(contaErro))

if __name__ == '__main__':
    sys.exit(main())
