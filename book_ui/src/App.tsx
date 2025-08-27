import { useState } from 'react'
import { sendPrompt } from './api'
import './App.css'

function App() {
  const [userPrompt, setUserPrompt] = useState("")
  const [apiResponse, setResponse] = useState("<Blank>")

  const handleClick = async () => {
    const res = await sendPrompt(userPrompt)
    setResponse(res)
  }

  return (
    <>
      <p>Hii!</p>
      <p>Enter a prompt to send to the API:</p>
      <textarea
        value={userPrompt}
        onChange={e => setUserPrompt(e.target.value)}
        placeholder="Type your prompt here"
        rows={5}
        style={{ width: '100%' }}
      />
      <p>Response: {apiResponse}</p>
      <button onClick={handleClick}>Send Prompt</button>
    </>
  )
}

export default App
