# Reconhecimento De Placas veiculares
Código em python para efetuar a leitura de placas de carros brasileiros


## Resumo da solução

A solução final consiste em efetuar a leitura de uma imagem buscando obter os caracteres da mesma e então estes seriam preditos por um modelo previamente treinado. Para isso foi necessário:

-	Obter imagens de placas
-	Separação dos caracteres
-	Criar e treinar um modelo
-	Função final para reconhecer os caracteres de uma nova placa e predizer eles com o modelo que já estava pronto. 


## Obtenção das imagens

As imagens foram obtidas por meio de um data set da UFPR (https://web.inf.ufpr.br/vri/databases/ufpr-alpr/), seguem os créditos:

R. Laroca, E. Severo, L. A. Zanlorensi, L. S. Oliveira, G. R. Gonçalves, W. R. Schwartz, D. Menotti, “A Robust Real-Time Automatic License Plate Recognition Based on the YOLO Detector,” in 2018 International Joint Conference on Neural Networks (IJCNN), July 2018, pp. 1–10. [IEEE Xplore] [PDF] [BibTeX]

O dataset possui imagens de veículos e documentos com as respectivas posições das placas e seus caracteres.

## Separação dos caracteres

 Uma vez que cada imagem do dataset obtido possui um arquivo com a posição de cada caractere na placa, bastou ser criado um código para ir lendo estes documentos ,obtendo os caracteres das imagens e então ir salvando cada imagem de caractere em um arquivo diferente e em pastas diferentes(cada pasta só possui um tipo de caractere) que posteriormente seria utilizado para o treino. O código utilizado nesta etapa está com o nome “separaCaracteres.py”, para utiliza-lo da melhor forma possível é necessário inserir o parâmetro --dataset com o caminho para a pasta onde se encontram as "tracks" do UFPR-ALPR dataset.

Após a separação dos caracteres foi observado que havia muita diferença no número de caracteres para cada caractere, por exemplo, haviam 200 exemplos da letra “A” e somente 30 da letra “Y”, isso iria causar um pequeno problema no momento em que fosse passado para o modelo uma imagem para ele tentar acertar, pois haveria muito mais chance de ele dizer que era um “A” do que um “Y” dependendo da qualidade da imagem, para tentar contornar isso foi criado um código de “data augmentation” para deixar as imagens em quantidades mais próximas. O código consiste em dada uma imagem ele efetuar alterações aleatórias no brilho, rotação e zoom da imagem. 

O código inicial para a parte de data augentation foi retirado deste site: http://sigmoidal.ai/reduzindo-overfitting-com-data-augmentation/ e feitas algumas adaptações criando então o código “dataAugmentation.py”.

## Transformação e rotulação
Processo responsável por efetuar a leitura das imagens, transformaçao para tons de cinzas e a rotulação conforme o nome da pasta (uma vez que em cada pasta somente iríamos ter um tipo de caracter). O resultado são duas matrizes, uma contendo os rótulos e outra as imagens, ambas são salvas em formas de arquivos .data para utilização no treinamento. O código responsável por isso é o “rotulaTreino.py”

## Treinamento um modelo

O algoritmo de aprendizado de máquina selecionado foi o KNN. De forma resumida, para esta aplicação o mesmo atua da seguinte forma: dado um novo caracter ele será comparado com K outros caracteres mais próximos, o rótulo que estiver em maior número dentre estes K será o que novo caracter irá receber. Para saber qual o número de caracteres que deveria ser comparado foi efetuado um teste para diversos valores iniciando de K= 2  até K=15 e então foi analisada a precisão de acerto para cada um destes valores, no caso o que apresentou melhor desempenho e com menor taxa de overfitting foi para K=3. O modelo treinado é salvo em um arquivo e este é utilizado na função final.

Importante notar que foram testados outros tipos de predições, como árvore de decisão e algo bem superficial de redes neurais, entretanto a árvore de decisão não estava tendo um bom resultado e a rede neural precisaria de mais tempo para ser configurada e testada.

O código responsável por essa etapa é o treinaModelo.py

## Função final

A última etapa foi criar uma função na qual conseguisse reconhecer os caracteres da placa para que então fosse possível realizar a predição destes separadamente e retornar o valor lido na placa. O código que faz isso é o predicao.py

De forma resumida:
-	A função faz a leitura de uma imagem( que deve ser uma placa recortada), passa a imagem para tons de cinza e então equaliza ela. 

-	A imagem então é binarizada com um valor inicial (parametroTresh) e então tenta obter todos contornos presentes na imagem binarizada, efetua algumas filtragens por meio de relações de tamanho entre os contornos e suas distâncias pois os caracteres possuem a mesma altura e tem uma proporção entre suas distâncias.

-	Caso forem localizados 7 caracteres estes são inseridos no modelo treinado previamente, caso não tenha sido localizados 7 caracteres o processo é repetido até que se encerre o número de tentativas estipuladas(que é um valor baseado no valor de binarização máximo viável para uma imagem). 

-	No momento em que cada caractere é predito ele obtém uma pontuação que é baseada nos K outros caractere que ele mais se assemelhou para o modelo, caso os K caracteres possuam o mesmo rótulo então o caractere que está sendo predito receberá a pontuação máxima, caso contrário a pontuação será proporcional ao rótulo que está em maioria dentre os K mais próximos.

-	Dependendo do valor do parâmetro “certezaPredição” (se menor que 7) o processo irá se repetir até que o valor da soma dos Scores seja igual ao valor da “certezaPredição” e irá ser retornada a placa que somou maior pontuação em seus caracteres até aquele momento. No caso do valor da “certezaPredição” for 7 o processo irá provavelmente se repetir um número próximo do total de tentativas para cada placa e será retornado o conjunto de caracteres que terem recebido maior soma na pontuação para cada posição.


Foi utilizada uma função de ordenação de contornos baseada na disponibilizada neste site: https://www.pyimagesearch.com/2015/04/20/sorting-contours-using-python-and-opencv/

# Como executar
- Instale as bibliotecas python presentes em requirements.txt

## Execução completa
Siga os passos abaixo para efetuar todas as etapas do projeto

Execute os códigos na seguinte ordem: 

    $ python3 separaCaracteres.py --dataset "CAMINHO PARA PASTAS DO DATASET UFPR-ALPR"
    $ python3 dataAugmentation.py
    $ python3 rotulaTreino.py
    $ python3 treinaModelo.py
    $ python3 predicao.py

## Somente predição

Execute o comando abaixo somente para verificar a saida do arquivo de predição utilizando o modelo ja treinado, a saida será semelhante ao arquivo saida_predicao.txt

    $ python3 predicao.py