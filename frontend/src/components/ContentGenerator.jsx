import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { FileText, Mail, HelpCircle, CheckSquare, Loader2, Copy, Download } from 'lucide-react'

const ContentGenerator = () => {
  const [activeContentTab, setActiveContentTab] = useState('email')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState({})

  // Email form state
  const [emailForm, setEmailForm] = useState({
    employee_name: '',
    company_name: '',
    position: '',
    start_date: '',
    department: '',
    manager_name: ''
  })

  // Summary form state
  const [summaryForm, setSummaryForm] = useState({
    document_text: '',
    summary_type: 'general'
  })

  // Questions form state
  const [questionsForm, setQuestionsForm] = useState({
    content: '',
    question_type: 'mixed',
    num_questions: 5
  })

  // Checklist form state
  const [checklistForm, setChecklistForm] = useState({
    position: '',
    department: ''
  })

  const summaryTypes = [
    { value: 'general', label: 'Tóm tắt tổng quan' },
    { value: 'key_points', label: 'Điểm chính' },
    { value: 'action_items', label: 'Hành động cần thực hiện' }
  ]

  const questionTypes = [
    { value: 'mixed', label: 'Hỗn hợp' },
    { value: 'multiple_choice', label: 'Trắc nghiệm' },
    { value: 'true_false', label: 'Đúng/Sai' }
  ]

  const generateWelcomeEmail = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/content/welcome-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ employee_info: emailForm }),
      })

      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setResults(prev => ({ ...prev, email: data.email }))
    } catch (error) {
      console.error('Error:', error)
      setResults(prev => ({ ...prev, email: { error: 'Có lỗi xảy ra khi tạo email' } }))
    } finally {
      setIsLoading(false)
    }
  }

  const generateSummary = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/content/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(summaryForm),
      })

      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setResults(prev => ({ ...prev, summary: data }))
    } catch (error) {
      console.error('Error:', error)
      setResults(prev => ({ ...prev, summary: { error: 'Có lỗi xảy ra khi tóm tắt tài liệu' } }))
    } finally {
      setIsLoading(false)
    }
  }

  const generateQuestions = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/content/training-questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(questionsForm),
      })

      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setResults(prev => ({ ...prev, questions: data }))
    } catch (error) {
      console.error('Error:', error)
      setResults(prev => ({ ...prev, questions: { error: 'Có lỗi xảy ra khi tạo câu hỏi' } }))
    } finally {
      setIsLoading(false)
    }
  }

  const generateChecklist = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/content/onboarding-checklist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(checklistForm),
      })

      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setResults(prev => ({ ...prev, checklist: data }))
    } catch (error) {
      console.error('Error:', error)
      setResults(prev => ({ ...prev, checklist: { error: 'Có lỗi xảy ra khi tạo checklist' } }))
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  const formatEmail = (email) => {
    if (email.error) return <p className="text-red-600">{email.error}</p>
    
    return (
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold text-gray-800 mb-2">Chủ đề:</h4>
          <p className="bg-gray-50 p-3 rounded border">{email.subject}</p>
        </div>
        <div>
          <h4 className="font-semibold text-gray-800 mb-2">Nội dung:</h4>
          <div className="bg-gray-50 p-4 rounded border whitespace-pre-wrap">
            {email.body}
          </div>
        </div>
      </div>
    )
  }

  const formatQuestions = (questions) => {
    if (questions.error) return <p className="text-red-600">{questions.error}</p>
    
    return (
      <div className="space-y-4">
        {questions.questions?.map((q, index) => (
          <Card key={index} className="border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-800">Câu {index + 1}</h4>
                <Badge variant="outline">{q.type}</Badge>
              </div>
              <p className="mb-3">{q.question}</p>
              {q.options && (
                <div className="space-y-1 mb-3">
                  {q.options.map((option, i) => (
                    <div key={i} className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{String.fromCharCode(65 + i)}.</span>
                      <span className="text-sm">{option}</span>
                    </div>
                  ))}
                </div>
              )}
              {q.correct_answer && (
                <div className="text-sm">
                  <span className="font-medium text-green-600">Đáp án: </span>
                  <span>{q.correct_answer}</span>
                </div>
              )}
              {q.explanation && (
                <div className="text-sm mt-2">
                  <span className="font-medium text-blue-600">Giải thích: </span>
                  <span>{q.explanation}</span>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center space-x-2">
          <FileText className="h-5 w-5 text-purple-600" />
          <span>Tạo Nội Dung Tự Động</span>
        </CardTitle>
        <CardDescription>
          Tự động soạn email, tóm tắt tài liệu và tạo câu hỏi đào tạo
        </CardDescription>
      </CardHeader>

      <CardContent>
        <Tabs value={activeContentTab} onValueChange={setActiveContentTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="email" className="flex items-center space-x-2">
              <Mail className="h-4 w-4" />
              <span className="hidden sm:inline">Email</span>
            </TabsTrigger>
            <TabsTrigger value="summary" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">Tóm tắt</span>
            </TabsTrigger>
            <TabsTrigger value="questions" className="flex items-center space-x-2">
              <HelpCircle className="h-4 w-4" />
              <span className="hidden sm:inline">Câu hỏi</span>
            </TabsTrigger>
            <TabsTrigger value="checklist" className="flex items-center space-x-2">
              <CheckSquare className="h-4 w-4" />
              <span className="hidden sm:inline">Checklist</span>
            </TabsTrigger>
          </TabsList>

          {/* Email Tab */}
          <TabsContent value="email" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tạo Email Chào Mừng</CardTitle>
                <CardDescription>
                  Tự động tạo email chào mừng cho nhân viên mới
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    placeholder="Tên nhân viên"
                    value={emailForm.employee_name}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, employee_name: e.target.value }))}
                  />
                  <Input
                    placeholder="Tên công ty"
                    value={emailForm.company_name}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, company_name: e.target.value }))}
                  />
                  <Input
                    placeholder="Vị trí công việc"
                    value={emailForm.position}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, position: e.target.value }))}
                  />
                  <Input
                    placeholder="Ngày bắt đầu"
                    value={emailForm.start_date}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, start_date: e.target.value }))}
                  />
                  <Input
                    placeholder="Phòng ban"
                    value={emailForm.department}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, department: e.target.value }))}
                  />
                  <Input
                    placeholder="Tên quản lý"
                    value={emailForm.manager_name}
                    onChange={(e) => setEmailForm(prev => ({ ...prev, manager_name: e.target.value }))}
                  />
                </div>
                <Button
                  onClick={generateWelcomeEmail}
                  disabled={isLoading || !emailForm.employee_name}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Đang tạo email...
                    </>
                  ) : (
                    <>
                      <Mail className="h-4 w-4 mr-2" />
                      Tạo Email Chào Mừng
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {results.email && (
              <Card className="border-purple-200 bg-purple-50/50">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Email Chào Mừng</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(results.email.subject + '\n\n' + results.email.body)}
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {formatEmail(results.email)}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Summary Tab */}
          <TabsContent value="summary" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tóm Tắt Tài Liệu</CardTitle>
                <CardDescription>
                  Tự động tóm tắt nội dung tài liệu theo nhiều kiểu khác nhau
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Nhập nội dung tài liệu cần tóm tắt..."
                  value={summaryForm.document_text}
                  onChange={(e) => setSummaryForm(prev => ({ ...prev, document_text: e.target.value }))}
                  rows={6}
                />
                <Select
                  value={summaryForm.summary_type}
                  onValueChange={(value) => setSummaryForm(prev => ({ ...prev, summary_type: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {summaryTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  onClick={generateSummary}
                  disabled={isLoading || !summaryForm.document_text}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Đang tóm tắt...
                    </>
                  ) : (
                    <>
                      <FileText className="h-4 w-4 mr-2" />
                      Tóm Tắt Tài Liệu
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {results.summary && (
              <Card className="border-purple-200 bg-purple-50/50">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Kết Quả Tóm Tắt</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(results.summary.summary)}
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {results.summary.error ? (
                    <p className="text-red-600">{results.summary.error}</p>
                  ) : (
                    <div className="bg-white p-4 rounded border">
                      <p className="whitespace-pre-wrap">{results.summary.summary}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Questions Tab */}
          <TabsContent value="questions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tạo Câu Hỏi Đào Tạo</CardTitle>
                <CardDescription>
                  Tự động tạo câu hỏi đào tạo từ nội dung học liệu
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Nhập nội dung để tạo câu hỏi..."
                  value={questionsForm.content}
                  onChange={(e) => setQuestionsForm(prev => ({ ...prev, content: e.target.value }))}
                  rows={6}
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Select
                    value={questionsForm.question_type}
                    onValueChange={(value) => setQuestionsForm(prev => ({ ...prev, question_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {questionTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Input
                    type="number"
                    placeholder="Số câu hỏi"
                    value={questionsForm.num_questions}
                    onChange={(e) => setQuestionsForm(prev => ({ ...prev, num_questions: parseInt(e.target.value) || 5 }))}
                    min="1"
                    max="20"
                  />
                </div>
                <Button
                  onClick={generateQuestions}
                  disabled={isLoading || !questionsForm.content}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Đang tạo câu hỏi...
                    </>
                  ) : (
                    <>
                      <HelpCircle className="h-4 w-4 mr-2" />
                      Tạo Câu Hỏi
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {results.questions && (
              <Card className="border-purple-200 bg-purple-50/50">
                <CardHeader>
                  <CardTitle>Câu Hỏi Đào Tạo</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] pr-4">
                    {formatQuestions(results.questions)}
                  </ScrollArea>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Checklist Tab */}
          <TabsContent value="checklist" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tạo Checklist Onboarding</CardTitle>
                <CardDescription>
                  Tự động tạo checklist onboarding theo vị trí và phòng ban
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    placeholder="Vị trí công việc"
                    value={checklistForm.position}
                    onChange={(e) => setChecklistForm(prev => ({ ...prev, position: e.target.value }))}
                  />
                  <Input
                    placeholder="Phòng ban"
                    value={checklistForm.department}
                    onChange={(e) => setChecklistForm(prev => ({ ...prev, department: e.target.value }))}
                  />
                </div>
                <Button
                  onClick={generateChecklist}
                  disabled={isLoading || !checklistForm.position}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Đang tạo checklist...
                    </>
                  ) : (
                    <>
                      <CheckSquare className="h-4 w-4 mr-2" />
                      Tạo Checklist
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {results.checklist && (
              <Card className="border-purple-200 bg-purple-50/50">
                <CardHeader>
                  <CardTitle>Checklist Onboarding</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] pr-4">
                    {results.checklist.error ? (
                      <p className="text-red-600">{results.checklist.error}</p>
                    ) : (
                      <div className="space-y-6">
                        {Array.isArray(results.checklist.checklist) ? 
                          results.checklist.checklist.map((phase, index) => (
                            <div key={index} className="border rounded-lg p-4 bg-white">
                              <h3 className="font-semibold text-lg mb-3 text-gray-800">
                                {phase.timeline}
                              </h3>
                              <div className="space-y-3">
                                {phase.tasks?.map((task, taskIndex) => (
                                  <div key={taskIndex} className="border-l-4 border-blue-400 pl-4">
                                    <div className="flex items-center justify-between mb-1">
                                      <h4 className="font-medium text-gray-800">{task.task}</h4>
                                      <Badge variant={task.priority === 'High' ? 'destructive' : task.priority === 'Medium' ? 'default' : 'secondary'}>
                                        {task.priority}
                                      </Badge>
                                    </div>
                                    <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                                      <span>👤 {task.responsible}</span>
                                      <span>⏱️ {task.estimated_time}</span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )) : (
                            <p className="text-gray-600">Không có dữ liệu checklist</p>
                          )
                        }
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </div>
  )
}

export default ContentGenerator

