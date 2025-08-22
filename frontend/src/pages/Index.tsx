import React from 'react';
import { GraduationCap } from 'lucide-react';
import FileUpload from '@/components/FileUpload';
import ChatWindow from '@/components/ChatWindow';
import ThemeToggle from '@/components/ThemeToggle';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Study Buddy AI
                </h1>
                <p className="text-sm text-muted-foreground">
                  Your intelligent learning companion
                </p>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-120px)]">
          {/* File Upload Panel - 1/4 width on large screens */}
          <div className="lg:col-span-1">
            <FileUpload />
          </div>
          
          {/* Chat Panel - 3/4 width on large screens */}
          <div className="lg:col-span-3">
            <ChatWindow />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;