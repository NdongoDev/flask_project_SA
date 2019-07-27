import psycopg2
import psycopg2.extras
import traceback
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import os

app = Flask(__name__)
app.secret_key = "flash message"
app.secret_key = os.urandom(24)
#connection au DB Postgres
def connectToDB():  
  try:
    return psycopg2.connect(dbname="postgres", user="postgres", password="postgres19", host="localhost")
  except:
    print("Can't connect to database")
    print(traceback.format_exc())
#page login
@app.route("/",  methods=['GET', 'POST'])
def Index():
        if request.method == 'POST':
           session.pop('user', None)
           if request.form['password'] == 'password':
                session['user'] = request.form['username']
                return redirect(url_for('inscription'))
        return render_template('login.html')


#inscription Apprenant
@app.route("/inscription")
def inscription():
    if g.user: 
            
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        cur.execute("SELECT id_apprenant, matricule, prenom, nom, email, date_naissance, adresse, statut, nom_promo FROM apprenant,promotion WHERE apprenant.id_promo=promotion.id_promo and apprenant.statut='inscrit'")
        data = cur.fetchall()
        conn.close()

        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM promotion")
        data1 = cur.fetchall()
        conn.close()

        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT id_apprenant, matricule, prenom, nom, email, date_naissance, adresse, statut, nom_promo FROM apprenant,promotion WHERE apprenant.id_promo=promotion.id_promo and apprenant.statut='annulé' """)
        data2 =cur.fetchall()
        conn.commit()

        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT id_apprenant, matricule, prenom, nom, email, date_naissance, adresse, statut, nom_promo FROM apprenant,promotion WHERE apprenant.id_promo=promotion.id_promo and apprenant.statut='suspendu' """)
        data3 =cur.fetchall()
        conn.commit()
        return render_template('inscription.html', inscription = data, promotion=data1, listeannule=data2, listesuspendu = data3 )
    return redirect(url_for('Index'))

@app.before_request 
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']
        
@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session['user']
    return 'Not logged in!'

@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return 'Dropped Session'

@app.route("/insertapp", methods = ["POST"])
def insertapp():
    if request.method == "POST":
        flash("Inscription reussi")
        prenom = request.form['first_name']
        nom = request.form['last_name']
        email = request.form['email']
        date_naissance = request.form['date_naissance']
        adresse = request.form['adresse']
        statut = request.form['statut'] 
        id_promo = int(request.form["promotion"])

        #verification matricule
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select MAX(id_apprenant) from apprenant""")
        resultat=cur.fetchall()
        conn.cursor()

        for mat in resultat :
                    i =mat[0] 
        date_actu=datetime.datetime.today().strftime("%m%Y")    
                
        if i == None:
            m = 1
            matricule="SA-00"+str(date_actu)+str(m)
        else :
            m = i+1
            matricule = "SA-00"+str(date_actu)+str(m)
        
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = "INSERT INTO apprenant (matricule, prenom, nom, email, date_naissance, adresse, statut, id_promo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        donnee = (matricule, prenom, nom, email, date_naissance, adresse, statut, id_promo)
        try:
            cur.execute(sql, donnee)
            conn.commit()
        except:
            flash("Erreur d'execution de l'insertion")
            print(traceback.format_exc())

        return redirect(url_for('inscription'))
#modifier inscription apprenant
@app.route('/updateIns', methods = ['POST', 'GET'])
def updateIns():
    if request.method == 'POST':
        id_data = request.form['id_app']
        matricule = request.form['matricule']
        prenom = request.form['first_name']
        nom = request.form['last_name']
        email = request.form['email']
        date_naissance = request.form['date_naissance']
        adresse = request.form['adresse']
        id_promo = int(request.form["promotion"])

        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""UPDATE apprenant 
                    SET matricule=%s, prenom=%s, nom = %s, email= %s, date_naissance= %s, adresse = %s, statut='inscrit' , id_promo=%s
                    WHERE id_apprenant = %s 
                    """, (matricule, prenom, nom, email, date_naissance, adresse, id_data, id_promo))
        flash("Donnée MAJ avec succée!")
        conn.commit()
        return redirect(url_for('inscription'))
