import psycopg2
import psycopg2.extras
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "flash message"
#connection au DB Postgres
def connectToDB():  
  #connectionString = 'dbname=db_Sacademy user=postgres password=postgres19 host=localhost'
  #print(connectionString)
  try:
    return psycopg2.connect(dbname="postgres", user="postgres", password="postgres19", host="localhost")
  except:
    print("Can't connect to database")
    print(traceback.format_exc())
#page login
@app.route("/")
def Index():
    return render_template('login.html')

#inscription Apprenant
@app.route("/inscription")
def inscription():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT id_apprenant, matricule, prenom, nom, email, date_naissance, adresse, statut, nom_promo FROM apprenant,promotion WHERE apprenant.id_promo=promotion.id_promo")
    data = cur.fetchall()
    conn.close()

    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM promotion")
    data1 = cur.fetchall()
    conn.close()
    return render_template('inscription.html', inscription = data, promotion=data1 )

@app.route("/insertapp", methods = ["POST"])
def insertapp():
    if request.method == "POST":
        flash("Inscription reussi")

        matricule = request.form['matricule']
        prenom = request.form['first_name']
        nom = request.form['last_name']
        email = request.form['email']
        date_naissance = request.form['date_naissance']
        adresse = request.form['adresse']
        statut = request.form['statut'] 
        tuteur = request.form['tuteur']
        id_promo = int(request.form["promotion"])
        
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = "INSERT INTO apprenant (matricule, prenom, nom, email, date_naissance, adresse, statut, tuteur, id_promo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        donnee = (matricule, prenom, nom, email, date_naissance, adresse, statut, tuteur, id_promo)
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
        id_data = request.form['id']
        matricule = request.form['matricule']
        prenom = request.form['first_name']
        nom = request.form['last_name']
        email = request.form['email']
        date_naissance = request.form['date_naissance']
        adresse = request.form['adresse']
        statut = request.form['statut']
        tuteur = request.form['tuteur']
        id_promo = int(request.form["promotion"])

        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""UPDATE apprenant 
                    SET matricule=%s, prenom=%s, nom = %s, email= %s, date_naissance= %s, adresse = %s, statut=%s, tuteur = %s, id_promo=%s
                    WHERE id_apprenant = %s 
                    """, (matricule, prenom, nom, email, date_naissance, adresse, statut, tuteur, id_data, id_promo))
        flash("Donnée MAJ avec succée!")
        conn.commit()
        return redirect(url_for('inscription'))
#supprimer apprenant
@app.route('/delete/<string:id_data>', methods = ['POST', 'GET'])
def delete(id_data):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("DELETE FROM apprenant WHERE id_apprenant = %s", (id_data))
    flash("Data Deleted Successfully")
    conn.commit()
    return redirect(url_for('inscription'))

#Sauvegarde referentiel
@app.route("/referentiel")
def referentiel():
    cur = connectToDB()
    cur = cur.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT * FROM referentiel")
    data = cur.fetchall()
    cur.close()
    return render_template('referentiel.html', referentiel = data)

@app.route("/insertref", methods = ["POST"])
def insertref():
    flash("Ajout réferentiel reussi")
    nom_ref = request.form['nom_ref']   
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("INSERT INTO referentiel (nom_ref) VALUES (%s)", (nom_ref,))
    conn.commit()
    return redirect(url_for('referentiel'))
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
@app.route("/promotion")  
def promotion():
    cur = connectToDB()
    cur = cur.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    cur.execute("SELECT id_promo, nom_promo,date_debut,date_fin, nom_ref FROM promotion,referentiel WHERE promotion.id_ref=referentiel.id_ref")
    data = cur.fetchall()
    cur.close()

    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM referentiel")
    data1 = cur.fetchall()
    conn.close()
    return render_template('promotion.html', promotion = data, referentiel=data1 )

@app.route("/insertprom", methods = ["GET", "POST"])
def insertprom():
    
    flash("Ajout promo reussi")
    
    nom_promo = request.form['nom_promo']
    date_debut = request.form['date_debut']
    date_fin = request.form['date_fin']
    id_ref = int(request.form['referentiel'])
        
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("INSERT INTO promotion (nom_promo, date_debut, date_fin, id_ref) VALUES (%s, %s, %s, %s)", (nom_promo, date_debut, date_fin, id_ref,))
        
    conn.commit()
    return redirect(url_for('promotion'))
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
                    """, (nom_promo, date_debut,date_fin,ref, id_data))
        flash("Donnée MAJ avec succée!")
        conn.commit()
        cur.close()
        return redirect(url_for('promotion'))
    else:
        return render_template('promotion.html')



if __name__== "__main__":
    app.run(debug=True)
    