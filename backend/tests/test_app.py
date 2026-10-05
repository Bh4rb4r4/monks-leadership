# O pacote Unittest será usado para organizar os testes da aplicação.
# Para isolar a comunicação (com o banco) será usado a ferramenta/metodo Mock.

import unittest
from unittest.mock import patch
from app import app, calcular_nota_ponderada

class EvaluationTestCase(unittest.TestCase):
    def setUp(self):
        
        # Preparação do cliente de testes do Flask antes de cada execução
        
        self.client = app.test_client()

    def test_weighted_score_calculation(self):
        
        # Validação da função do cálculo da nota final
        # Multiplicação das notas brutas pelos pesos numéricos de cada categoria
        
        score = calcular_nota_ponderada(4, 4, 3, 4, 2, 4)
        self.assertEqual(score, 3.6)

    @patch('app.get_db')
    def test_weekly_limit_rejection(self, mock_db):
        
        # Teste para impedir as avaliações duplicadas
        # Simulação da resposta do banco, onde indica se já existe avaliação recente
        
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = [1]
        
        response = self.client.post('/api/evaluations', json={
            "evaluator_id": 1, "evaluated_id": 2,
            "q1": 4, "q2": 4, "q3": 3, "q4": 4, "q5": 2, "q6": 4
        })
        
        # Confirma que a API retorna o código 403 de acesso negado
        
        self.assertEqual(response.status_code, 403)

    @patch('app.get_db')
    def test_successful_evaluation(self, mock_db):
        
        # Teste do fluxo de sucesso ao enviar um novo formulário
        # Simulator da base de dados, onde confirma zero avaliações nos últimos sete dias
        
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = [0]
        
        response = self.client.post('/api/evaluations', json={
            "evaluator_id": 1, "evaluated_id": 3,
            "q1": 4, "q2": 4, "q3": 4, "q4": 4, "q5": 4, "q6": 4
        })
        
        # Confirmação de que a API retorna o código 201, indicando a criação do registro
        
        self.assertEqual(response.status_code, 201)

    @patch('app.get_db')
    def test_list_employees(self, mock_db):
        
        # Verificação do funcionamento da rota de listagem de todos os perfis
        # Aplica dados fictícios de dois funcionários na resposta da consulta
        
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1, "Alice", "CEO"), (2, "Bob", "CTO")]
        
        response = self.client.get('/api/employees')
        data = response.get_json()
        
        # Valida o status 200 e confirma a leitura correta dos nomes
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], "Alice")

    @patch('app.get_db')
    def test_list_subordinates(self, mock_db):
        
        # Confirma a execução da rota que busca liderados na estrutura de cargos
        # Simula a entrega de um subordinado vinculado ao líder consultado
        
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(2, "Bob", "CTO")]
        
        response = self.client.get('/api/subordinates/1')
        data = response.get_json()
        
        # Validação do recebimento exato de um perfil na lista
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)

    @patch('app.get_db')
    def test_get_latest_evaluation_found(self, mock_db):
        
        # Teste da rota que recupera a avaliação mais recente de um funcionário
        # Aplica uma tupla para simular a linha completa extraída da tabela SQL
        
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1, 1, 2, "2026-10-05 10:00:00", 4, 4, 3, 4, 2, 4)
        
        response = self.client.get('/api/evaluations/2')
        data = response.get_json()
        
        # Confere se o endpoint calcula e entrega a média ponderada corretamente
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['weighted_score'], 3.6)

    @patch('app.get_db')
    def test_get_latest_evaluation_not_found(self, mock_db):
        
        # Confere o comportamento da aplicação quando o funcionário não possui notas
        # Força o retorno vazio do banco de dados
        
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None
        
        response = self.client.get('/api/evaluations/99')
        
        # Confirma a entrega do código 404 de erro de busca
        
        self.assertEqual(response.status_code, 404)
