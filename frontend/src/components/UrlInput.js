import React, { useState } from 'react';

const FileUpload = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && (selectedFile.type.startsWith('video/') || selectedFile.type.startsWith('audio/'))) {
      setFile(selectedFile);
    } else {
      alert('Please select a valid video or audio file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      onUpload(data);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded shadow-sm">
      <h2 className="text-lg mb-4">Upload Media File</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="video/*,audio/*"
          onChange={handleFileChange}
          className="mb-4"
        />
        <button
          type="submit"
          disabled={!file || loading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
    </div>
  );
};

export default FileUpload;
