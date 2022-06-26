# import the necessary packages
import cv2
import os
import numpy as np
from os import listdir
import argparse
import sys
import shutil

linhaInfoCantosPlaca=6

def obtemImagens(nomeArquivo):
    # OBTENDO A PLACA E OS CARACTERES DELA DO ARQUIVO
	fo = open(nomeArquivo, "r")
	#indo para a posição da placa
	placaLinha = fo.readlines()
	placa = placaLinha[linhaInfoCantosPlaca]
	placa=placa[7:16]
	mediaAltura=0
	mediaLargura=0

	posicoesCaracteres=np.zeros((7,4))
	try:
		for i in range(7):
			posicaoPlaca = placaLinha[8+i]
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

			if posicaoPlaca[18 + deslocador] == ' ':
				largura=int(posicaoPlaca[17+deslocador:18+deslocador])
			else:
				deslocador = deslocador + 1
				largura=int(posicaoPlaca[17+deslocador-1:19+deslocador])

			altura=int(posicaoPlaca[19+deslocador:21+deslocador])		
			posicoesCaracteres[i]=(x,y,largura,altura)
			mediaAltura+=altura
			mediaLargura+=largura

	except: 	
		mediaAltura=0
		mediaLargura=0

	tamanho=mediaAltura*mediaLargura/7
	fo.close()

	return(placa,posicoesCaracteres,tamanho)


def main():
	parser = argparse.ArgumentParser(description='args')
	parser.add_argument('--dataset')			#recebe o caminho onde costam as pastas das placas do UFPR-ALPR
	args = parser.parse_args()
	if args.dataset == None:
		filePath="UFPR-ALPR/"
	else:
		filePath=str(args.dataset)

	caractesresPath="caracteres/"
	pastas = [arq for arq in listdir(filePath)]
	contador=[0]*37
	maiorTamanho=0

	for numeroPasta in pastas:
		print("Pasta atual: "+str(numeroPasta))
		arquivos = [arq for arq in listdir(filePath+numeroPasta+"/")]
		jpgs = [arq for arq in arquivos if arq.lower().endswith(".png")]

		for JPG in jpgs:
			txt=JPG[:-3]+"txt"
			placa,posicoesCaracteres,tamanho=obtemImagens(filePath+numeroPasta+"/"+txt)
			if tamanho>maiorTamanho:
				placaM=placa
				posicoesCaracteresM=posicoesCaracteres

		letraAtual=0
		for i in range(7):
			imagem = cv2.imread(filePath+numeroPasta+"/"+JPG)
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
				contador[letraParaAsc]+=1
				valor=contador[letraParaAsc]

			if valor!=1:				#verificando se ja foi criado o diretorio da letra
				cv2.imwrite(caractesresPath+placaM[letraAtual]+"/"+str(valor+3200)+".jpg", caracter)
			else:
				if not os.path.isdir(caractesresPath):
					os.mkdir(caractesresPath)
				#Removendo o diretorio caso exista
				if os.path.isdir(caractesresPath+placaM[letraAtual]):
					shutil.rmtree(caractesresPath+placaM[letraAtual])
				os.mkdir(caractesresPath+placaM[letraAtual])
				cv2.imwrite(caractesresPath+placaM[letraAtual]+"/"+str(valor+3200)+".jpg",caracter)

			letraAtual+=1
			if letraAtual==3:
				letraAtual+=1

if __name__ == '__main__':
    sys.exit(main())