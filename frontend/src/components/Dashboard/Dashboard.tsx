"use client"

import type React from "react"
import { useState } from "react"
import Header from "./Header"
import ContentUpload from "./ContentUpload"
import "./Dashboard.css"

const Dashboard: React.FC = () => {
  const [, setHasUploaded] = useState(false)

  const handleContentUpload = () => {
    setHasUploaded(true)
  }


  return (
    <div className="dashboard">
      <Header />

      <div className="dashboard-content">
        <div className="dashboard-main">
          <div className="content-upload-section">
            <ContentUpload 
              onContentUpload={handleContentUpload} 
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
