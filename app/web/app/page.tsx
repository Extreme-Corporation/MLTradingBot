const stats = {
  balance: 1000.0,
  winrate: 0.58,
  trades: 42,
  pnl: 120.5
};

export default function Dashboard() {
  return (
    <main className="page">
      <header className="header">
        <div>
          <h1>IQ Option Bot</h1>
          <p>Dashboard em tempo real (mock)</p>
        </div>
        <button className="primary">Iniciar sessão</button>
      </header>

      <section className="grid">
        <div className="card">
          <h2>Saldo simulado</h2>
          <p>${stats.balance.toFixed(2)}</p>
        </div>
        <div className="card">
          <h2>Winrate</h2>
          <p>{(stats.winrate * 100).toFixed(1)}%</p>
        </div>
        <div className="card">
          <h2>Trades</h2>
          <p>{stats.trades}</p>
        </div>
        <div className="card">
          <h2>PNL diário</h2>
          <p>${stats.pnl.toFixed(2)}</p>
        </div>
      </section>

      <section className="panel">
        <h3>Operações recentes</h3>
        <table>
          <thead>
            <tr>
              <th>Par</th>
              <th>Direção</th>
              <th>Valor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>EURUSD</td>
              <td>CALL</td>
              <td>$20</td>
              <td>WIN</td>
            </tr>
            <tr>
              <td>EURUSD</td>
              <td>PUT</td>
              <td>$20</td>
              <td>LOSS</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  );
}
