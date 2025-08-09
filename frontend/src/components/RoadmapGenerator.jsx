import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { MapPin, Loader2, CheckCircle, Clock, BookOpen, Target, Users } from 'lucide-react'

const RoadmapGenerator = () => {
  const [selectedPosition, setSelectedPosition] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('fresher')
  const [roadmap, setRoadmap] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [positions, setPositions] = useState([])

  const experienceLevels = [
    { value: 'fresher', label: 'Fresher (0-1 năm)' },
    { value: 'junior', label: 'Junior (1-3 năm)' },
    { value: 'senior', label: 'Senior (3+ năm)' }
  ]

  // Load positions when component mounts
  useEffect(() => {
    fetchPositions()
  }, [])

  const fetchPositions = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/roadmap/positions')
      if (response.ok) {
        const data = await response.json()
        setPositions(data.positions || [])
      }
    } catch (error) {
      console.error('Error fetching positions:', error)
      // Fallback positions
      setPositions(['developer', 'designer', 'marketing', 'hr', 'sales'])
    }
  }

  const generateRoadmap = async () => {
    if (!selectedPosition) return

    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/roadmap/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          position: selectedPosition,
          experience_level: experienceLevel
        }),
      })

      if (!response.ok) {
        throw new Error('Network response was not ok')
      }

      const data = await response.json()
      setRoadmap(data.roadmap || 'Không thể tạo lộ trình lúc này.')
    } catch (error) {
      console.error('Error:', error)
      setRoadmap('Xin lỗi, có lỗi xảy ra khi tạo lộ trình. Vui lòng thử lại sau.')
    } finally {
      setIsLoading(false)
    }
  }

  const formatRoadmap = (content) => {
    if (!content) return null

    const lines = content.split('\n')
    return lines.map((line, index) => {
      // Headers
      if (line.startsWith('###')) {
        return (
          <h3 key={index} className="text-lg font-semibold text-gray-800 mt-6 mb-3 flex items-center">
            <Target className="h-5 w-5 mr-2 text-blue-600" />
            {line.replace('###', '').trim()}
          </h3>
        )
      }
      if (line.startsWith('##')) {
        return (
          <h2 key={index} className="text-xl font-bold text-gray-900 mt-8 mb-4 flex items-center">
            <BookOpen className="h-6 w-6 mr-2 text-green-600" />
            {line.replace('##', '').trim()}
          </h2>
        )
      }
      if (line.startsWith('#')) {
        return (
          <h1 key={index} className="text-2xl font-bold text-gray-900 mt-6 mb-4">
            {line.replace('#', '').trim()}
          </h1>
        )
      }

      // Lists
      if (line.trim().startsWith('-') || line.trim().startsWith('*')) {
        return (
          <div key={index} className="flex items-start space-x-2 mb-2 ml-4">
            <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
            <span className="text-gray-700">{line.replace(/^[\s\-\*]+/, '').trim()}</span>
          </div>
        )
      }

      // Numbers
      if (/^\d+\./.test(line.trim())) {
        return (
          <div key={index} className="flex items-start space-x-2 mb-2 ml-4">
            <div className="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium flex-shrink-0">
              {line.trim().match(/^\d+/)[0]}
            </div>
            <span className="text-gray-700">{line.replace(/^\d+\.\s*/, '').trim()}</span>
          </div>
        )
      }

      // Bold text
      if (line.includes('**')) {
        const parts = line.split('**')
        return (
          <p key={index} className="mb-3 text-gray-700">
            {parts.map((part, i) => 
              i % 2 === 1 ? <strong key={i} className="font-semibold text-gray-900">{part}</strong> : part
            )}
          </p>
        )
      }

      // Regular paragraphs
      if (line.trim()) {
        return (
          <p key={index} className="mb-3 text-gray-700 leading-relaxed">
            {line}
          </p>
        )
      }

      return <div key={index} className="mb-2"></div>
    })
  }

  return (
    <div className="space-y-6">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center space-x-2">
          <MapPin className="h-5 w-5 text-green-600" />
          <span>Tạo Lộ Trình Onboarding Cá Nhân Hóa</span>
        </CardTitle>
        <CardDescription>
          Tạo lộ trình học tập và làm quen phù hợp với vị trí công việc và kinh nghiệm
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Input Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Vị trí công việc</label>
            <Select value={selectedPosition} onValueChange={setSelectedPosition}>
              <SelectTrigger>
                <SelectValue placeholder="Chọn vị trí công việc" />
              </SelectTrigger>
              <SelectContent>
                {positions.map((position) => (
                  <SelectItem key={position} value={position}>
                    {position.charAt(0).toUpperCase() + position.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Mức độ kinh nghiệm</label>
            <Select value={experienceLevel} onValueChange={setExperienceLevel}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {experienceLevels.map((level) => (
                  <SelectItem key={level.value} value={level.value}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button
          onClick={generateRoadmap}
          disabled={!selectedPosition || isLoading}
          className="w-full bg-green-600 hover:bg-green-700"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Đang tạo lộ trình...
            </>
          ) : (
            <>
              <Target className="h-4 w-4 mr-2" />
              Tạo Lộ Trình
            </>
          )}
        </Button>

        {/* Results */}
        {roadmap && (
          <Card className="border-green-200 bg-green-50/50">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-green-800">
                <CheckCircle className="h-5 w-5" />
                <span>Lộ Trình Onboarding</span>
              </CardTitle>
              <div className="flex items-center space-x-4">
                <Badge variant="outline" className="border-green-300 text-green-700">
                  <Users className="h-3 w-3 mr-1" />
                  {selectedPosition}
                </Badge>
                <Badge variant="outline" className="border-blue-300 text-blue-700">
                  <Clock className="h-3 w-3 mr-1" />
                  {experienceLevels.find(l => l.value === experienceLevel)?.label}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px] pr-4">
                <div className="prose prose-sm max-w-none">
                  {formatRoadmap(roadmap)}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-blue-200 bg-blue-50/50">
            <CardContent className="p-4 text-center">
              <BookOpen className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-medium text-blue-800 mb-1">Tài liệu học tập</h3>
              <p className="text-sm text-blue-600">Gợi ý tài liệu phù hợp</p>
            </CardContent>
          </Card>

          <Card className="border-purple-200 bg-purple-50/50">
            <CardContent className="p-4 text-center">
              <Target className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h3 className="font-medium text-purple-800 mb-1">Mục tiêu</h3>
              <p className="text-sm text-purple-600">Theo dõi tiến độ</p>
            </CardContent>
          </Card>

          <Card className="border-orange-200 bg-orange-50/50">
            <CardContent className="p-4 text-center">
              <Users className="h-8 w-8 text-orange-600 mx-auto mb-2" />
              <h3 className="font-medium text-orange-800 mb-1">Mentor</h3>
              <p className="text-sm text-orange-600">Kết nối với đồng nghiệp</p>
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </div>
  )
}

export default RoadmapGenerator

