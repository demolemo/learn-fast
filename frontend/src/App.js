import React from 'react';
import FileUpload from './components/FileUpload';
import Summary from './components/Summary';
import './App.css';

function App() {
  const [summary, setSummary] = React.useState(null);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Media Summarizer</h1>
      </header>
      <main>
        <FileUpload onSummaryReceived={setSummary} />
        {summary && <Summary content={summary} />}
      </main>
    </div>
  );
}

export default App; 