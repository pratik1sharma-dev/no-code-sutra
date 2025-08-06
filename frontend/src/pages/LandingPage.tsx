import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, CheckCircle, Zap, Clock, Shield } from 'lucide-react';
import { apiEndpoints } from '../config/environment';
import PromptInterface from '../components/ui/PromptInterface';
import ChatInterface from '../components/ui/ChatInterface';
import WorkflowPreview from '../components/ui/WorkflowPreview';
import Examples from '../components/ui/Examples';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [userPrompt, setUserPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedWorkflow, setGeneratedWorkflow] = useState<any>(null);
  const [showChat, setShowChat] = useState(false);
  const [clarificationQuestions, setClarificationQuestions] = useState<string[]>([]);

  const handleGenerateWorkflow = async () => {
    if (!userPrompt.trim()) {
      alert('Please enter a description of what you want to automate.');
      return;
    }
    
    if (userPrompt.length < 10) {
      alert('Please provide a more detailed description (at least 10 characters).');
      return;
    }
    
    setIsGenerating(true);
    try {
      // Call the Python backend to generate workflow
      const response = await fetch(apiEndpoints.generateWorkflow, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: userPrompt,
          user_id: null
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate workflow');
      }

      const result = await response.json();
      
      // Check if clarification is needed
      if (result.questions && result.questions.length > 0) {
        setGeneratedWorkflow(result.workflow);
        setClarificationQuestions(result.questions);
        setShowChat(true);
      } else {
        // Navigate directly to workflow builder
        navigateToEditor(result.workflow, userPrompt);
      }
    } catch (error) {
      console.error('Failed to generate workflow:', error);
      
      // Show user-friendly error message
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Failed to connect to the AI service. Please check your internet connection and try again.';
      
      alert(`Error: ${errorMessage}`);
      
      // Fallback to simple workflow if backend is not available
      const fallbackWorkflow = {
        name: 'Simple Workflow',
        description: userPrompt,
        nodes: [
          { 
            id: '1', 
            type: 'aiAgent', 
            label: 'Process Request', 
            position: { x: 100, y: 100 },
            data: {
              label: 'Process Request',
              type: 'aiAgent',
              config: { prompt: userPrompt },
              status: 'idle',
              executionCount: 0
            }
          }
        ],
        edges: []
      };
      
      navigateToEditor(fallbackWorkflow, userPrompt);
    } finally {
      setIsGenerating(false);
    }
  };

  const navigateToEditor = (workflow: any, originalPrompt: string) => {
    const workflowData = encodeURIComponent(JSON.stringify({
      prompt: originalPrompt,
      generated: true,
      ...workflow
    }));
    
    navigate(`/app/workflow/new?generated=${workflowData}`);
  };

  const handleChatComplete = (finalWorkflow: any) => {
    setShowChat(false);
    setGeneratedWorkflow(finalWorkflow);
  };

  const handleCustomizeWorkflow = () => {
    if (generatedWorkflow) {
      navigateToEditor(generatedWorkflow, userPrompt);
    }
  };

  const examples = [
    "Find construction companies in NYC and send them personalized emails",
    "Create blog posts about AI trends and post them to LinkedIn",
    "Process customer data and send weekly reports to my team"
  ];

  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Instant Automation",
      description: "From idea to working workflow in under 3 minutes"
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "AI-Powered",
      description: "Smart suggestions and automatic optimization"
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Save Time",
      description: "Automate repetitive tasks and focus on what matters"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Reliable",
      description: "Enterprise-grade automation that actually works"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">No Code Sutra</span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
            <a href="#examples" className="text-gray-600 hover:text-gray-900 transition-colors">Examples</a>
            <button 
              onClick={() => navigate('/login')}
              className="px-4 py-2 text-blue-600 hover:text-blue-700 transition-colors"
            >
              Sign In
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Main Headline */}
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Automate Anything with AI
          </h1>
          
          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Describe what you want to automate. We'll build it for you.
          </p>

          {/* Input Section */}
          <div className="mb-16">
            <PromptInterface
              value={userPrompt}
              onChange={setUserPrompt}
              onGenerate={handleGenerateWorkflow}
              isLoading={isGenerating}
            />
          </div>

          {/* Chat Interface for Clarification */}
          {showChat && (
            <div className="mb-16">
              <ChatInterface
                workflow={generatedWorkflow}
                questions={clarificationQuestions}
                onComplete={handleChatComplete}
              />
            </div>
          )}

          {/* Workflow Preview */}
          {generatedWorkflow && !showChat && (
            <div className="mb-16">
              <WorkflowPreview
                workflow={generatedWorkflow}
                onCustomize={handleCustomizeWorkflow}
              />
            </div>
          )}
        </div>

        {/* Features Section */}
        <section id="features" className="max-w-6xl mx-auto py-16">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center p-6">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4 text-blue-600">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* How It Works */}
        <section className="max-w-4xl mx-auto py-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Describe</h3>
              <p className="text-gray-600">Tell us what you want to automate in simple language</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Generate</h3>
              <p className="text-gray-600">AI creates your workflow automatically</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Deploy</h3>
              <p className="text-gray-600">Connect your accounts and start automating</p>
            </div>
          </div>
        </section>

        {/* Examples Section */}
        <section id="examples" className="py-16">
          <Examples />
        </section>

        {/* CTA Section */}
        <section className="max-w-2xl mx-auto py-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Automate?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of professionals who are already saving hours every day
          </p>
          <button
            onClick={() => setUserPrompt('')}
            className="px-8 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors text-lg font-semibold"
          >
            Start Your First Workflow
          </button>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>&copy; 2024 No Code Sutra. The simplest way to create AI-powered workflows.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 