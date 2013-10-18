Matplotlib


Pra rodar todas as funções do pylab direto no iPython

$ ipython --pylab

ou então

$ import pylab


Comandos básicos:

Plotar x por y com linhas:

$ pylab.plot(x, y, "r") # dá pra passar a cor
$ pylab.show()  # deveria funcionar :(
$ pylab.savefig("nome_da_figura.png")
$ pylab.clf() # limpar plot completo

$ title("Titulo do gráfico")
$ xlabel("Label do eixo x")
$ ylabel("Label do eixo y")


$ pylab.linspace(start, end, num_of_points)


# Scatter (só pontos)

$ pylab.scatter(x, y)
