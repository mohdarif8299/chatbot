"use client"

import type React from "react"
import { useAuth } from "../../context/AuthContext"
import { useNavigate } from "react-router-dom"

const Header: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">EduPlatform</h1>
          <span className="header-subtitle">AI-Powered Learning</span>
        </div>

        <div className="header-right">
          <div className="user-info">
            <span className="user-name">Welcome, {user?.name}</span>
            <div className="user-avatar">{user?.name?.charAt(0).toUpperCase()}</div>
          </div>
          <button onClick={() => {
            logout()
            navigate('/login', { replace: true })
          }} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
