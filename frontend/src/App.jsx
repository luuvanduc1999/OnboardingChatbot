import { useState, useEffect, useRef } from 'react'
import { FaVolumeHigh } from "react-icons/fa6";
import { Home, Users, Settings, Bot, Sun, Moon, Check, ChevronDown } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import './App.css'

function App() {
  const [theme, setTheme] = useState('light')
  const [selectedAccentColor, setSelectedAccentColor] = useState('#8B5CF6') // Purple default
  const [selectedBotColor, setSelectedBotColor] = useState('#22C55E') // Green default
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', text: 'Chào mừng đến với chatbot của nhóm 1' },
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const accentColors = [
    '#8B5CF6', // Purple
    '#A855F7', // Purple variant
    '#EF4444', // Red
    '#F97316', // Orange
    '#EAB308', // Yellow
    '#22C55E', // Green
    '#3B82F6', // Blue
    '#EC4899'  // Pink
  ]

  // Auto scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const playWavAudio = async (text)=>{
    const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
         
        const raw = JSON.stringify({
          "text": text,
        });
         
        const requestOptions = {
          method: "POST",
          headers: myHeaders,
          body: raw,
          redirect: "follow"
        };
         
        let messageRsp
        fetch("http://127.0.0.1:5000/api/tts", requestOptions)
          .then(async (result) => {
            const blob = await result.blob(); // Nhận file dưới dạng blob
            const audioUrl = URL.createObjectURL(blob); // Tạo URL blob
            const audio = new Audio(audioUrl); // Tạo Audio object
            audio.play(); // Phát âm thanh
          })
          .catch((error) => console.error(error));
  }

  const handleSendMessage = async () => {
    if (inputMessage.trim()) {
      const newMessage = {
        id: messages.length + 1,
        type: 'user',
        text: inputMessage
      }
      setMessages([...messages, newMessage])
      setInputMessage('')
      setIsLoading(true)
      
      // Simulate API call to chatbot
      try {
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
         
        const raw = JSON.stringify({
          "question": inputMessage
        });
         
        const requestOptions = {
          method: "POST",
          headers: myHeaders,
          body: raw,
          redirect: "follow"
        };
         
        let messageRsp
        fetch("http://127.0.0.1:5000/api/chatbot", requestOptions)
          .then((response) => response.text())
          .then((result) => 
          setTimeout(() => {
            const botResponse = {
              id: messages.length + 2,
              type: 'bot',
              text: JSON.parse(result)?.response
            }
            setMessages(prev => [...prev, botResponse])
            setIsLoading(false)
          }, 1000))
          .catch((error) => console.error(error));
      } catch (error) {
        console.error('Error sending message:', error)
        const errorResponse = {
          id: messages.length + 2,
          type: 'bot',
          text: 'Xin lỗi, có lỗi xảy ra khi gửi tin nhắn. Vui lòng thử lại.'
        }
        setMessages(prev => [...prev, errorResponse])
        setIsLoading(false)
      }
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <div className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-4 space-y-4">
        <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
          <div className="w-4 h-4 bg-white rounded-sm"></div>
        </div>
        
        <button className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors">
          <Home className="w-5 h-5 text-gray-600" />
        </button>
        
        <button className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors">
          <Users className="w-5 h-5 text-gray-600" />
        </button>
        
        <button className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors">
          <Settings className="w-5 h-5 text-gray-600" />
        </button>
        
        <button className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center border-2 border-purple-500">
          <Bot className="w-5 h-5 text-purple-600" />
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Left Panel - Customization */}
        <div className="w-96 bg-white p-6 space-y-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Change the colors to customize your bot
            </h1>
          </div>

          {/* Theme Selection */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Theme</h3>
            <div className="flex space-x-4">
              <button
                onClick={() => setTheme('light')}
                className={`flex items-center space-x-3 px-6 py-4 rounded-2xl border-2 transition-all relative ${
                  theme === 'light' 
                    ? 'border-purple-500 bg-purple-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Sun className="w-6 h-6 text-purple-600" />
                <span className="font-medium text-gray-900">Light</span>
                {theme === 'light' && (
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}
              </button>
              
              <button
                onClick={() => setTheme('dark')}
                className={`flex items-center space-x-3 px-6 py-4 rounded-2xl border-2 transition-all relative ${
                  theme === 'dark' 
                    ? 'border-purple-500 bg-purple-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Moon className="w-6 h-6 text-purple-600" />
                <span className="font-medium text-gray-900">Dark</span>
                {theme === 'dark' && (
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Color Selection */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Color</h3>
            
            {/* Accent Color */}
            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-3">Accent color</p>
              <div className="flex flex-wrap gap-3 mb-4">
                {accentColors.map((color, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedAccentColor(color)}
                    className={`w-10 h-10 rounded-full border-2 transition-all relative ${
                      selectedAccentColor === color 
                        ? 'border-gray-400 scale-110' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    style={{ backgroundColor: color }}
                  >
                    {selectedAccentColor === color && (
                      <div className="absolute inset-0 rounded-full flex items-center justify-center">
                        <Check className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
              <div className="flex items-center space-x-2">
                <div 
                  className="w-6 h-6 rounded-full border border-gray-300"
                  style={{ 
                    background: `conic-gradient(from 0deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000)`
                  }}
                />
                <span className="text-sm text-gray-600">Custom color</span>
              </div>
            </div>

            {/* Bot Messages Color */}
            <div>
              <p className="text-sm text-gray-600 mb-3">Bot messages</p>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setSelectedBotColor('#22C55E')}
                  className={`w-10 h-10 rounded-full border-2 transition-all relative ${
                    selectedBotColor === '#22C55E' 
                      ? 'border-gray-400 scale-110' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  style={{ backgroundColor: '#22C55E' }}
                >
                  {selectedBotColor === '#22C55E' && (
                    <div className="absolute inset-0 rounded-full flex items-center justify-center">
                      <Check className="w-5 h-5 text-white" />
                    </div>
                  )}
                </button>
                <div 
                  className="w-6 h-6 rounded-full border border-gray-300"
                  style={{ 
                    background: `conic-gradient(from 0deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000)`
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Chat Preview */}
        <div className="flex-1 p-6 flex flex-col">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 flex-1 flex flex-col overflow-hidden">
            {/* Chat Header */}
            <div 
              className="h-16 flex items-center px-4"
              style={{ backgroundColor: selectedAccentColor }}
            />
            
            {/* Chat Messages */}
            <div className="flex-1 p-6 space-y-4 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
              {messages.map((message) => (
                <div key={message.id} className={`flex items-start space-x-3 ${message.type === 'user' ? 'justify-end' : ''}`}>
                  {message.type === 'bot' && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                  
                  <div 
                    className={`rounded-2xl px-4 py-3 max-w-xs ${
                      message.type === 'bot' 
                        ? 'bg-gray-100 text-gray-800' 
                        : 'text-white'
                    }`}
                    style={message.type === 'user' ? { backgroundColor: selectedAccentColor } : {}}
                  >
                    <p className="text-sm">{message.text}{message.type ==='bot' && (<FaVolumeHigh onClick={()=>playWavAudio(message.text)}/>)}</p>
                  </div>
                  
                  {message.type === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center flex-shrink-0">
                      <div className="w-4 h-4 bg-gray-600 rounded-full" />
                    </div>
                  )}
                </div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-gray-600" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-4 py-3 max-w-xs">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}

              {/* Suggested Reply */}
              <div className="flex justify-center">
                <button 
                  className="px-6 py-3 rounded-full border-2 text-sm font-medium transition-colors hover:bg-gray-50"
                  style={{ 
                    borderColor: selectedBotColor,
                    color: selectedBotColor
                  }}
                >
                  Suggested reply here
                </button>
              </div>

              {/* Invisible element for auto-scroll */}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-6 border-t border-gray-200">
              <div className="flex items-center space-x-3">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50"
                />
                <button 
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="w-12 h-12 rounded-full text-white flex items-center justify-center hover:opacity-90 transition-opacity disabled:opacity-50"
                  style={{ backgroundColor: selectedAccentColor }}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Bottom Text */}
          <div className="text-center mt-4">
            <p className="text-sm text-gray-600 italic">
              Customizing the chatbot UI design in a no-code{' '}
              <span style={{ color: selectedAccentColor }} className="font-medium">
                AI chatbot builder
              </span>
            </p>
          </div>

          {/* Floating Action Button */}
          <div className="fixed bottom-8 right-8">
            <button 
              onClick={scrollToBottom}
              className="w-14 h-14 rounded-full text-white shadow-lg flex items-center justify-center hover:scale-105 transition-transform"
              style={{ backgroundColor: selectedBotColor }}
            >
              <ChevronDown className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App