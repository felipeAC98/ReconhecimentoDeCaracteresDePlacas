# import the necessary packages
import cv2
import os
import numpy as np
from os import listdir

def obtemImagens(nomeArquivo):
    # OBTENDO A PLACA E OS CARACTERES DELA DO ARQUIVO


	fo = open(nomeArquivo, "r")

	#indo para a posição da placa

	placaLinha = fo.readlines()
	placa = placaLinha[6]
	
	placa=placa[7:16]
	print (placa)
	mediaAltura=0
	mediaLargura=0

	posicoesCaracteres=np.zeros((7,4))
	try:
		for i in range(7):

			posicaoPlaca = placaLinha[8+i]
			print(posicaoPlaca)
			deslocador=0


			if posicaoPlaca[12] == ' ':
				x=int(posicaoPlaca[9:12])
			else :
				deslocador=deslocador+1
				x = int(posicaoPlaca[9:13])

			if posicaoPlaca[16 + deslocador] == ' ':
				y=int(posicaoPlaca[13+deslocador:16+deslocador])
			else:
				deslocador = deslocador + 1
				y=int(posicaoPlaca[13+deslocador-1:17+deslocador])

			print("deslocador: " +str(deslocador))

			if posicaoPlaca[18 + deslocador] == ' ':
				largura=int(posicaoPlaca[17+deslocador:18+deslocador])
			else:
				deslocador = deslocador + 1
				largura=int(posicaoPlaca[17+deslocador-1:19+deslocador])

			altura=int(posicaoPlaca[19+deslocador:21+deslocador])		

			posicoesCaracteres[i]=(x,y,largura,altura)


			mediaAltura+=altura

			mediaLargura+=largura
		#print(posicoesCaracteres)

	except: 	
		mediaAltura=0
		mediaLargura=0

	tamanho=mediaAltura*mediaLargura/7
	fo.close()

	return(placa,posicoesCaracteres,tamanho)




pastas = [arq for arq in listdir("validation/")]

contador=[0]*37

maiorTamanho=0

for numeroPasta in pastas:

	arquivos = [arq for arq in listdir("validation/"+numeroPasta+"/")]
	jpgs = [arq for arq in arquivos if arq.lower().endswith(".png")]

	for JPG in jpgs:


		txt=JPG[:-3]+"txt"
		print(txt)
		placa,posicoesCaracteres,tamanho=obtemImagens("validation/"+numeroPasta+"/"+txt)

		if tamanho>maiorTamanho:
			placaM=placa
			posicoesCaracteresM=posicoesCaracteres


	print(posicoesCaracteresM[0][1])
	letraAtual=0
	for i in range(7):

		imagem = cv2.imread("validation/"+numeroPasta+"/"+JPG)


		x=(int)(posicoesCaracteresM[i,0])
		y=(int)(posicoesCaracteresM[i,1])
		w=(int)(posicoesCaracteresM[i,2])
		h=(int)(posicoesCaracteresM[i,3])


		#posicoesCaracteres[i]=(x,y,largura,altura)
		caracter = imagem[y:y+h, x:x+w]
		
		if ord(placaM[letraAtual])<65: 					#se for um numero
			contador[int(placaM[letraAtual])]+=1
			valor=contador[int(placaM[letraAtual])]


		else:						#entao eh letra
			letraParaAsc=ord(placaM[letraAtual])-54
			print(letraParaAsc)
			contador[letraParaAsc]+=1
			valor=contador[letraParaAsc]

		if valor!=1:				#verificando se ja foi criado o diretorio da letra

			cv2.imwrite("caracteres/"+placaM[letraAtual]+"/"+str(valor+3200)+".jpg", caracter)

		else:
			#print("Criando diretorio: "+JPG[letraAtual])
			os.mkdir("caracteres/"+placaM[letraAtual])
			cv2.imwrite("caracteres/"+placaM[letraAtual]+"/"+str(valor+3200)+".jpg",caracter)

		letraAtual+=1
		if letraAtual==3:
			letraAtual+=1
'''
		if largura*altura>tamanhoMaiorPlaca:
			arquivoComMaiorPlaca=i
			tamanhoMaiorPlaca=largura*altura

		if arquivoComMaiorPlaca<10:
		        nomeArquivo = "testing/track00"+str(imgNumber)+"/track00"+  str(imgNumber) + "[0"+ str(arquivoComMaiorPlaca) +"].txt"
		        imageName = "testing/track00"+str(imgNumber) +"/track00"+  str(imgNumber) + "[0"+str(arquivoComMaiorPlaca) +"].png"
		else:
		        nomeArquivo = "testing/track00"+str(imgNumber)+"/track00"+  str(imgNumber) + "["+ str(arquivoComMaiorPlaca)+"].txt"
		        imageName = "testing/track00"+str(imgNumber) +"/track00"+  str(imgNumber) + "["+ str(arquivoComMaiorPlaca)+"].png"	


		x,y,largura,altura=obtemImagens(nomeArquivo)

		print("Maior placa nos arquivos: "+str(arquivoComMaiorPlaca))
		print(x)
		print(y)
		print(largura)
		print(altura)
		print(imageName)
		#print (altura)

		# Close opend file
		

		# OBTENDO A PLACA DA IMAGEM

		image = cv2.imread(imageName)


		#image[y:Y+tamanho , x:x+tamanho
		cropped = image[y:(y+altura),x:(x+largura)]
		cv2.imshow("cropped", cropped)
		cv2.waitKey(0)

		cv2.imwrite("imagensCortadas/track00"+str(imgNumber) + "[01].png", cropped)
'''

