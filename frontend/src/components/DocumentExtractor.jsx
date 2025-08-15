import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Upload, FileText, User, Loader2, CheckCircle, AlertCircle, Download, Copy } from 'lucide-react'

const DocumentExtractor = () => {
  const [activeExtractTab, setActiveExtractTab] = useState('upload')
  const [isLoading, setIsLoading] = useState(false)
  const [extractedData, setExtractedData] = useState(null)
  const [formData, setFormData] = useState({})
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const documentTypes = [
    { value: 'cv', label: 'CV/Resume' },
    { value: 'id_card', label: 'CMND/CCCD' },
    { value: 'diploma', label: 'Bằng cấp' },
    { value: 'other', label: 'Tài liệu khác' }
  ]

  const formFields = [
    { key: 'full_name', label: 'Họ và tên', type: 'text' },
    { key: 'email', label: 'Email', type: 'email' },
    { key: 'phone', label: 'Số điện thoại', type: 'tel' },
    { key: 'address', label: 'Địa chỉ', type: 'text' },
    { key: 'date_of_birth', label: 'Ngày sinh', type: 'date' },
    { key: 'id_number', label: 'Số CMND/CCCD', type: 'text' },
    { key: 'education', label: 'Học vấn', type: 'text' },
    { key: 'experience', label: 'Kinh nghiệm', type: 'textarea' },
    { key: 'skills', label: 'Kỹ năng', type: 'textarea' },
    { key: 'position_applied', label: 'Vị trí ứng tuyển', type: 'text' }
  ]

  const allowedFileTypes = [
    'application/pdf',        // PDF
    'application/msword',     // DOC
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // DOCX
    'text/plain',             // TXT
    'image/jpeg',             // JPG/JPEG
    'image/png'               // PNG
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Kiểm tra định dạng file
    if (!allowedFileTypes.includes(file.type)) {
      alert(`Định dạng tệp không hợp lệ: ${file.name}`);
      return;
    }

    setSelectedFile(file);
  }

  const handleDragOver = (event) => {
    event.preventDefault()
  }

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (!file) return;

    // Kiểm tra định dạng file
    if (!allowedFileTypes.includes(file.type)) {
      alert(`Định dạng tệp không hợp lệ: ${file.name}`);
      return;
    }

    setSelectedFile(file);
  }

  const extractFromDocument = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    const formDataToSend = new FormData()
    formDataToSend.append('file', selectedFile)
    formDataToSend.append('document_type', 'cv') // Default to CV

    try {
      const response = await fetch('http://127.0.0.1:5001/api/extract/upload', {
        method: 'POST',
        body: formDataToSend,
      })

      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      if (data?.result?.error) {
        const errorMessage = data.result.error;
        setExtractedData({ error: errorMessage });
        alert(`Có lỗi khi trích xuất: ${errorMessage}`);
        setIsLoading(false);
        return; // dừng hàm, không fill form
      }
      const extracted = data?.result?.extracted_data || {};
      setExtractedData(extracted)

      function getPositionApplied(experience = []) {
        if (!experience.length) return '';
      
        // Ưu tiên job hiện tại
        const currentJob = experience.find(e =>
          e.duration?.toLowerCase().includes('nay') ||
          e.duration?.toLowerCase().includes('present')
        );
      
        if (currentJob) return currentJob.position || '';
      
        // Nếu không có job hiện tại thì lấy job mới nhất (cuối danh sách)
        return experience.slice(-1)[0]?.position || '';
      }

      function convertToISO(dateStr) {
        const [day, month, year] = dateStr.split('/');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
      }
      
      // Auto-fill form with extracted data
      setFormData({
        full_name: extracted.personal_info?.full_name || '',
        email: extracted.personal_info?.email || '',
        phone: extracted.personal_info?.phone || '',
        address: extracted.personal_info?.address || '',
        date_of_birth: extracted.personal_info?.birth_date
        ? convertToISO(extracted.personal_info.birth_date)
        : '',
        id_number: extracted.personal_info?.id_number || '',
        education: extracted.education?.map(e => `${e.degree} - ${e.school}`).join(', ') || '',
        experience: extracted.experience?.map(e => `${e.position} tại ${e.company}`).join('\n') || '',
        skills: [
          ...(extracted.skills?.technical || []),
          ...(extracted.skills?.languages || [])
        ].join(', '),
        position_applied: getPositionApplied(extracted.experience)
      });
      setActiveExtractTab('form')
    } catch (error) {
      console.error('Error:', error)
      setExtractedData({ error: 'Có lỗi xảy ra khi trích xuất thông tin từ tài liệu' })
    } finally {
      setIsLoading(false)
    }
  }

  const autoFillForm = async () => {
    if (!extractedData || extractedData.error) return

    setIsLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5001/api/extract/auto-fill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ extracted_info: extractedData }),
      })

      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setFormData(data.form_data || {})
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFormChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  const downloadFormData = () => {
    const dataStr = JSON.stringify(formData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'form_data.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  const formatExtractedData = (data) => {
    if (data.error) {
      return <p className="text-red-600">{data.error}</p>
    }

    return (
      <div className="space-y-4">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="border-b pb-2">
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-700 capitalize">
                {key.replace(/_/g, ' ')}:
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(value?.toString() || '')}
              >
                <Copy className="h-3 w-3" />
              </Button>
            </div>
            <p className="text-gray-900 mt-1">{value?.toString() || 'N/A'}</p>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center space-x-2">
          <Upload className="h-5 w-5 text-orange-600" />
          <span>Trích Xuất Thông Tin Tự Động</span>
        </CardTitle>
        <CardDescription>
          Upload tài liệu để tự động trích xuất thông tin và điền biểu mẫu
        </CardDescription>
      </CardHeader>

      <CardContent>
        <Tabs value={activeExtractTab} onValueChange={setActiveExtractTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="upload" className="flex items-center space-x-2">
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </TabsTrigger>
            <TabsTrigger value="extract" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Trích xuất</span>
            </TabsTrigger>
            <TabsTrigger value="form" className="flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span>Biểu mẫu</span>
            </TabsTrigger>
          </TabsList>

          {/* Upload Tab */}
          <TabsContent value="upload" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Upload Tài Liệu</CardTitle>
                <CardDescription>
                  Hỗ trợ các định dạng: PDF, DOCX, DOC, TXT, JPG, PNG
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* File Upload Area */}
                <div
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-orange-400 transition-colors cursor-pointer"
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  {selectedFile ? (
                    <div className="space-y-2">
                      <p className="text-lg font-medium text-gray-900">{selectedFile.name}</p>
                      <p className="text-sm text-gray-600">
                        Kích thước: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <Badge variant="outline" className="mt-2">
                        {selectedFile.type || 'Unknown type'}
                      </Badge>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <p className="text-lg font-medium text-gray-900">
                        Kéo thả file vào đây hoặc click để chọn
                      </p>
                      <p className="text-sm text-gray-600">
                        Hỗ trợ PDF, DOCX, DOC, TXT, JPG, PNG (tối đa 10MB)
                      </p>
                    </div>
                  )}
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png"
                  onChange={handleFileSelect}
                />

                {selectedFile && (
                  <div className="flex space-x-2">
                    <Button
                      onClick={extractFromDocument}
                      disabled={isLoading}
                      className="flex-1 bg-orange-600 hover:bg-orange-700"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Đang xử lý...
                        </>
                      ) : (
                        <>
                          <FileText className="h-4 w-4 mr-2" />
                          Trích Xuất Thông Tin
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setSelectedFile(null)}
                    >
                      Hủy
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Supported Documents */}
            <Card className="border-blue-200 bg-blue-50/50">
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-blue-600" />
                  Loại Tài Liệu Hỗ Trợ
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {documentTypes.map((type) => (
                    <div key={type.value} className="flex items-center space-x-3 p-3 bg-white rounded border">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span className="font-medium">{type.label}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Extract Tab */}
          <TabsContent value="extract" className="space-y-4">
            {extractedData ? (
              <Card className="border-orange-200 bg-orange-50/50">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center">
                      <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
                      Thông Tin Đã Trích Xuất
                    </span>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={autoFillForm}
                        disabled={isLoading || extractedData.error}
                      >
                        <User className="h-4 w-4 mr-2" />
                        Điền Biểu Mẫu
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(JSON.stringify(extractedData, null, 2))}
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Copy JSON
                      </Button>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] pr-4">
                    {formatExtractedData(extractedData)}
                  </ScrollArea>
                </CardContent>
              </Card>
            ) : (
              <Card className="border-gray-200">
                <CardContent className="p-8 text-center">
                  <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-600 mb-2">
                    Chưa có dữ liệu trích xuất
                  </p>
                  <p className="text-sm text-gray-500">
                    Vui lòng upload tài liệu ở tab "Upload" để bắt đầu trích xuất thông tin
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Form Tab */}
          <TabsContent value="form" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center">
                    <User className="h-5 w-5 mr-2 text-orange-600" />
                    Biểu Mẫu Thông Tin Nhân Viên
                  </span>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={downloadFormData}
                      disabled={Object.keys(formData).length === 0}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Tải xuống
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(JSON.stringify(formData, null, 2))}
                      disabled={Object.keys(formData).length === 0}
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </Button>
                  </div>
                </CardTitle>
                <CardDescription>
                  Thông tin được tự động điền từ tài liệu đã upload
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {formFields.map((field) => (
                    <div key={field.key} className="space-y-2">
                      <label className="text-sm font-medium text-gray-700">
                        {field.label}
                      </label>
                      {field.type === 'textarea' ? (
                        <Textarea
                          value={formData[field.key] || ''}
                          onChange={(e) => handleFormChange(field.key, e.target.value)}
                          placeholder={`Nhập ${field.label.toLowerCase()}`}
                          rows={3}
                        />
                      ) : (
                        <Input
                          type={field.type}
                          value={formData[field.key] || ''}
                          onChange={(e) => handleFormChange(field.key, e.target.value)}
                          placeholder={`Nhập ${field.label.toLowerCase()}`}
                        />
                      )}
                    </div>
                  ))}
                </div>

                {Object.keys(formData).length > 0 && (
                  <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="font-medium text-green-800">
                        Biểu mẫu đã được điền tự động
                      </span>
                    </div>
                    <p className="text-sm text-green-700">
                      Vui lòng kiểm tra và chỉnh sửa thông tin nếu cần thiết
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </CardContent>
    </div>
  )
}

export default DocumentExtractor

