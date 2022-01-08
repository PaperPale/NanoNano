from flask import Flask, render_template, request, flash, url_for, redirect, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

import time
import os
import amino
import json


data_ini = "2021-06-26 17:43:30"
format = '%Y-%m-%d %H:%M:%S'

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "Papel"
app.permanent_session_lifetime = timedelta(minutes=900)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'

db = SQLAlchemy(app)

class users(db.Model):
   userId = db.Column("userId", db.Integer, primary_key=True)
   email = db.Column(db.String(42))
   password = db.Column(db.String(42))
   name = db.Column(db.String(42))
   level = db.Column(db.Integer)
   
   
   def __init__(self, userId, email, password, name, level):
   
      self.userId = userId
      self.email = email
      self.password = password
      self.name = name 
      self.level = level


client = None
sub = None
comId = None
@app.route("/", methods=["POST", "GET"])
def login():
   global client
   
   client = amino.Client()
   if request.method == "POST":
     session.permanent = True
     eform = request.form["email"]
     pform = request.form["password"]
     session["email"] = eform
     session["password"] = pform
     loginAmino = client.login(eform, pform)
     session["Auth"] = loginAmino
     
     #login sucesso
     if session["Auth"]==200:
       return redirect(url_for("user"))
   
   #primeira vez verificando
   elif "Auth" in session:
     if session["Auth"]==200:
        return redirect(url_for("user"))
     else:
        return render_template("login.html", erro="Erro de Autenticação ao Logar")
   else:
     return render_template("login.html", erro="")
     
@app.route("/logout")
def logout():
   global client, sub, comId
   session.pop("email", None)
   session.pop("password", None)
   session.pop("Auth", None)
   session.pop("DadosSubsClients", None)
   session.pop("ChatsPublicBruto", None)
   session.pop("joinedData", None)
   client = None
   comId = None
   sub = None
   return redirect(url_for("login"))


  #for para salvar sessions e dado
@app.route("/subuser", methods=["POST", "GET"])
def subuser():
  global client, sub, comId
  print("global\n\n")
  if request.args.get("comId")==None:pass
  else:
      comId=request.args.get("comId")
  
  if sub!=None and client!=None:
    try:
       sub = amino.SubClient(profile=client.profile, comId=comId)
       
          
       if request.method == "POST":
            name = request.form["name"]
            if request.form["content"]==None:
              content="Penso, logo existo"
            else:
              content = request.form["content"]
              
            
            if sub.profile.customTitles!=None:
               titlesjson = request.form["titlesjson"]
               tagTitles = []
               
               tagTitlesColors = titlesjson.split(",")
               for i in sub.profile.customTitles:
                         tagTitles.append(i['title'])
               print(tagTitles)
               print(tagTitlesColors)
               sub.edit_profile(nickname=name,
               content=content, titles=tagTitles, colors=tagTitlesColors)
            else:
              
              sub.edit_profile(nickname=name,
              content=content)
            
            return redirect(url_for("c"))
            
       else:pass
       #if POST?
       
       print("Verify Reqst\n\n")
       if "joinedData" in session:
           if sub.profile.customTitles==None:
                print("None titles")
                return render_template("sub_perfil.html", sub=sub.profile, joinedData=session["joinedData"], lenTitles=0)
           else:
                print("Titles Yes")
                lenTitles = len(sub.profile.customTitles)
               
                return render_template("sub_perfil.html", sub=sub.profile, joinedData=session["joinedData"], lenTitles=lenTitles)
                
       else:
           return redirect(url_for("c"))
           
           
           
    except Exception as e:
        return f"<span>{e}</span>"
  else:
  #sub and client !=
       return redirect(url_for("c"))
       
  



@app.route("/catalog")
def catalog():
  global client, sub
  sub = None
  session.pop("ChatsPublicBruto", None)
  session.pop("joinedData", None)
  if "Auth" in session and session["Auth"]==200:
  #usersession
     usersession = [session["email"], session["password"]]
     try:
        if client==None:
  #if client None
                client = amino.Client()
                if client.login(usersession[0], usersession[1])==200:
                      return redirect(url_for("catalog"))
                
                
        elif client!=None:
             if "DadosSubsClients" in session:
                 return render_template("comunidades.html", client=client.profile, subs=session["DadosSubsClients"])
             else:
                 subs = client.sub_clients()  
                 DadosSubsClients = []
                 for name, icon, comId, users, keys, created, lang in zip(subs.name, subs.icon, subs.comId, subs.usersCount, subs.customList, subs.createdTime, subs.primaryLanguage):
                      ListPrimary = [name, icon, comId, users, keys, created, lang]
                      DadosSubsClients.append(ListPrimary)
       
                 print(DadosSubsClients)
                 session["DadosSubsClients"] = DadosSubsClients
                 return render_template("comunidades.html", client=client.profile, subs=session["DadosSubsClients"])
        else:
           return redirect(url_for("user"))
     except Exception as e:
         return f"<span>{e}</span>"
         
  else:
     return redirect(url_for("user"))
     
  

@app.route("/c")
def c():
 global comId
 if request.args.get("comId")==None:pass
 else:
   comId=request.args.get("comId")
 
 print(comId)
 global client, sub
 try:
  if client==None: 
           return redirect(url_for("user"))
           
  elif client!=None and comId==None:  
           return redirect(url_for("user"))
   
  elif client!=None and comId!=None:
           if "DadosSubsClients" in session:
               comIds = [i[2] for i in session["DadosSubsClients"]]
           else:
               return redirect(url_for("user"))
               
           if int(comId) in comIds:
                 Joined = client.get_community_info(comId)
                 if Joined.primaryLanguage=="pt":lan="Português"
                 elif Joined.primaryLanguage=="en":lan="English"
                 elif Joined.primaryLanguage=="de":lan="Deutsch"
                 elif Joined.primaryLanguage=="ru":lan="Russo"
                 elif Joined.primaryLanguage=="ar":lan="Árabe"
                 else: lan="Nativo"
                 JoinedData = {
                       "icon":f"{Joined.icon}",
                       "name":f"{Joined.name}",
                       "usersCount":f"{Joined.usersCount}",
                       "aminoId":f"{Joined.aminoId}",
                       "link":f"{Joined.link}",
                       "primaryLanguage":f"{lan}",
                       "welcomeMessage":f"{Joined.welcomeMessage}",
                       "themeColor":f"{Joined.themeColor}",
                       "agent":f"{Joined.agent.nickname}",
                       "ranking":f"{Joined.advancedSettings['rankingTable']}",
                       "comId":f"{comId}"}
                 
                 
                 ChatsPublicBruto = []
                 ChatsUnidade = []
                 
                 if sub==None:
                    sub = amino.SubClient(profile=client.profile, comId=comId)
                    print(sub.profile.customTitles)
                    ChatsPublicInfo = sub.get_public_chat_threads(type="recommended", start=0, size=11)
                    for title, icon, author, membersCount, vvChatJoinType in zip(ChatsPublicInfo.title, ChatsPublicInfo.icon, ChatsPublicInfo.author.icon, ChatsPublicInfo.membersCount, ChatsPublicInfo.vvChatJoinType):
                                   primaryPublic = [title, icon, author, membersCount, vvChatJoinType]
                                   ChatsUnidade.append(primaryPublic)
                    for i in range(0, 18, 3):
                         ChatProcess = ChatsUnidade[i:i+3]
                         ChatsPublicBruto.append(ChatProcess)
                    session["ChatsPublicBruto"] = ChatsPublicBruto
                    session["joinedData"] = JoinedData
                    print(ChatsPublicBruto)
                    return render_template("comunidade.html",client=client.profile, chats=ChatsPublicBruto, joinedData=session["joinedData"])
                 else:
                    return render_template("comunidade.html",client=client.profile, chats=session["ChatsPublicBruto"], joinedData=session["joinedData"])
                    
                          
                     
                    
           else:
               return redirect(url_for("catalog"))
           
           
  
  else:
     return redirect(url_for("user"))
 except Exception as e:
     return f"<span>{e}</span>"

@app.route("/user")
def user():
  global client, sub
  sub = None
  session.pop("ChatsPublicBruto", None)
  session.pop("joinedData", None)
  if "Auth" in session:
    if session["Auth"]==200:
       #usersession
     usersession = [session["email"], session["password"]]
     try:
       if client==None:
       #if client None
         DadosSubsClients = [] 
         
         client = amino.Client()
         try:
              if client.login(usersession[0], usersession[1])==200:
                   subs = client.sub_clients()
                   
                   for name, icon, comId, users, keys, created, lang in zip(subs.name, subs.icon, subs.comId, subs.usersCount, subs.customList, subs.createdTime, subs.primaryLanguage):
                          ListPrimary = [name, icon, comId, users, keys, created, lang]
                          DadosSubsClients.append(ListPrimary)
           
                   print(DadosSubsClients)
                   session["DadosSubsClients"] = DadosSubsClients
                   return render_template("perfil.html",client=client.profile, sid=client.sid, subs=session["DadosSubsClients"])
                   
         except Exception as erro:
             return f"<span>{erro}</span>"
         
         
       
       elif client!=None:
       #else Client None               
                 #announ = client.get_ta_announcements(language="pt", start=0, size=12)       
             if "DadosSubsClients" in session:pass
             #pass
              
             else:
                     subs = client.sub_clients()
                     DadosSubsClients = []
                     for name, icon, comId, users, keys, created, lang in zip(subs.name, subs.icon, subs.comId, subs.usersCount, subs.customList, subs.createdTime, subs.primaryLanguage):
                          ListPrimary = [name, icon, comId, users, keys, created, lang]
                          DadosSubsClients.append(ListPrimary)
                     session["DadosSubsClients"] = DadosSubsClients
                     
                     #TA_announ = []
                     #for title, content, blogid, createdtime, viewcount in zip(announ.title, announ.content, announ.blogId, announ.createdTime, announ.viewCount):
             try:
                 return render_template("perfil.html",client=client.profile, sid=client.sid, subs=session["DadosSubsClients"])
             except Exception as erroo:
                 return f"<span>{erroo}</span>"
             
                   
       else:
       #client none?
           return redirect(url_for("logout"))
           
     except Exception as e:
           return f"<span>{e}</span>"
    else:
    #if auth
       return redirect(url_for("logout"))
       
       
  else:
  #if auth session?
     return redirect(url_for("logout"))
     
     
          
     
     
     

if __name__ == '__main__':
    db.create.all()
    app.run(debug=True)
