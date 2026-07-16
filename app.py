import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import os
from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Initialize Flask app
server = Flask(__name__)
app = server

# Database path
DATABASE_URL = 'sqlite:///predictions.db'

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Ensure the model is loaded
try:
    model = pickle.load(open('best_model.pkl', 'rb'))
except FileNotFoundError:
    model = None # Handle case where model is not found

# Prediction Model
class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, nullable=False)
    sex = Column(String, nullable=False)
    studytime = Column(Integer, nullable=False)
    higher = Column(String, nullable=False)
    internet = Column(String, nullable=False)
    medu = Column(Integer, nullable=False)
    g1 = Column(Integer, nullable=False)
    g2 = Column(Integer, nullable=False)
    predicted_g3 = Column(Float, nullable=False)
    detailed_interpretation = Column(Text, nullable=False)
    improvement_suggestions = Column(Text, nullable=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Prepare data for Dash app
def prepare_data():
    df1 = pd.read_csv('eleves_liste1.csv')
    df2 = pd.read_excel('eleves_liste2.xlsx')
    df = pd.concat([df1, df2], ignore_index=True)

    # Create a copy for prediction to avoid altering the original dataframe
    predict_df = df.copy()
    predict_df['sex'] = predict_df['sex'].apply(lambda x: 1 if x == 'M' else 0)
    predict_df['higher'] = predict_df['higher'].apply(lambda x: 1 if x == 'yes' else 0)
    predict_df['internet'] = predict_df['internet'].apply(lambda x: 1 if x == 'yes' else 0)

    # Select the features for the model
    features = predict_df[['sex', 'studytime', 'higher', 'internet', 'Medu', 'G1', 'G2']]
    
    if model:
        df['predicted_g3'] = model.predict(features)
    else:
        df['predicted_g3'] = np.random.uniform(0, 20, size=len(df)) # Fallback for no model

    # Define student categories
    def categorize_student(g3):
        if g3 < 10:
            return 'En échec'
        elif 10 <= g3 < 12:
            return 'À risque'
        else:
            return 'Normal'

    df['category'] = df['predicted_g3'].apply(categorize_student)
    return df

data_df = prepare_data()

# Dash App
dash_app = dash.Dash(__name__, server=server, url_base_pathname='/reporting/', external_stylesheets=[dbc.themes.BOOTSTRAP])

# KPIs
kpi_echec = data_df[data_df['category'] == 'En échec'].shape[0]
kpi_risque = data_df[data_df['category'] == 'À risque'].shape[0]
kpi_normal = data_df[data_df['category'] == 'Normal'].shape[0]

dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Tableau de Bord - Performance des Élèves"), className="mb-4 mt-4")
    ]),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Élèves en échec", className="card-title"), html.P(f"{kpi_echec}", className="card-text")])), width=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Élèves à risque", className="card-title"), html.P(f"{kpi_risque}", className="card-text")])), width=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Élèves en situation normale", className="card-title"), html.P(f"{kpi_normal}", className="card-text")])), width=4),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart'), width=6),
        dbc.Col(dcc.Graph(id='pie-chart'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='box-plot'), width=6),
        dbc.Col(dcc.Graph(id='corr-matrix'), width=6)
    ])
], fluid=True)

@dash_app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('box-plot', 'figure'),
     Output('corr-matrix', 'figure')],
    [Input('bar-chart', 'id')] # Dummy input to trigger callback
)
def update_graphs(_):
    category_counts = data_df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']

    # Bar chart with legend and centered title
    bar_fig = px.bar(category_counts, x='category', y='count', title="Répartition des élèves par catégorie", color='category')
    bar_fig.update_layout(title_x=0.5)

    # Pie chart with centered title
    pie_fig = px.pie(category_counts, names='category', values='count', title="Proportion des élèves par catégorie")
    pie_fig.update_layout(title_x=0.5)

    # Box plot with centered title and legend
    box_fig = px.box(data_df, x='category', y='predicted_g3', title="Distribution des notes par catégorie", color='category')
    box_fig.update_layout(title_x=0.5)
    
    # Correlation matrix with centered title
    corr_df = data_df[['studytime', 'Medu', 'G1', 'G2', 'predicted_g3']].corr()
    corr_fig = px.imshow(corr_df, text_auto=True, title="Matrice de corrélation")
    corr_fig.update_layout(title_x=0.5)

    return bar_fig, pie_fig, box_fig, corr_fig

@server.route('/')
def home():
    return render_template('home.html')

@server.route('/prediction')
def prediction_page():
    return render_template('predict.html')

@server.route('/about')
def about_page():
    return render_template('about.html')

@server.route('/history')
def history_page():
    db = next(get_db())
    history = db.query(Prediction).order_by(Prediction.timestamp.desc()).all()
    return render_template('history.html', history=history)

@server.route('/reporting')
def reporting():
    return render_template('reporting.html')

