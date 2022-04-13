from flask import Flask, render_template, request, flash, url_for, redirect, session
from datetime import timedelta

import time
import os de
import json

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "Papel"
app.permanent_session_lifetime = timedelta(minutes=90)





@app.route("/", methods=["POST", "GET"])
def index():
   
   try:
                  if request.method == "POST":
                          session.permanent = True
                          fnome = request.form["nome"]
                          fsexo = request.form["sexo"]
                          session["fnome"] = fnome
                          session["fsexo"] = fsexo

                          return redirect(url_for("/"))

                  #primeira vez verificando
                  elif session["fnome"] and session["fsexo"]:
                          return render_template("index.html", formul=True, nome=session["fnome"])
                  else:
                          return render_template("index.html", formul=False, nome="Meu Caro")
                    
      
      
   except (TypeError, OSError, ValueError) as e:
           return render_template("erroSection.html", mensagem=e)
   except Exception as e:
           return render_template("erroSection.html", mensagem=e)
   except:
           return render_template("erroSection.html", mensagem="Erro Desconhecido!")
      
      
      


  #for para salvar sessions e dado


@app.route("/assediador")
def user():
   print()
  
          
     
@app.route("/logout")
def logout():
    print()


     

if __name__ == '__main__':

    app.run(debug=True)
