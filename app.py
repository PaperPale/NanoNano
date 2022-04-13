from flask import Flask, render_template, request, flash, url_for, redirect, session
from datetime import timedelta

import time
import os
import json

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "Papel"
app.permanent_session_lifetime = timedelta(minutes=90)





@app.route("/", methods=["POST", "GET"])
def index():
   
                  if request.method == "POST":
                          session.permanent = True
                          session["nome"] = request.form["nome"]
                          

                          return render_template("index.html", formul=True, nome=session["nome"])

                  #primeira vez verificando
                  elif "nome" in session:
                          if session["nome"] == None:
                               return render_template("index.html", formul=False, nome=session["nome"])
                          else:
                               return render_template("index.html", formul=True, nome=session["nome"])
                  
                  else:
                          return render_template("index.html", formul=False, nome="Meu Caro")
                    
      
      
      


  #for para salvar sessions e dado  
          
     
@app.route("/clear")
def clear():
    session["nome"] = None
    print("limpador!")
    return redirect(url_for("/"))
 


     

if __name__ == '__main__':

    app.run(debug=True)
