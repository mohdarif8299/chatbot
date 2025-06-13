"use client"

import React, { useState, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import QuestionInterface from './QuestionInterface';
import './ContentUpload.css';

interface ContentUploadProps {
  onContentUpload: (contentId: string) => void
}

const ContentUpload: React.FC<ContentUploadProps> = ({ onContentUpload }) => {
  useAuth();
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [uploadedFileType, setUploadedFileType] = useState<string | null>(null);
  const [showQuestionInterface, setShowQuestionInterface] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleContentUpload = (content: string) => {
    onContentUpload(content);
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files).slice(0, 1);
    handleFiles(files);
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).slice(0, 1);
    handleFiles(files);
  }

  const handleFiles = async (files: File[]) => {
    setError("");
    setLoading(true);

    try {
      const file = files[0];
      if (!file) {
        setError("No file selected.");
        return;
      }

      const fileName = file.name.toLowerCase();
      const fileExtension = fileName.split('.').pop();

      if (fileExtension === "pdf" || fileExtension === "docx") {
        const formData = new FormData();
        formData.append('file', file, file.name);

        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/content/upload`, {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || 'Failed to process file. Please check server logs.');
        }

        const data = await response.json();
        console.log('Upload response:', data);

        const contentId = data.data?.content_id || data.content_id;
        if (!contentId) {
          throw new Error('No content_id received from server');
        }

        setUploadedFile(contentId);
        setUploadedFileType(fileExtension);
        setShowQuestionInterface(true);
        handleContentUpload(contentId);
      } else {
        setError(`Unsupported file type: ${file.name}. Please upload PDF or DOCX files only.`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process file. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setUploadedFileType(null);
    setShowQuestionInterface(false);
    handleContentUpload('');
  };

  return (
    <div className="content-upload">
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title">
            <div className="sidebar-icon">📄</div>
            <div>
              <h2>Document Hub</h2>
              <p className="sidebar-subtitle">Manage your uploads</p>
            </div>
          </div>
        </div>
        
        <div className="files-section">
          <div className="files-header">
            <h3>Uploaded Files</h3>
            {uploadedFile && (
              <span className="file-count-badge">1 file</span>
            )}
          </div>
          
          <ul className="file-list">
            {uploadedFile ? (
              <li className="file-item">
                <div className="file-icon">📄</div>
                <div className="file-info">
                  <div className="file-name">{uploadedFile}</div>
                  <div className="file-type">
                    {uploadedFileType === "pdf" ? "PDF Document" : "Word Document"}
                  </div>
                </div>
                <button className="remove-btn" onClick={handleRemoveFile}>×</button>
              </li>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📁</div>
                <p className="empty-text">No files uploaded yet</p>
              </div>
            )}
          </ul>
        </div>
      </div>

      <div className="main-content">
        <div className="upload-section">
          <div
            className={`drop-zone ${isDragging ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileSelect}
              ref={fileInputRef}
              id="fileInput"
            />
            
            {loading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p className="loading-text">Processing your file...</p>
                <p className="loading-subtext">This may take a few moments</p>
              </div>
            ) : (
              <div className="drop-zone-content">
                <button
                  className="select-btn"
                  onClick={() => fileInputRef.current?.click()}
                >
                  📁 Drag or Select PDF/DOCX File
                </button>
                <p className="file-info-text">Supported formats: PDF, DOCX (max 10MB)</p>
              </div>
            )}
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">❌</span>
              <div className="error-content">
                <h4>Error</h4>
                <p>{error}</p>
              </div>
            </div>
          )}
        </div>

        {showQuestionInterface && uploadedFile && (
          <div className="question-interface">
            <QuestionInterface 
              uploadedContent={uploadedFile} 
              onContentUpload={handleContentUpload} 
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentUpload;