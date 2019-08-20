# licitascore

> Este repositório tem como objetivo disponibilizar o sistema **licitascore**.

Criado por ocasião do [HackFest 2019](https://hackfest.imd.ufrn.br), o Pandora Team decidiu se ater à questão das licitações e abrir a caixa de pandora desse universo, explorando informações que pudessem agilizar o trabalho do Ministério Público no rastreamento de empresas que juntas ou de maneira isolada fraudulam processo licitatórios. 

A ferramenta do **licitascore** estabelece um índice de *DESconfiabilidade* de pessoas jurídicas/CNPJs que participaram de licitações de acordo com os seguintes implementados até o momento:

❏ Processos trabalhistas e criminais

❏ Cadastro de empresas inidôneas

❏ Número de CNAEs das empresas

O resultado foi aplicado em dois quadros interativos que se complementam - o primeiro, um mapa do estado do Rio Grande do Norte com os nomes e licitascores de diferentes empresas e as localizações de suas sedes e o segundo é um grafo em que as diferentes empresas analisadas são conectadas por sócios em comum, caso haja.

Além disso, seguindo indicação de uma outra necessidade do MP, foram construídas diversas análises generalistas acerca das licitações realizadas no Rio Grande do Norte. São representadas as modalidades empregadas em diferentes anos e os tipos de objeto adquiridos através desses processos a fim de estimular perguntas chave para outras análises e identificação de possíveis anormalidades.

### Dados :memo:

Os Dados disponíveis no sistema são dados abertos reais dispobilizados pelos portais da [Receita Federal](http://receita.economia.gov.br/orientacao/tributaria/cadastros/cadastro-nacional-de-pessoas-juridicas-cnpj/dados-publicos-cnpj) e do [Jusbrasil](https://www.jusbrasil.com.br/home).

Os dados foram obtidos filtrando as licitações vencendoras disponíveis no TCE-RN com as palavras chaves "ALIMENTAÇÃO EST" e "MERENDA" em 2019.

### Execução :dart:

O sistema foi desenvolvido nas linguagen Python3 e R. 

Para seu funcionamento são necessários os seguintes módulos, que podem ser instalados via terminal:

````
pip3 install -r requirements.txt
````

Uso:

````
python3 main.py
````

Uma vez instalados os módulos o script main.py deve ser executado e o site estará disponível no navegador.

### Autores :busts_in_silhouette:

:bust_in_silhouette: __Danilo Rodrigo__:
* [Github](https://github.com/DaniloRodrigo)
* [Lattes](http://lattes.cnpq.br/8497491123988999)

:bust_in_silhouette: __Dhiego Souto__:
* [Github](https://github.com/dhiego22)
* [Lattes](http://lattes.cnpq.br/7232169055258869)

:bust_in_silhouette: __Paulo Soares__:
* [Github](https://github.com/Hatsura)
* [Lattes](http://lattes.cnpq.br/1232677110942724)

:bust_in_silhouette: __Patrick Terrematte__:
* [Github](https://github.com/terrematte)
* [Lattes](http://lattes.cnpq.br/4283045850342312)

:bust_in_silhouette: __Tayná Fiúza__:
* [Github](https://github.com/fiuzatayna)
* [Lattes](http://lattes.cnpq.br/4497357102512154)
