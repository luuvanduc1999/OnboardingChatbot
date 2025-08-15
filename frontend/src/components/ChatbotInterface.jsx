import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Send, Bot, User, Loader2, MessageSquare, Lightbulb, Volume2, VolumeX } from 'lucide-react'

const ChatbotInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Xin chào! Tôi là chatbot hỗ trợ onboarding. Tôi có thể giúp bạn:\n\n🎯 Tạo lộ trình onboarding cá nhân hóa\n📧 Tạo nội dung tự động (email, tóm tắt, câu hỏi)\n🔍 Trích xuất thông tin từ tài liệu\n❓ Trả lời câu hỏi về chính sách công ty\n\nHãy thử hỏi "help" để xem hướng dẫn chi tiết!',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const endOfMessagesRef = useRef(null)

  // TTS state
  const [playingId, setPlayingId] = useState(null)
  const audioRef = useRef(null)

  // Dynamic suggested questions
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    "Tạo lộ trình cho developer",
    "Chính sách nghỉ phép như thế nào?",
    "Tạo email chào mừng",
    "Xử lý CV",
    "help"
  ])

  const getFrontendSuggestions = (history) => {
    const lastUserMsg = history.filter(m => m.type === 'user').slice(-1)[0]?.content?.toLowerCase() || '';
    if (!lastUserMsg) return [];
    const suggestions = [];
    if (lastUserMsg.includes('developer') || lastUserMsg.includes('lộ trình')) {
      suggestions.push('Gợi ý học tập cho developer');
      suggestions.push('Các kỹ năng cần cho developer mới');
    }
    if (lastUserMsg.includes('email')) {
      suggestions.push('Tạo email chào mừng');
      suggestions.push('Tạo email nhắc nhở onboarding');
    }
    if (lastUserMsg.includes('cv') || lastUserMsg.includes('hồ sơ')) {
      suggestions.push('Xử lý CV');
      suggestions.push('Tự động điền biểu mẫu từ CV');
    }
    if (lastUserMsg.includes('chính sách')) {
      suggestions.push('Chính sách nghỉ phép như thế nào?');
      suggestions.push('Chính sách thưởng/phạt');
    }
    if (suggestions.length === 0) {
      suggestions.push('help');
    }
    return suggestions;
  };

  const fetchBackendSuggestions = async (history) => {
    const userQuestions = history.filter(m => m.type === 'user').map(m => m.content);
    try {
      const response = await fetch('http://127.0.0.1:5001/api/chatbot/suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ history: userQuestions })
      });
      if (response.ok) {
        const data = await response.json();
        return Array.isArray(data.suggestions) ? data.suggestions : [];
      }
    } catch (e) {}
    return [];
  };

  useEffect(() => {
    const updateSuggestions = async () => {
      const userQuestions = messages.filter(m => m.type === 'user');
      if (userQuestions.length === 0) {
        setSuggestedQuestions([
          "Tạo lộ trình cho developer",
          "Chính sách nghỉ phép như thế nào?",
          "Tạo email chào mừng",
          "Xử lý CV",
          "help"
        ]);
        return;
      }
      const frontend = getFrontendSuggestions(messages);
      const backend = await fetchBackendSuggestions(messages);

      let processedBackend = [];
      backend.forEach(item => {
        if (typeof item === 'string') {
          try {
            const arr = JSON.parse(item);
            if (Array.isArray(arr)) {
              processedBackend.push(...arr);
            } else {
              processedBackend.push(item);
            }
          } catch {
            const split = item.split(/\n|\r|\d+\.\s+/).map(s => s.trim()).filter(Boolean);
            if (split.length > 1) {
              processedBackend.push(...split);
            } else {
              processedBackend.push(item);
            }
          }
        } else {
          processedBackend.push(item);
        }
      });

      const merged = Array.from(new Set([
        ...frontend,
        ...processedBackend.filter(item => {
          if (typeof item !== 'string') return true;
          const trimmed = item.trim().toLowerCase();
          if (trimmed === '[ ]' || trimmed === '[]') return false;
          if (trimmed.includes('json')) return false;
          if (trimmed.includes('[')) return false;
          if (trimmed.includes(']')) return false;
          if (trimmed.includes('```')) return false;
          return true;
        })
      ]));

      const limited = merged.slice(0, 3);
      setSuggestedQuestions(limited.length ? limited : [
        "Tạo lộ trình cho developer",
        "Chính sách nghỉ phép như thế nào?",
        "Tạo email chào mừng",
        "Xử lý CV",
        "help"
      ]);
    };
    updateSuggestions();
  }, [messages]);

  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const sendMessage = async (message = inputValue) => {
    if (!message.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:5001/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: message }),
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const data = await response.json()
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response || 'Xin lỗi, tôi không thể xử lý yêu cầu này lúc này.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Xin lỗi, có lỗi xảy ra khi kết nối với server. Vui lòng thử lại sau.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatMessage = (content) => {
    return content.split('\n').map((line, index) => (
      <span key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </span>
    ))
  }

  const handlePlayTTS = async (message) => {
    if (playingId === message.id) {
      audioRef.current?.pause()
      audioRef.current = null
      setPlayingId(null)
      return
    }

    try {
      setPlayingId(message.id)
      const res = await fetch("http://127.0.0.1:5001/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message.content })
      })
      if (!res.ok) throw new Error("TTS API error")
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)

      if (audioRef.current) {
        audioRef.current.pause()
      }
      audioRef.current = new Audio(url)
      audioRef.current.play()

      audioRef.current.onended = () => {
        setPlayingId(null)
        audioRef.current = null
      }
    } catch (err) {
      console.error("TTS error:", err)
      setPlayingId(null)
    }
  }

  return (
    <div className="h-[600px] flex flex-col">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center space-x-2">
          <MessageSquare className="h-5 w-5 text-blue-600" />
          <span>Chatbot AI Hỗ trợ Onboarding</span>
        </CardTitle>
        <CardDescription>
          Hỏi đáp thông minh về chính sách, quy trình và các chức năng mới
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col space-y-4 overflow-hidden">
        <div className="flex flex-col gap-2">
          <div className="flex items-center space-x-2 text-sm text-gray-600 mb-2">
            <Lightbulb className="h-4 w-4" />
            <span>Gợi ý câu hỏi:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, index) => {
              let clean = question;
              if (typeof clean === 'string') {
                clean = clean.trim();
                clean = clean.replace(/,$/, '').trim();
                while (clean.startsWith('"')) clean = clean.slice(1);
                while (clean.endsWith('"')) clean = clean.slice(0, -1);
              }
              return (
                <Badge
                  key={index}
                  variant="outline"
                  className="cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-colors px-3 py-2 text-base"
                  onClick={() => sendMessage(clean)}
                >
                  {clean}
                </Badge>
              );
            })}
          </div>
        </div>

        <div className="flex-1 min-h-0">
          <ScrollArea className="h-full pr-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {message.type === 'bot' && (
                        <Bot className="h-4 w-4 mt-1 text-blue-600" />
                      )}
                      {message.type === 'user' && (
                        <User className="h-4 w-4 mt-1 text-white" />
                      )}
                      <div className="flex-1">
                        <div className="text-sm font-medium mb-1 flex items-center justify-between">
                          <span>{message.type === 'bot' ? 'Chatbot' : 'Bạn'}</span>
                          {message.type === 'bot' && (
                            <button
                              onClick={() => handlePlayTTS(message)}
                              className="ml-2 text-blue-600 hover:text-blue-800"
                              title={playingId === message.id ? "Phát âm thanh" : "Dừng phát"}
                            >
                              {playingId === message.id ? (
                                <Volume2 className="h-4 w-4" />
                              ) : (
                                <VolumeX className="h-4 w-4" />
                              )}
                            </button>
                          )}
                        </div>
                        <div className="text-sm leading-relaxed">
                          {formatMessage(message.content)}
                        </div>
                        <div className={`text-xs mt-2 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.timestamp.toLocaleTimeString('vi-VN')}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-4 w-4 text-blue-600" />
                      <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                        <span className="text-sm text-gray-600">Đang xử lý...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={endOfMessagesRef} />
            </div>
          </ScrollArea>
        </div>

        <div className="flex space-x-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Nhập câu hỏi của bạn..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={() => sendMessage()}
            disabled={isLoading || !inputValue.trim()}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </div>
  )
}

export default ChatbotInterface