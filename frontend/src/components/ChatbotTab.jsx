import { useState } from 'react'
import { Sun, Moon, Bot, User } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'

const ChatbotTab = () => {
  const [theme, setTheme] = useState('light')
  const [selectedColor, setSelectedColor] = useState('#8B5CF6') // Purple default

  const colors = [
    '#8B5CF6', // Purple
    '#EF4444', // Red  
    '#F97316', // Orange
    '#EAB308', // Yellow
    '#22C55E', // Green
    '#06B6D4', // Cyan
    '#3B82F6', // Blue
    '#8B5CF6', // Purple (duplicate for layout)
    '#EC4899'  // Pink
  ]

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme)
  }

  const handleColorChange = (color) => {
    setSelectedColor(color)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left Panel - Customization */}
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Change the colors to customize your bot
          </h2>
        </div>

        {/* Theme Selection */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Theme</h3>
          <div className="flex space-x-4">
            <button
              onClick={() => handleThemeChange('light')}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg border-2 transition-all ${
                theme === 'light' 
                  ? 'border-purple-500 bg-purple-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Sun className="w-5 h-5" />
              <span className="font-medium">Light</span>
            </button>
            <button
              onClick={() => handleThemeChange('dark')}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg border-2 transition-all ${
                theme === 'dark' 
                  ? 'border-purple-500 bg-purple-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <Moon className="w-5 h-5" />
              <span className="font-medium">Dark</span>
            </button>
          </div>
        </div>

        {/* Color Selection */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Color</h3>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">Accent color</p>
            <div className="flex flex-wrap gap-3">
              {colors.map((color, index) => (
                <button
                  key={index}
                  onClick={() => handleColorChange(color)}
                  className={`w-8 h-8 rounded-full border-2 transition-all ${
                    selectedColor === color 
                      ? 'border-gray-400 scale-110' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  style={{ backgroundColor: color }}
                />
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
        </div>
      </div>

      {/* Right Panel - Preview */}
      <div className="space-y-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          {/* Header */}
          <div 
            className="h-12 rounded-t-lg mb-4"
            style={{ backgroundColor: selectedColor }}
          />
          
          {/* Chat Messages */}
          <div className="space-y-4">
            {/* Bot Message */}
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot className="w-4 h-4 text-gray-600" />
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs">
                <p className="text-sm text-gray-800">Bot message here</p>
              </div>
            </div>

            {/* User Message */}
            <div className="flex items-start space-x-3 justify-end">
              <div 
                className="rounded-lg px-4 py-2 max-w-xs text-white"
                style={{ backgroundColor: selectedColor }}
              >
                <p className="text-sm">User message here</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                <User className="w-4 h-4 text-gray-600" />
              </div>
            </div>

            {/* Suggested Reply */}
            <div className="flex justify-center">
              <button 
                className="px-4 py-2 rounded-full border text-sm transition-colors hover:bg-gray-50"
                style={{ 
                  borderColor: selectedColor,
                  color: selectedColor
                }}
              >
                Suggested reply here
              </button>
            </div>
          </div>

          {/* Input Area */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <button 
                className="w-10 h-10 rounded-full text-white flex items-center justify-center"
                style={{ backgroundColor: selectedColor }}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div className="text-center">
          <p className="text-sm text-gray-600 italic">
            Customizing the chatbot UI design in a no-code{' '}
            <span style={{ color: selectedColor }} className="font-medium">
              AI chatbot builder
            </span>
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChatbotTab

