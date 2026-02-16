// import { useState } from 'react'
import './App.css'
import { Recorder } from './components/Recorder'
import './services/SyncManager'

function App() {
  return (
    <div className="app-container">
      <header style={{ padding: '20px', borderBottom: '1px solid #333' }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>VoiceNote Pro</h1>
      </header>
      <main>
        <Recorder />
      </main>
    </div>
  )
}

export default App
