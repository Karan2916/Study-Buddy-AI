import React, { useState, useCallback } from 'react';
import { Upload, FileText, Check, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { uploadFiles } from '@/lib/api';

interface UploadedFile {
  id: string;
  name: string;
  status: 'uploading' | 'processing' | 'indexed';
  progress: number;
}

const FileUpload: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const { toast } = useToast();

  const handleFileSelect = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    
    if (selectedFiles.length === 0) return;

    // Filter PDF files only
    const pdfFiles = selectedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== selectedFiles.length) {
      toast({
        title: "Invalid files detected",
        description: "Only PDF files are supported",
        variant: "destructive",
      });
    }

    if (pdfFiles.length === 0) return;

    // Add files to state with uploading status
    const newFiles: UploadedFile[] = pdfFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      status: 'uploading',
      progress: 0,
    }));

    setFiles(prev => [...prev, ...newFiles]);

    try {
      // Upload files with progress tracking
      await uploadFiles(pdfFiles, (progress) => {
        setFiles(prev => prev.map(file => 
          newFiles.some(nf => nf.id === file.id) 
            ? { ...file, progress }
            : file
        ));
      });

      // Update status to processing
      setFiles(prev => prev.map(file => 
        newFiles.some(nf => nf.id === file.id)
          ? { ...file, status: 'processing', progress: 100 }
          : file
      ));

      // Simulate processing time, then mark as indexed
      setTimeout(() => {
        setFiles(prev => prev.map(file => 
          newFiles.some(nf => nf.id === file.id)
            ? { ...file, status: 'indexed' }
            : file
        ));

        toast({
          title: "Files indexed successfully!",
          description: `${pdfFiles.length} document(s) ready for chat`,
        });
      }, 2000);

    } catch (error) {
      // Remove failed uploads
      setFiles(prev => prev.filter(file => !newFiles.some(nf => nf.id === file.id)));
      
      toast({
        title: "Upload failed",
        description: "Failed to upload files. Please try again.",
        variant: "destructive",
      });
    }

    // Reset input
    event.target.value = '';
  }, [toast]);

  const getStatusColor = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'secondary';
      case 'processing':
        return 'default';
      case 'indexed':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
        return <Clock className="w-3 h-3" />;
      case 'processing':
        return <Clock className="w-3 h-3" />;
      case 'indexed':
        return <Check className="w-3 h-3" />;
      default:
        return null;
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Course Materials
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <input
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload">
            <Button asChild className="w-full">
              <span className="cursor-pointer flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Upload Documents
              </span>
            </Button>
          </label>
        </div>

        <div className="space-y-3">
          {files.map((file) => (
            <div key={file.id} className="p-3 border rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                </div>
                <Badge 
                  variant={getStatusColor(file.status)}
                  className="ml-2 flex items-center gap-1"
                >
                  {getStatusIcon(file.status)}
                  {file.status === 'uploading' ? 'Uploading' : 
                   file.status === 'processing' ? 'Processing' : 'Indexed'}
                </Badge>
              </div>
              
              {(file.status === 'uploading' || file.status === 'processing') && (
                <Progress 
                  value={file.progress} 
                  className="upload-progress"
                />
              )}
            </div>
          ))}
          
          {files.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No documents uploaded yet</p>
              <p className="text-sm">Upload PDF files to get started</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default FileUpload;