#action annuler apprennant
@app.route('/annulerins/<string:id_data>',methods= ['POST','GET'])
def  annuler(id_data):
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        flash("Inscription annulé")
        cur.execute("""UPDATE apprenant SET statut='annulé' WHERE id_apprenant =%s""",(id_data,))
        
        conn.commit() 
        
        return redirect(url_for('inscription'))
#action suspendre apprennant
@app.route('/suspendreins/<string:id_data>',methods= ['POST','GET'])
def  suspendreins(id_data):
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        flash("Inscription suspendu")
        cur.execute("""UPDATE apprenant SET statut='suspendu' WHERE id_apprenant =%s""",(id_data,))
        
        conn.commit() 
        
        return redirect(url_for('inscription'))
#action reinscrire
@app.route('/reinscrire/<string:id_data>',methods= ['POST','GET'])
def  reinscrire(id_data):   
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        flash("Réinscription établie avec succés!")
        cur.execute("""UPDATE apprenant SET statut='inscrit' WHERE id_apprenant =%s""",(id_data,))
        
        conn.commit() 
        
        return redirect(url_for('inscription'))

#Sauvegarde referentiel
@app.route("/referentiel",methods= ['GET','POST'])
def referentiel():
        if request.method == 'POST':
                nom_ref=request.form['nom_ref'] 
                
                conn = connectToDB()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
                cur.execute("SELECT * FROM referentiel")
                data = cur.fetchall()
                cur.close()
                conn.commit()
                
                control_ref=False
                for row in data:
                        if row[1].lower() == nom_ref.lower():
                                control_ref =True
                                break
                if control_ref == True  :                    
                        flash("Ce réferentiel existe deja")
                        return  render_template('referentiel.html',referentiel=data)
                else:
                        flash("Ajout réferentiel reussi")
                        cur.execute("INSERT INTO referentiel (nom_ref) VALUES (%s)", (nom_ref,))
                        conn.commit()
                        return  render_template('referentiel.html',referentiel=data)

        return render_template('referentiel.html')

#Modifier referentiel
@app.route('/updateref', methods = ['POST', 'GET'])
def updateref():
    if request.method == 'POST':
        id_data = request.form['id']
        nom_ref = request.form['nom_ref']

        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""UPDATE referentiel 
                    SET nom_ref=%s
                    WHERE id_ref = %s 
                    """, (nom_ref, id_data))
        flash("Donnée MAJ avec succée!")
        conn.commit()
        return redirect(url_for('referentiel'))
    else:
        return render_template('referentiel.html')
#Promotion
@app.route("/promotion", methods = ["GET", "POST"])  
def promotion():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM referentiel")
    data1 = cur.fetchall()
    cur.close()
    conn.commit()

    if request.method == 'POST':     
        nom_promo = request.form['nom_promo']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']
        id_ref = int(request.form['referentiel'])
        
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        cur.execute("SELECT id_promo, nom_promo,date_debut,date_fin, nom_ref FROM promotion,referentiel WHERE promotion.id_ref=referentiel.id_ref")
        data = cur.fetchall()
        cur.close()
        conn.commit()

        control_promo=False
        for row in data:
                if row[1].lower() == nom_promo.lower():
                        control_promo =True
                        break
        if control_promo == True  :                    
                flash("Cette promotion existe deja")
                return  render_template('promotion.html', promotion = data)
        else:
                flash("Ajout promo reussi")
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute("INSERT INTO promotion (nom_promo, date_debut, date_fin, id_ref) VALUES (%s, %s, %s, %s)", (nom_promo, date_debut, date_fin, id_ref,)) 
                conn.commit()
                return  render_template('promotion.html', promotion = data)

    return render_template('promotion.html', referentiel=data1)
                
#modifier promotion
@app.route('/updateprom', methods = ['POST', 'GET'])
def updateprom():
    if request.method == 'POST':
        
        id_data= request.form['id']
        nom_promo = request.form['nom_promo']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']
        ref = request.form['referentiel']
        
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""UPDATE promotion 
                    SET nom_promo=%s, date_debut=%s, date_fin=%s, id_ref=%s
                    WHERE id_promo = %s 
                    """, (nom_promo, date_debut,date_fin, ref, id_data))
        flash("Donnée MAJ avec succée!")
        conn.commit()
        cur.close()
        return redirect(url_for('promotion'))
    else:
        return render_template('promotion.html')




if __name__== "__main__":
    app.run(debug=True)
    