import React, { useState } from 'react';
import { Send, MessageCircle, CheckCircle } from 'lucide-react';

interface ChatMessage {
  id: string;
  type: 'question' | 'answer';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  workflow: any;
  questions: string[];
  onComplete: (workflow: any) => void;
  onAskClarification?: (question: string, answer: string) => Promise<any>;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  workflow,
  questions,
  onComplete,
  onAskClarification
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  React.useEffect(() => {
    if (questions.length > 0 && currentQuestionIndex < questions.length) {
      const question = questions[currentQuestionIndex];
      setMessages(prev => [...prev, {
        id: `q-${currentQuestionIndex}`,
        type: 'question',
        content: question,
        timestamp: new Date()
      }]);
    }
  }, [currentQuestionIndex, questions]);

  const handleSubmitAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentAnswer.trim() || isProcessing) return;

    const answer = currentAnswer.trim();
    setCurrentAnswer('');
    setIsProcessing(true);

    // Add user answer to messages
    setMessages(prev => [...prev, {
      id: `a-${currentQuestionIndex}`,
      type: 'answer',
      content: answer,
      timestamp: new Date()
    }]);

    try {
      if (onAskClarification) {
        const updatedWorkflow = await onAskClarification(
          questions[currentQuestionIndex],
          answer
        );
        
        if (updatedWorkflow) {
          // If we have more questions, continue
          if (currentQuestionIndex + 1 < questions.length) {
            setCurrentQuestionIndex(prev => prev + 1);
          } else {
            // All questions answered, complete the workflow
            onComplete(updatedWorkflow);
          }
        }
      } else {
        // If no clarification handler, just move to next question
        if (currentQuestionIndex + 1 < questions.length) {
          setCurrentQuestionIndex(prev => prev + 1);
        } else {
          onComplete(workflow);
        }
      }
    } catch (error) {
      console.error('Error processing clarification:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSkip = () => {
    if (currentQuestionIndex + 1 < questions.length) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      onComplete(workflow);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto bg-white rounded-2xl shadow-lg border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <MessageCircle className="w-6 h-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Let's refine your workflow</h3>
            <p className="text-sm text-gray-600">
              {currentQuestionIndex + 1} of {questions.length} questions
            </p>
          </div>
        </div>
      </div>

      <div className="h-96 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'question' ? 'justify-start' : 'justify-end'}`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-2xl ${
                message.type === 'question'
                  ? 'bg-blue-50 text-gray-900 border border-blue-200'
                  : 'bg-blue-600 text-white'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-4 rounded-2xl">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {currentQuestionIndex < questions.length && !isProcessing && (
        <div className="p-6 border-t border-gray-200">
          <form onSubmit={handleSubmitAnswer} className="space-y-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                placeholder="Type your answer..."
                className="flex-1 p-3 border border-gray-300 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                disabled={isProcessing}
              />
              <button
                type="submit"
                disabled={!currentAnswer.trim() || isProcessing}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex justify-between items-center">
              <button
                type="button"
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Skip this question
              </button>
              
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <CheckCircle className="w-4 h-4" />
                {currentQuestionIndex + 1} of {questions.length}
              </div>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatInterface; 