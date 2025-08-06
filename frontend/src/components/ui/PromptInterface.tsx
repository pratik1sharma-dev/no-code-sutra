import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, ArrowRight } from 'lucide-react';

interface PromptInterfaceProps {
  value: string;
  onChange: (value: string) => void;
  onGenerate: () => void;
  isLoading: boolean;
  suggestions?: string[];
}

const PromptInterface: React.FC<PromptInterfaceProps> = ({
  value,
  onChange,
  onGenerate,
  isLoading,
  suggestions = []
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const defaultSuggestions = [
    "Find construction companies in NYC and send them personalized emails",
    "Create blog posts about AI trends and post them to LinkedIn",
    "Process customer data and send weekly reports to my team",
    "Monitor social media mentions and respond automatically",
    "Generate leads from LinkedIn and add them to CRM"
  ];

  const allSuggestions = suggestions.length > 0 ? suggestions : defaultSuggestions;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !isLoading) {
      onGenerate();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion);
    setShowSuggestions(false);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(true)}
            placeholder="Describe what you want to automate... (e.g., 'Find leads on LinkedIn and send them personalized emails')"
            className="w-full p-6 pr-16 text-lg border-2 border-gray-200 rounded-2xl resize-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200 min-h-[120px] max-h-[300px]"
            disabled={isLoading}
          />
          
          <button
            type="submit"
            disabled={!value.trim() || isLoading}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        {showSuggestions && value.length < 20 && (
          <div className="mt-4 p-4 bg-white border border-gray-200 rounded-xl shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">Try these examples:</span>
            </div>
            <div className="space-y-2">
              {allSuggestions.slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left p-3 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors duration-150"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </form>

      {value.trim() && (
        <div className="mt-4 flex items-center justify-center">
          <button
            onClick={onGenerate}
            disabled={isLoading}
            className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generating Workflow...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Create My Workflow
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default PromptInterface; 