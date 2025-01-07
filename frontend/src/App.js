import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import UrlInput from './components/UrlInput';
import './App.css';

function App() {
  const [result, setResult] = useState(null);

  const handleResult = (data) => {
    setResult(data);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Media Processor</h1>
      </header>
      <main className="container mx-auto p-4">
        <FileUpload onUpload={handleResult} />
        <UrlInput onSubmit={handleResult} />
        {result && (
          <div className="mt-4 p-4 border rounded">
            <h2>Result:</h2>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