@server.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not found, please train the model first.'}), 500

    db = next(get_db())

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        predictions = []
        for index, row in df.iterrows():
            try:
                data = row.to_dict()
                prediction_result = make_prediction(data)
                predictions.append(prediction_result)
                save_prediction(db, data, prediction_result)
            except Exception as e:
                return jsonify({'error': f'Error processing row {index}: {str(e)}'}), 400
        return jsonify(predictions)

    else:
        try:
            data = request.form.to_dict()
            prediction_result = make_prediction(data)
            save_prediction(db, data, prediction_result)
            return jsonify(prediction_result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400


@server.route('/predict_api', methods=['POST'])
def predict_api():
    if model is None:
        return jsonify({'error': 'Model not found, please train the model first.'}), 500

    db = next(get_db())

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
        
    try:
        prediction_result = make_prediction(data)
        save_prediction(db, data, prediction_result)
        return jsonify(prediction_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def save_prediction(db, data, prediction_result):
    new_prediction = Prediction(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        sex=data['sex'],
        studytime=data['studytime'],
        higher=data['higher'],
        internet=data['internet'],
        medu=data['Medu'],
        g1=data['G1'],
        g2=data['G2'],
        predicted_g3=prediction_result['prediction'],
        detailed_interpretation=prediction_result['detailed_interpretation'],
        improvement_suggestions=json.dumps(prediction_result['improvement_suggestions'])
    )
    db.add(new_prediction)
    db.commit()

def make_prediction(data):
    # Extraction et conversion des données
    sex = data.get('sex')
    studytime_raw = data.get('studytime')
    if studytime_raw is None:
        raise ValueError('Missing studytime field in request.')
    try:
        studytime = int(studytime_raw)
    except (ValueError, TypeError):
        raise ValueError('studytime must be an integer.')
    higher = data.get('higher')
    internet = data.get('internet')
    Medu = int(data.get('Medu'))
    G1 = int(data.get('G1'))
    G2 = int(data.get('G2'))

    # Convert categorical to numerical for prediction
    sex_num = 1 if sex == 'M' else 0
    higher_num = 1 if higher == 'yes' else 0
    internet_num = 1 if internet == 'yes' else 0

    features = [sex_num, studytime, higher_num, internet_num, Medu, G1, G2]
    final_features = [np.array(features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 2)

    # Detailed interpretation and improvement suggestions
    detailed_interpretation = ""
    improvement_suggestions = []

    if output >= 16:
        detailed_interpretation = "Excellent travail ! L'étudiant est sur la bonne voie pour une mention. Ses performances actuelles sont très solides, indiquant une bonne compréhension des matières et une méthode de travail efficace."
        improvement_suggestions.append("Continuer sur cette lancée en explorant des sujets plus avancés ou en aidant d'autres élèves.")
        improvement_suggestions.append("Participer à des projets ou des concours pour approfondir ses connaissances.")
    elif output >= 12:
        detailed_interpretation = "Bonnes performances. L'étudiant a de solides acquis et une base stable. Il montre une bonne capacité à assimiler les informations, mais il y a encore une marge de progression pour atteindre l'excellence."
        improvement_suggestions.append("Identifier les matières où des efforts supplémentaires pourraient être bénéfiques.")
        improvement_suggestions.append("Revoir régulièrement les notions clés et pratiquer des exercices variés.")
        improvement_suggestions.append("Optimiser le temps d'étude en se concentrant sur les points faibles.")
    elif output >= 10:
        detailed_interpretation = "Résultat satisfaisant, mais il y a une marge de progression. L'étudiant maîtrise les bases, mais des lacunes peuvent exister. Un suivi attentif est recommandé pour consolider les acquis et éviter l'accumulation de retards."
        improvement_suggestions.append("Mettre en place un planning de révision structuré.")
        improvement_suggestions.append("Ne pas hésiter à demander de l'aide aux professeurs ou à des camarades pour les points difficiles.")
        improvement_suggestions.append("Améliorer les méthodes de travail et la concentration pendant les cours.")
        if studytime < 3: # Example: if study time is low for this score
            improvement_suggestions.append("Augmenter le temps d'étude hebdomadaire pour renforcer les connaissances.")
    else:
        detailed_interpretation = "Attention, un suivi pédagogique semble nécessaire pour éviter le décrochage. L'étudiant rencontre des difficultés significatives qui nécessitent une intervention rapide et ciblée pour éviter une dégradation des résultats."
        improvement_suggestions.append("Mettre en place un soutien scolaire individualisé ou des cours de rattrapage.")
        improvement_suggestions.append("Identifier les causes profondes des difficultés (méthode de travail, compréhension, motivation).")
        improvement_suggestions.append("Communiquer régulièrement avec l'équipe pédagogique pour un suivi personnalisé.")
        if internet == 'no':
            improvement_suggestions.append("S'assurer d'un accès stable à internet pour les ressources éducatives en ligne.")
        if Medu < 2:
            improvement_suggestions.append("Encourager l'implication des parents dans le suivi scolaire et l'environnement d'apprentissage à la maison.")

    return {
        'prediction': output,
        'detailed_interpretation': detailed_interpretation,
        'improvement_suggestions': improvement_suggestions
    }

if __name__ == "__main__":
    app.run(debug=True)
