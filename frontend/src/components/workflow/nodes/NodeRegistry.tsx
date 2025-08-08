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
  Brain,
  Globe,
  Bell,
  FolderOpen,
  Server,
  Zap,
  Filter,
  BarChart3,
  AlertTriangle
} from 'lucide-react';
import type { WorkflowNodeData, NodeType } from '../../../types/workflow';
import { BaseNode } from './BaseNode';
import { AIAgentNode } from './AIAgentNode';
import { EmailNode } from './EmailNode';

// Node type definitions
export const NODE_TYPES = {
  aiAgent: {
    type: 'aiAgent' as NodeType,
    label: 'AI Agent',
    description: 'AI-powered tasks (research, analysis, content generation)',
    icon: Bot,
    color: 'primary',
    category: 'AI & ML'
  },
  webScraper: {
    type: 'webScraper' as NodeType,
    label: 'Web Scraper',
    description: 'Extract data from websites and web pages',
    icon: Globe,
    color: 'secondary',
    category: 'Data'
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
  notification: {
    type: 'notification' as NodeType,
    label: 'Notification',
    description: 'Send notifications (push, SMS, in-app)',
    icon: Bell,
    color: 'warning',
    category: 'Communication'
  },
  data: {
    type: 'data' as NodeType,
    label: 'Data',
    description: 'Data processing, storage, and manipulation',
    icon: Database,
    color: 'secondary',
    category: 'Data'
  },
  fileOperation: {
    type: 'fileOperation' as NodeType,
    label: 'File Operation',
    description: 'File operations (read, write, move, delete)',
    icon: FolderOpen,
    color: 'secondary',
    category: 'Data'
  },
  database: {
    type: 'database' as NodeType,
    label: 'Database',
    description: 'Database operations (query, insert, update, delete)',
    icon: Server,
    color: 'secondary',
    category: 'Data'
  },
  apiCall: {
    type: 'apiCall' as NodeType,
    label: 'API Call',
    description: 'External API integrations (social media, third-party services)',
    icon: Zap,
    color: 'primary',
    category: 'Integration'
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
  transform: {
    type: 'transform' as NodeType,
    label: 'Transform',
    description: 'Data transformation (CSV↔JSON, format conversion)',
    icon: FileText,
    color: 'secondary',
    category: 'Data'
  },
  filter: {
    type: 'filter' as NodeType,
    label: 'Filter',
    description: 'Data filtering based on conditions',
    icon: Filter,
    color: 'secondary',
    category: 'Data'
  },
  aggregate: {
    type: 'aggregate' as NodeType,
    label: 'Aggregate',
    description: 'Data aggregation (group, sum, count, average)',
    icon: BarChart3,
    color: 'secondary',
    category: 'Data'
  },
  errorHandler: {
    type: 'errorHandler' as NodeType,
    label: 'Error Handler',
    description: 'Error handling and recovery',
    icon: AlertTriangle,
    color: 'danger',
    category: 'Logic'
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
const WebScraperNode = DefaultNode;
const SlackNode = DefaultNode;
const NotificationNode = DefaultNode;
const DataNode = DefaultNode;
const FileOperationNode = DefaultNode;
const DatabaseNode = DefaultNode;
const ApiCallNode = DefaultNode;
const ConditionNode = DefaultNode;
const DelayNode = DefaultNode;
const ScheduleNode = DefaultNode;
const TransformNode = DefaultNode;
const FilterNode = DefaultNode;
const AggregateNode = DefaultNode;
const ErrorHandlerNode = DefaultNode;

// Node component mapping
const NODE_COMPONENTS: Record<NodeType, React.ComponentType<NodeProps<WorkflowNodeData>>> = {
  aiAgent: AIAgentNode,
  webScraper: WebScraperNode,
  email: EmailNode,
  slack: SlackNode,
  notification: NotificationNode,
  data: DataNode,
  fileOperation: FileOperationNode,
  database: DatabaseNode,
  apiCall: ApiCallNode,
  condition: ConditionNode,
  delay: DelayNode,
  schedule: ScheduleNode,
  transform: TransformNode,
  filter: FilterNode,
  aggregate: AggregateNode,
  errorHandler: ErrorHandlerNode
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