import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { MessageCircle, MapPin, FileText, Upload, Bot, Users, Briefcase, FileCheck } from 'lucide-react'
import ChatbotInterface from './components/ChatbotInterface.jsx'
import RoadmapGenerator from './components/RoadmapGenerator.jsx'
import ContentGenerator from './components/ContentGenerator.jsx'
import DocumentExtractor from './components/DocumentExtractor.jsx'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('chatbot')

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-3">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Chatbot Onboarding
                  </h1>
                  <p className="text-sm text-gray-600">Hệ thống hỗ trợ nhân viên mới</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1 text-sm text-gray-600">
                  <Users className="h-4 w-4" />
                  <span>Phiên bản mở rộng</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Chào mừng đến với hệ thống Onboarding thông minh
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Trải nghiệm onboarding hoàn toàn mới với AI - từ tư vấn cá nhân hóa đến xử lý tài liệu tự động
            </p>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-2 hover:border-blue-300"
                  onClick={() => setActiveTab('chatbot')}>
              <CardHeader className="text-center">
                <div className="mx-auto bg-blue-100 p-3 rounded-full w-fit group-hover:bg-blue-200 transition-colors">
                  <MessageCircle className="h-8 w-8 text-blue-600" />
                </div>
                <CardTitle className="text-lg">Chatbot AI</CardTitle>
                <CardDescription>
                  Hỏi đáp thông minh về chính sách, quy trình và phúc lợi
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-2 hover:border-green-300"
                  onClick={() => setActiveTab('roadmap')}>
              <CardHeader className="text-center">
                <div className="mx-auto bg-green-100 p-3 rounded-full w-fit group-hover:bg-green-200 transition-colors">
                  <MapPin className="h-8 w-8 text-green-600" />
                </div>
                <CardTitle className="text-lg">Lộ trình cá nhân</CardTitle>
                <CardDescription>
                  Tạo lộ trình onboarding phù hợp với vị trí công việc
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-2 hover:border-purple-300"
                  onClick={() => setActiveTab('content')}>
              <CardHeader className="text-center">
                <div className="mx-auto bg-purple-100 p-3 rounded-full w-fit group-hover:bg-purple-200 transition-colors">
                  <FileText className="h-8 w-8 text-purple-600" />
                </div>
                <CardTitle className="text-lg">Tạo nội dung</CardTitle>
                <CardDescription>
                  Tự động soạn email, tóm tắt tài liệu và tạo câu hỏi
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-2 hover:border-orange-300"
                  onClick={() => setActiveTab('extract')}>
              <CardHeader className="text-center">
                <div className="mx-auto bg-orange-100 p-3 rounded-full w-fit group-hover:bg-orange-200 transition-colors">
                  <Upload className="h-8 w-8 text-orange-600" />
                </div>
                <CardTitle className="text-lg">Xử lý tài liệu</CardTitle>
                <CardDescription>
                  Trích xuất thông tin từ CV và tự động điền biểu mẫu
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          {/* Main Interface */}
          <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
            <CardContent className="p-0">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-4 bg-gray-50 p-1 rounded-t-lg">
                  <TabsTrigger value="chatbot" className="flex items-center space-x-2">
                    <MessageCircle className="h-4 w-4" />
                    <span className="hidden sm:inline">Chatbot</span>
                  </TabsTrigger>
                  <TabsTrigger value="roadmap" className="flex items-center space-x-2">
                    <MapPin className="h-4 w-4" />
                    <span className="hidden sm:inline">Lộ trình</span>
                  </TabsTrigger>
                  <TabsTrigger value="content" className="flex items-center space-x-2">
                    <FileText className="h-4 w-4" />
                    <span className="hidden sm:inline">Nội dung</span>
                  </TabsTrigger>
                  <TabsTrigger value="extract" className="flex items-center space-x-2">
                    <Upload className="h-4 w-4" />
                    <span className="hidden sm:inline">Tài liệu</span>
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="chatbot" className="p-6">
                  <ChatbotInterface />
                </TabsContent>

                <TabsContent value="roadmap" className="p-6">
                  <RoadmapGenerator />
                </TabsContent>

                <TabsContent value="content" className="p-6">
                  <ContentGenerator />
                </TabsContent>

                <TabsContent value="extract" className="p-6">
                  <DocumentExtractor />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Footer */}
          <footer className="mt-12 text-center text-gray-600">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <div className="flex items-center space-x-2">
                <Briefcase className="h-4 w-4" />
                <span className="text-sm">Onboarding thông minh</span>
              </div>
              <div className="flex items-center space-x-2">
                <FileCheck className="h-4 w-4" />
                <span className="text-sm">Xử lý tự động</span>
              </div>
              <div className="flex items-center space-x-2">
                <Bot className="h-4 w-4" />
                <span className="text-sm">AI hỗ trợ 24/7</span>
              </div>
            </div>
            <p className="text-sm">
              © 2024 Chatbot Onboarding System. Được phát triển với ❤️ để hỗ trợ nhân viên mới.
            </p>
          </footer>
        </main>
      </div>
    </Router>
  )
}

export default App

