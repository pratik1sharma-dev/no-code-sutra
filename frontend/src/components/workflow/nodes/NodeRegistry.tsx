import React from 'react';
import type { NodeProps } from 'reactflow';
import { 
  Bot, 
  Mail, 
  MessageSquare, 
  Database, 
  GitBranch, 
  Clock, 
  Calendar,
  FileText,
  Share2,
  Image,
  Search,
  Brain
} from 'lucide-react';
import type { WorkflowNodeData, NodeType } from '../../../types/workflow';
import { BaseNode } from './BaseNode';
import { AIAgentNode } from './AIAgentNode';
import { EmailNode } from './EmailNode';
import { LangGraphNode } from './LangGraphNode';

// Node type definitions
export const NODE_TYPES = {
  aiAgent: {
    type: 'aiAgent' as NodeType,
    label: 'AI Agent',
    description: 'LangGraph AI agent for intelligent processing',
    icon: Bot,
    color: 'primary',
    category: 'AI & ML'
  },
  langGraph: {
    type: 'langGraph' as NodeType,
    label: 'LangGraph Agent',
    description: 'AI-powered workflow nodes with LangGraph',
    icon: Brain,
    color: 'primary',
    category: 'AI & ML'
  },
  email: {
    type: 'email' as NodeType,
    label: 'Email',
    description: 'Send automated emails with templates',
    icon: Mail,
    color: 'success',
    category: 'Communication'
  },
  slack: {
    type: 'slack' as NodeType,
    label: 'Slack',
    description: 'Send messages to Slack channels',
    icon: MessageSquare,
    color: 'primary',
    category: 'Communication'
  },
  data: {
    type: 'data' as NodeType,
    label: 'Data',
    description: 'Input/output data handling',
    icon: Database,
    color: 'secondary',
    category: 'Data'
  },
  condition: {
    type: 'condition' as NodeType,
    label: 'Condition',
    description: 'If/then logic and branching',
    icon: GitBranch,
    color: 'warning',
    category: 'Logic'
  },
  delay: {
    type: 'delay' as NodeType,
    label: 'Delay',
    description: 'Add time delays to workflow',
    icon: Clock,
    color: 'secondary',
    category: 'Timing'
  },
  schedule: {
    type: 'schedule' as NodeType,
    label: 'Schedule',
    description: 'Schedule workflow execution',
    icon: Calendar,
    color: 'primary',
    category: 'Timing'
  },
  blogWriter: {
    type: 'blogWriter' as NodeType,
    label: 'Blog Writer',
    description: 'Generate blog content with AI',
    icon: FileText,
    color: 'success',
    category: 'Content'
  },
  socialMedia: {
    type: 'socialMedia' as NodeType,
    label: 'Social Media',
    description: 'Post to social media platforms',
    icon: Share2,
    color: 'primary',
    category: 'Content'
  },
  imageGenerator: {
    type: 'imageGenerator' as NodeType,
    label: 'Image Generator',
    description: 'Generate images with AI',
    icon: Image,
    color: 'warning',
    category: 'Content'
  },
  seoOptimizer: {
    type: 'seoOptimizer' as NodeType,
    label: 'SEO Optimizer',
    description: 'Optimize content for SEO',
    icon: Search,
    color: 'success',
    category: 'Content'
  }
} as const;

// Default node component for unimplemented nodes
const DefaultNode: React.FC<NodeProps<WorkflowNodeData>> = (props) => {
  const { data } = props;
  const nodeType = NODE_TYPES[data.type];
  const Icon = nodeType?.icon || Bot;

  return (
    <BaseNode
      {...props}
      icon={<Icon className="w-4 h-4" />}
      color={nodeType?.color || 'primary'}
    >
      <div className="text-xs text-gray-500">
        {nodeType?.description || 'Node type not implemented yet'}
      </div>
    </BaseNode>
  );
};

// Placeholder components for unimplemented nodes
const SlackNode = DefaultNode;
const DataNode = DefaultNode;
const ConditionNode = DefaultNode;
const DelayNode = DefaultNode;
const ScheduleNode = DefaultNode;
const BlogWriterNode = DefaultNode;
const SocialMediaNode = DefaultNode;
const ImageGeneratorNode = DefaultNode;
const SEOOptimizerNode = DefaultNode;

// Node component mapping
const NODE_COMPONENTS: Record<NodeType, React.ComponentType<NodeProps<WorkflowNodeData>>> = {
  aiAgent: AIAgentNode,
  langGraph: LangGraphNode,
  email: EmailNode,
  slack: SlackNode,
  data: DataNode,
  condition: ConditionNode,
  delay: DelayNode,
  schedule: ScheduleNode,
  blogWriter: BlogWriterNode,
  socialMedia: SocialMediaNode,
  imageGenerator: ImageGeneratorNode,
  seoOptimizer: SEOOptimizerNode
};

// Node registry hook
export const useNodeRegistry = () => {
  const getNodeComponent = (type: NodeType) => {
    return NODE_COMPONENTS[type] || DefaultNode;
  };

  const getNodeTypeInfo = (type: NodeType) => {
    return NODE_TYPES[type];
  };

  const getAllNodeTypes = () => {
    return Object.values(NODE_TYPES);
  };

  const getNodeTypesByCategory = () => {
    const categories: Record<string, typeof NODE_TYPES[keyof typeof NODE_TYPES][]> = {};
    
    Object.values(NODE_TYPES).forEach(nodeType => {
      if (!categories[nodeType.category]) {
        categories[nodeType.category] = [];
      }
      categories[nodeType.category].push(nodeType);
    });

    return categories;
  };

  return {
    getNodeComponent,
    getNodeTypeInfo,
    getAllNodeTypes,
    getNodeTypesByCategory
  };
}; 