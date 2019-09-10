import sys
import numpy as np
import cv2
import os
from os import listdir

#===================== MAIN ==========================

# definindo algumas variaveis para salvar os caracteres em um banco de caracteres rotulados


placasDoTreino=0
	
nErradas=0
respostas = []
caracteres = np.empty((0,84))


pastas = [arq for arq in listdir("aumenta/")]

for pasta in pastas:

	arquivos = [arq for arq in listdir("aumenta/"+pasta+"/")]

	imagens = [arq for arq in arquivos if arq.lower().endswith(".jpg")]
	print(pasta)

	for imagemCaracter in imagens:

		imagem=cv2.imread("aumenta/"+pasta+"/"+imagemCaracter)


		#Deixando somente em tons de cinza

		gray = cv2.cvtColor(imagem,cv2.COLOR_BGR2GRAY)

		#Equalizando a imagem
		gray=cv2.equalizeHist(gray)


		rotulo=pasta



#==================== Salvando imagem em tons de cinza

		resize = cv2.resize(gray, (7, 12))

		respostas.append(ord(rotulo))

		caracter = resize.reshape((1, 84))
		caracteres = np.append(caracteres, caracter, 0)


#============ Salvando rotulacao (somente para sklearn)


respostas = np.array(respostas,np.float32)


respostas = respostas.reshape((respostas.size,1))

np.savetxt('caracteres.data',caracteres)
np.savetxt('rotulos.data',respostas)




