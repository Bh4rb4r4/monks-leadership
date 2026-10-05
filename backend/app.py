# Utilização do Flask:
# 1) Processamento das rotas REST, CORS e a conexão do PostgreSQL
# 2) Autorização das requisições vindas do Frontend.
# psycopg2 irá executar as instruções SQL no banco de dados.

import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PESOS = {
    'q1': 25,  # Entrega de resultados
    'q2': 20,  # Execução e qualidade do trabalho
    'q3': 20,  # Capacidade de aprendizado e desenvolvimento
    'q4': 15,  # Resolução de problemas e pensamento crítico
    'q5': 10,  # Colaboração, influência e liderança
    'q6': 10   # Visão estratégica e potencial de crescimento
}

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "employeedb"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "adminpassword")
    )

def calcular_nota_ponderada(q1, q2, q3, q4, q5, q6):
    total = (q1 * PESOS['q1']) + (q2 * PESOS['q2']) + (q3 * PESOS['q3']) + \
            (q4 * PESOS['q4']) + (q5 * PESOS['q5']) + (q6 * PESOS['q6'])
    return round(total / 100.0, 2)

@app.route('/api/employees', methods=['GET'])
def list_employees():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, position_name FROM employee ORDER BY name')
    users = [{'id': row[0], 'name': row[1], 'position': row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/subordinates/<int:leader_id>', methods=['GET'])
def list_subordinates(leader_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Busca de subordinados diretos e indiretos através da hierarquia 
    
    cursor.execute('''
        WITH RECURSIVE subordinates AS (
            SELECT lead_id FROM leader_lead WHERE leader_id = %s
            UNION
            SELECT ll.lead_id FROM leader_lead ll
            INNER JOIN subordinates s ON ll.leader_id = s.lead_id
        )
        SELECT e.id, e.name, e.position_name 
        FROM employee e
        JOIN subordinates s ON e.id = s.lead_id
    ''', (leader_id,))
    
    subs = [{'id': r[0], 'name': r[1], 'position': r[2]} for r in cursor.fetchall()]
    conn.close()
    return jsonify(subs)

@app.route('/api/evaluations/<int:evaluated_id>', methods=['GET'])
def get_latest_evaluation(evaluated_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, evaluator_id, evaluated_id, created_at,
               score_resultados, score_execucao, score_aprendizado,
               score_resolucao, score_lideranca, score_estrategia
        FROM evaluation 
        WHERE evaluated_id = %s
        ORDER BY created_at DESC LIMIT 1
    ''', (evaluated_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"message": "Nenhuma avaliação cadastrada"}), 404

    q1, q2, q3, q4, q5, q6 = row[4], row[5], row[6], row[7], row[8], row[9]
    weighted_score = calcular_nota_ponderada(q1, q2, q3, q4, q5, q6)

    return jsonify({
        "id": row[0],
        "evaluator_id": row[1],
        "evaluated_id": row[2],
        "created_at": row[3],
        "scores": {
            "q1": q1, "q2": q2, "q3": q3,
            "q4": q4, "q5": q5, "q6": q6
        },
        "weighted_score": weighted_score
    })

@app.route('/api/evaluations', methods=['POST'])
def save_evaluation():
    data = request.json
    evaluator = data['evaluator_id']
    evaluated = data['evaluated_id']
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Validação da regra de restrição de sete dias
    
    cursor.execute('''
        SELECT count(*) FROM evaluation 
        WHERE evaluator_id = %s AND evaluated_id = %s 
        AND created_at >= CURRENT_DATE - INTERVAL '7 days'
    ''', (evaluator, evaluated))
    
    if cursor.fetchone()[0] > 0:
        conn.close()
        return jsonify({"error": "Funcionário já avaliado nesta semana"}), 403
        
    cursor.execute('''
        INSERT INTO evaluation (
            evaluator_id, evaluated_id, score_resultados, score_execucao, 
            score_aprendizado, score_resolucao, score_lideranca, score_estrategia
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        evaluator, evaluated, data['q1'], data['q2'], 
        data['q3'], data['q4'], data['q5'], data['q6']
    ))
    
    conn.commit()
    conn.close()
    return jsonify({"status": "sucesso"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
