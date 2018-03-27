#!/usr/bin/python3

import webapp
from urllib.parse import unquote
import csv

HTTP_CODE = "http%3A%2F%2F"
HTTPS_CODE = "https%3A%2F%2F"
MAQUINA = "localhost"
PUERTO = 1234

class MyApp(webapp.webApp):

    url_real = {}
    url_acort = {}
    http_code = " "
    html_body = " "
    contador = 0

    def leer(self):
        try:
            with open("urls.csv") as fichero:
                leer = csv.reader(fichero, delimiter=',')
                for row in leer:
                    self.url_real[row[0]] = row[1]
                    self.url_acort[row[1]] = row[0]
                    self.contador += 1
        except FileNotFoundError:
            print("No existe fichero para leer")

    def escribir(self):
        with open("urls.csv", "w", newline='') as fichero:
            escritura = csv.writer(fichero, delimiter=',')
            for elementos in self.url_real:
                escritura.writerow([elementos, self.url_real[elementos]])

    def parse(self, request):
        self.leer()
        return(request.split(' ', 1)[0], request.split(' ', 2)[1], request.split('\r\n\r\n')[-1])

    def process(self, parsedRequest):
        metodo, recurso, url_real = parsedRequest
        if(metodo == "GET"):
            if recurso == "/":
                if self.contador == 0:
                    guardada = "No hay ninguna URL"
                else:
                    guardada = "Las URLs guardaddas son: <br>"
                for corta, larga in self.url_real.items():
                    guardada = guardada + (corta + " con nr " + larga + "<br>")
                http_code = "HTTP/1.1 200 OK"
                formulario = """
                             <form action="" method="POST">
                                 URL a acortar:<br>
                                 <input type="text" name="URL" value=""><br>
                                 <input type="submit" value="Acortar URL">
                             </form>
                             """
                html_body = ("<html><body>" + formulario +"URLs acortadas: " + str(self.url_real) + "</html></body>")
            else:
                index_acortada = recurso[1:]
                if recurso in self.url_real:
                    sin_acortar = self.url_real[index_acortada]
                    http_code = "HTTP/1.1 308 Permanent Redirect"
                    html_body = ("<html><body>Redireccion " + sin_acortar + "<meta http-equiv='refresh' content='0;url=" + index_acortada + "'>" + "</body></html>")
                else:
                    http_code = "HTTP/1.1 404 Not Found"
                    html_body = ("<html><body><h1>No hay recurso" + "</h1></body></html>")
        elif(metodo == "POST"):
            if url_real == "":
                http_code = "HTTP/1.1 204 No Content"
                html_body = ("<html><body><h1>Sin contenido. Necesita introducir URL" + "</h1></body></html>")
            else:
                if(url_real[0:14] == HTTPS_CODE or url_real[0:13] == HTTP_CODE):
                    url_real = unquote(url_real)
                else:
                    url_real = "http://" + url_real

                self.contador = len(self.url_real)
                if url_real in self.url_real:
                    enlace = ("http://" + MAQUINA + ":" + str(PUERTO) + "/" + str(self.url_real[url_real]))
                    http_code = "HTTP/1.1 200 OK"
                    html_body = ("<html><body>La URL acortada es: " + "<a href=" + enlace + ">" + enlace + "</a></body></html>")
                else:
                    self.url_real[url_real] = self.contador
                    enlace = "http://" + MAQUINA + ":" + str(PUERTO) + "/" + str(self.contador)
                    self.url_acort[self.contador] = url_real
                    self.contador += 1
                    self.escribir()
                    http_code = "HTTP/1.1 200 OK"
                    html_body = ("<html><body>La URL acortada es: " + "<a href=" + enlace + ">" + enlace + "</a></body></html>")
        else:
            http_code = "HTTP/1.1 405 Method Not allowed"
            html_body = ("<html><body><h1>Este metodo no esta permitido" + "</h1></body></html>")
        return(http_code, html_body)

if __name__ == "__main__":
    testWebApp = MyApp(MAQUINA, PUERTO)
