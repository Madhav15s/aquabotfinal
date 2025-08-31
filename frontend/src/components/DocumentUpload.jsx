import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './DocumentUpload.css';

const DocumentUpload = ({ onUpload, onClose }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFiles = (files) => {
    const validFiles = Array.from(files).filter(file => {
      const validTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ];
      
      return validTypes.includes(file.type) || file.name.endsWith('.pdf') || file.name.endsWith('.doc') || 
             file.name.endsWith('.docx') || file.name.endsWith('.txt') || file.name.endsWith('.xls') || 
             file.name.endsWith('.xlsx');
    });

    if (validFiles.length === 0) {
      alert('Please upload valid document files (PDF, DOC, DOCX, TXT, XLS, XLSX)');
      return;
    }

    setUploadedFiles(prev => [...prev, ...validFiles]);
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const processDocuments = async () => {
    if (uploadedFiles.length === 0) return;

    setIsProcessing(true);
    setUploadProgress(0);

    try {
      const documents = [];
      
      for (let i = 0; i < uploadedFiles.length; i++) {
        const file = uploadedFiles[i];
        setUploadProgress((i / uploadedFiles.length) * 100);

        // Simulate document processing
        await new Promise(resolve => setTimeout(resolve, 500));

        // Extract text content (in real implementation, use OCR or text extraction)
        const content = await extractTextFromFile(file);
        
        documents.push({
          name: file.name,
          type: file.type || 'unknown',
          size: file.size,
          content: content,
          uploadTime: new Date().toISOString()
        });
      }

      setUploadProgress(100);
      
      // Simulate AI analysis delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      onUpload(documents);
      
    } catch (error) {
      console.error('Error processing documents:', error);
      alert('Error processing documents. Please try again.');
    } finally {
      setIsProcessing(false);
      setUploadProgress(0);
    }
  };

  const extractTextFromFile = async (file) => {
    // Simulate text extraction based on file type
    if (file.type === 'text/plain') {
      return await file.text();
    } else if (file.type === 'application/pdf') {
      // Simulate PDF text extraction
      return `PDF Document: ${file.name}\n\nExtracted content would include:\n- Charter party terms\n- Laytime clauses\n- Freight rates\n- Port costs\n- Vessel specifications\n- Route details\n- Insurance terms`;
    } else if (file.type.includes('word') || file.type.includes('document')) {
      // Simulate Word document text extraction
      return `Word Document: ${file.name}\n\nExtracted content would include:\n- Contract terms\n- Commercial clauses\n- Technical specifications\n- Financial details\n- Operational procedures`;
    } else if (file.type.includes('excel') || file.type.includes('spreadsheet')) {
      // Simulate Excel document text extraction
      return `Excel Document: ${file.name}\n\nExtracted content would include:\n- Cost breakdowns\n- Financial calculations\n- Data tables\n- Charts and graphs\n- Statistical information`;
    } else {
      return `Document: ${file.name}\n\nContent extracted and ready for AI analysis.`;
    }
  };

  const getFileIcon = (fileName) => {
    if (fileName.endsWith('.pdf')) return '📄';
    if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) return '📝';
    if (fileName.endsWith('.txt')) return '📃';
    if (fileName.endsWith('.xls') || fileName.endsWith('.xlsx')) return '📊';
    return '📄';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <motion.div
      className="document-upload"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
    >
      <div className="upload-header">
        <h2>📄 Upload Maritime Documents</h2>
        <p>Upload charter parties, voyage orders, and other maritime documents for AI analysis</p>
        <button className="close-button" onClick={onClose}>×</button>
      </div>

      <div className="upload-content">
        {/* Drag & Drop Area */}
        <div
          className={`drag-drop-area ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="drag-content">
            <div className="drag-icon">📁</div>
            <h3>Drag & Drop Documents Here</h3>
            <p>or click to browse files</p>
            <p className="supported-formats">
              Supported formats: PDF, DOC, DOCX, TXT, XLS, XLSX
            </p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <motion.div
            className="uploaded-files"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h3>Selected Documents ({uploadedFiles.length})</h3>
            <div className="files-list">
              {uploadedFiles.map((file, index) => (
                <motion.div
                  key={index}
                  className="file-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <div className="file-info">
                    <span className="file-icon">{getFileIcon(file.name)}</span>
                    <div className="file-details">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{formatFileSize(file.size)}</span>
                    </div>
                  </div>
                  <button
                    className="remove-file-btn"
                    onClick={() => removeFile(index)}
                    title="Remove file"
                  >
                    ×
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Upload Progress */}
        <AnimatePresence>
          {isProcessing && (
            <motion.div
              className="upload-progress"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="progress-header">
                <span>Processing Documents...</span>
                <span className="progress-percentage">{Math.round(uploadProgress)}%</span>
              </div>
              <div className="progress-bar">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action Buttons */}
        <div className="upload-actions">
          <button
            className="cancel-btn"
            onClick={onClose}
            disabled={isProcessing}
          >
            Cancel
          </button>
          <button
            className="upload-btn"
            onClick={processDocuments}
            disabled={uploadedFiles.length === 0 || isProcessing}
          >
            {isProcessing ? 'Processing...' : `Process ${uploadedFiles.length} Document${uploadedFiles.length !== 1 ? 's' : ''}`}
          </button>
        </div>
      </div>

      {/* Document Analysis Preview */}
      {uploadedFiles.length > 0 && !isProcessing && (
        <motion.div
          className="analysis-preview"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h3>🔍 AI Analysis Preview</h3>
          <p>After processing, I'll be able to:</p>
          <ul>
            <li>📋 Extract key terms and conditions</li>
            <li>⏰ Analyze laytime clauses and demurrage</li>
            <li>💰 Calculate voyage costs and profitability</li>
            <li>📊 Identify commercial risks and opportunities</li>
            <li>🚢 Suggest route optimizations</li>
            <li>📝 Generate compliance reports</li>
          </ul>
        </motion.div>
      )}
    </motion.div>
  );
};

export default DocumentUpload; 