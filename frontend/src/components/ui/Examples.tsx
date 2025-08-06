import React from 'react';
import { Zap, Mail, TrendingUp, Users, MessageSquare, BarChart3 } from 'lucide-react';

interface Example {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  category: string;
  prompt: string;
  complexity: 'simple' | 'medium' | 'complex';
}

const Examples: React.FC = () => {
  const examples: Example[] = [
    {
      id: '1',
      title: 'Lead Generation',
      description: 'Find and qualify leads automatically',
      icon: <Users className="w-6 h-6" />,
      category: 'Sales',
      prompt: 'Find construction companies in NYC and send them personalized emails',
      complexity: 'simple'
    },
    {
      id: '2',
      title: 'Content Marketing',
      description: 'Create and distribute content across platforms',
      icon: <TrendingUp className="w-6 h-6" />,
      category: 'Marketing',
      prompt: 'Create blog posts about AI trends and post them to LinkedIn',
      complexity: 'medium'
    },
    {
      id: '3',
      title: 'Customer Support',
      description: 'Automate customer inquiries and responses',
      icon: <MessageSquare className="w-6 h-6" />,
      category: 'Support',
      prompt: 'Monitor social media mentions and respond automatically',
      complexity: 'medium'
    },
    {
      id: '4',
      title: 'Data Processing',
      description: 'Process and analyze data automatically',
      icon: <BarChart3 className="w-6 h-6" />,
      category: 'Analytics',
      prompt: 'Process customer data and send weekly reports to my team',
      complexity: 'simple'
    },
    {
      id: '5',
      title: 'Email Automation',
      description: 'Send personalized emails at scale',
      icon: <Mail className="w-6 h-6" />,
      category: 'Communication',
      prompt: 'Send follow-up emails to leads based on their behavior',
      complexity: 'simple'
    },
    {
      id: '6',
      title: 'AI Research',
      description: 'Research and analyze information automatically',
      icon: <Zap className="w-6 h-6" />,
      category: 'Research',
      prompt: 'Research competitors and generate market analysis reports',
      complexity: 'complex'
    }
  ];

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple':
        return 'bg-green-100 text-green-700';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'complex':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getComplexityLabel = (complexity: string) => {
    switch (complexity) {
      case 'simple':
        return 'Easy';
      case 'medium':
        return 'Medium';
      case 'complex':
        return 'Advanced';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Popular Use Cases
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          See how others are automating their workflows. Click any example to get started.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {examples.map((example) => (
          <div
            key={example.id}
            className="group bg-white border border-gray-200 rounded-2xl p-6 hover:border-blue-300 hover:shadow-lg transition-all duration-200 cursor-pointer"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg text-blue-600 group-hover:bg-blue-100 transition-colors">
                  {example.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    {example.title}
                  </h3>
                  <p className="text-sm text-gray-500">{example.category}</p>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getComplexityColor(example.complexity)}`}>
                {getComplexityLabel(example.complexity)}
              </span>
            </div>

            <p className="text-gray-600 text-sm mb-4">
              {example.description}
            </p>

            <div className="bg-gray-50 rounded-lg p-3 mb-4">
              <p className="text-xs text-gray-500 mb-1">Example prompt:</p>
              <p className="text-sm text-gray-700 italic">
                "{example.prompt}"
              </p>
            </div>

            <button className="w-full text-left text-sm text-blue-600 hover:text-blue-700 font-medium group-hover:underline transition-colors">
              Try this workflow →
            </button>
          </div>
        ))}
      </div>

      <div className="mt-12 text-center">
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Don't see what you need?
          </h3>
          <p className="text-gray-600 mb-6">
            Our AI can create custom workflows for any automation need. Just describe what you want to achieve.
          </p>
          <button className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
            <Zap className="w-4 h-4" />
            Create Custom Workflow
          </button>
        </div>
      </div>
    </div>
  );
};

export default Examples; 