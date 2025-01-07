import React, { useState } from 'react';
import { uploadFile } from '../services/api';

function FileUpload({ onSummaryReceived }) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadFile(file);
      onSummaryReceived(response.summary);
    } catch (err) {
      setError('Failed to upload file: ' + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        accept="audio/*,video/*"
        onChange={handleFileUpload}
        disabled={isUploading}
      />
      {isUploading && <p>Uploading and processing...</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default FileUpload; 