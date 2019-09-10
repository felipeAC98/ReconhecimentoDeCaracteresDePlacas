# importar os pacotes necessários


#http://sigmoidal.ai/reduzindo-overfitting-com-data-augmentation/

import numpy as np
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
from os import listdir
import os

pastas = [arq for arq in listdir("caracteres/")]

for pasta in pastas:


	arquivos = [arq for arq in listdir("caracteres/"+pasta+"/")]
	os.mkdir("aumenta/"+pasta)
	imagens = [arq for arq in arquivos if arq.lower().endswith(".jpg")]
	imagensCriadas=0

	numeroDeImagens=len(imagens)

	if numeroDeImagens<30:
		replicas=25
	elif numeroDeImagens<40:
		replicas=17
	elif  numeroDeImagens<50:
		replicas=13
	elif  numeroDeImagens<60:
		replicas=10
	elif  numeroDeImagens<80:
		replicas=9

	elif numeroDeImagens<90:
		replicas=6

	elif  numeroDeImagens<110:
		replicas=5

	elif  numeroDeImagens<150:
		replicas=4

	elif  numeroDeImagens<210:
		replicas=3

	elif  numeroDeImagens<270:
		replicas=2

	else:
		replicas=1

	for imagemCaracter in imagens:
		# definir caminhos da imagem original e diretório do output
		IMAGE_PATH = "caracteres/"+pasta+"/"+imagemCaracter
		OUTPUT_PATH = "aumenta/"+pasta+"/"
		 
		# carregar a imagem original e converter em array
		image = load_img(IMAGE_PATH)
		image = img_to_array(image)
		 
		# adicionar uma dimensão extra no array
		image = np.expand_dims(image, axis=0)
		 
		# criar um gerador (generator) com as imagens do
		# data augmentation
		imgAug = ImageDataGenerator( rotation_range=8,
						zoom_range=[0.9,1.0],
									brightness_range=[0.1,3],
				                    fill_mode='nearest', horizontal_flip=False)
		imgGen = imgAug.flow(image, save_to_dir=OUTPUT_PATH,
				             save_format='jpg', save_prefix='0000001')

		# gerar 10 imagens por data augmentation
		counter = 0
		for (i, newImage) in enumerate(imgGen):
			counter += 1
			imagensCriadas+=1

			# ao gerar 10 imagens, parar o loop
			if counter == replicas:
				break

		if imagensCriadas>500:
			break
