"use client"

import React from 'react';
import './SideLayout.css';

interface SideLayoutProps {
  contentId: string | null;
  contentType: string | null;
  onRemoveContent: () => void;
}

const SideLayout: React.FC<SideLayoutProps> = ({ contentId, contentType, onRemoveContent }) => {
  return (
    <div className="side-layout">
      <div className="uploaded-content">
        <div className="content-header">
          <h4>Uploaded Content</h4>
          {contentId && (
            <button 
              onClick={onRemoveContent}
              className="remove-button"
              title="Remove content"
            >
              ×
            </button>
          )}
        </div>
        {contentId ? (
          <div className="content-info">
            <p className="content-id">ID: {contentId}</p>
            <p className="content-type">Type: {contentType?.toUpperCase()}</p>
          </div>
        ) : (
          <div className="no-content">
            <p>No content uploaded yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SideLayout;
