// Este elemento (app.tsx) irá reunir toda a lógica de simulação da sessão.
// O localStorage irá armazenar a identidade do avaliador atual.
// Quando o avaliador mudar, a tela e o estado do React será atualizado.

import React, { useState, useEffect } from 'react';

interface Employee {
  id: number;
  name: string;
  position: string;
}

interface EvaluationData {
  scores: { [key: string]: number };
  weighted_score: number;
  created_at: string;
}

function App() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [currentLeaderId, setCurrentLeaderId] = useState<string>(
    localStorage.getItem('currentLeaderId') || ''
  );
  const [subordinates, setSubordinates] = useState<Employee[]>([]);
  const [selectedSub, setSelectedSub] = useState<Employee | null>(null);
  const [latestEval, setLatestEval] = useState<EvaluationData | null>(null);
  const [scores, setScores] = useState<{ [key: string]: number }>({
    q1: 1, q2: 1, q3: 1, q4: 1, q5: 1, q6: 1
  });
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    fetch('http://localhost:5000/api/employees')
      .then((res) => res.json())
      .then((data) => setEmployees(data));
  }, []);

  useEffect(() => {
    if (currentLeaderId) {
      localStorage.setItem('currentLeaderId', currentLeaderId);
      fetch(`http://localhost:5000/api/subordinates/${currentLeaderId}`)
        .then((res) => res.json())
        .then((data) => {
          setSubordinates(data);
          setSelectedSub(null);
          setLatestEval(null);
        });
    } else {
      setSubordinates([]);
    }
  }, [currentLeaderId]);

  const handleSelectSubordinate = (sub: Employee) => {
    setSelectedSub(sub);
    setMessage('');
    fetch(`http://localhost:5000/api/evaluations/${sub.id}`)
      .then((res) => {
        if (res.ok) return res.json();
        return null;
      })
      .then((data) => {
        setLatestEval(data);
        if (data) {
          setScores(data.scores);
        } else {
          setScores({ q1: 1, q2: 1, q3: 1, q4: 1, q5: 1, q6: 1 });
        }
      });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSub || !currentLeaderId) return;

    fetch('http://localhost:5000/api/evaluations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        evaluator_id: Number(currentLeaderId),
        evaluated_id: selectedSub.id,
        ...scores
      })
    }).then(async (res) => {
      if (res.status === 403) {
        setMessage('Atenção: Este funcionário já foi avaliado nesta semana.');
      } else if (res.ok) {
        setMessage('Avaliação enviada com sucesso!');
        handleSelectSubordinate(selectedSub);
      }
    });
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Plataforma de Avaliação</h1>
      
      <label><strong>Atuar como líder: </strong></label>
      <select 
        value={currentLeaderId} 
        onChange={(e) => setCurrentLeaderId(e.target.value)}
      >
        <option value="">Selecione...</option>
        {employees.map((e) => (
          <option key={e.id} value={e.id}>{e.name} ({e.position})</option>
        ))}
      </select>

      <h2>Equipe Disponível (Hierarquia)</h2>
      <ul>
        {subordinates.map((sub) => (
          <li key={sub.id} style={{ marginBottom: '8px' }}>
            {sub.name} - {sub.position}{' '}
            <button onClick={() => handleSelectSubordinate(sub)}>Selecionar</button>
          </li>
        ))}
      </ul>

      {selectedSub && (
        <div style={{ borderTop: '1px solid #ccc', paddingTop: '15px' }}>
          <h3>Avaliando: {selectedSub.name} (ID: {selectedSub.id})</h3>

          {latestEval && (
            <div style={{ background: '#f9f9f9', padding: '12px', marginBottom: '15px', borderRadius: '4px' }}>
              <h4>Avaliação Registrada</h4>
              <p>Média Ponderada: <strong>{latestEval.weighted_score} / 4.0</strong></p>
              <p>Data: {new Date(latestEval.created_at).toLocaleDateString()}</p>
            </div>
          )}

          {message && <p style={{ color: 'red', fontWeight: 'bold' }}>{message}</p>}

          <form onSubmit={handleSubmit}>
            {[
              { key: 'q1', label: 'Entrega de Resultados (Peso 25%)' },
              { key: 'q2', label: 'Execução e Qualidade do Trabalho (Peso 20%)' },
              { key: 'q3', label: 'Capacidade de Aprendizado e Desenvolvimento (Peso 20%)' },
              { key: 'q4', label: 'Resolução de Problemas e Pensamento Crítico (Peso 15%)' },
              { key: 'q5', label: 'Colaboração, Influência e Liderança (Peso 10%)' },
              { key: 'q6', label: 'Visão Estratégica e Potencial de Crescimento (Peso 10%)' }
            ].map((q) => (
              <div key={q.key} style={{ marginBottom: '10px' }}>
                <label>{q.label}: </label>
                <select
                  value={scores[q.key]}
                  onChange={(e) => setScores({ ...scores, [q.key]: Number(e.target.value) })}
                >
                  {[1, 2, 3, 4].map((n) => (
                    <option key={n} value={n}>{n}</option>
                  ))}
                </select>
              </div>
            ))}
            <button type="submit" style={{ marginTop: '10px' }}>Enviar Avaliação</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
