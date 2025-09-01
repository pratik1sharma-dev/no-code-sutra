import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Trash2, 
  Edit, 
  Plus, 
  Search, 
  Filter,
  Clock,
  MoreVertical,
  Calendar,
  Activity,
  Loader2,
  Globe,
  Lock,
  History
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import apiService, { WorkflowListResponse } from '../services/api';
import { authService } from '../services/auth';

interface Workflow {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  node_count: number;
  status: string;
  user_id: string;
  is_public: boolean;
  version: number;
  parent_id?: string;
}

const Workflows: React.FC = () => {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'draft' | 'active' | 'paused'>('all');
  const [sharingFilter, setSharingFilter] = useState<'all' | 'public' | 'private'>('all');
  const [totalCount, setTotalCount] = useState(0);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  // Get current user info
  useEffect(() => {
    const userInfo = authService.getUser();
    if (userInfo && userInfo.user_id) {
      setCurrentUserId(userInfo.user_id);
    }
  }, []);

  // Load workflows from backend
  useEffect(() => {
    const loadWorkflows = async () => {
      try {
        setIsLoading(true);
        const includePublic = sharingFilter === 'all' || sharingFilter === 'public';
        const response = await apiService.listWorkflows({
          include_public: includePublic,
          show_versions: false,
          limit: 50,
          offset: 0
        });
        
        setWorkflows(response.workflows || []);
        setTotalCount(response.total);
      } catch (error) {
        console.error('Failed to load workflows:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadWorkflows();
  }, [sharingFilter]);

  // Filter workflows
  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workflow.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || workflow.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleCreateNew = () => {
    navigate('/app/workflow');
  };

  const handleEditWorkflow = (workflowId: string) => {
    console.log('Navigating to workflow:', workflowId);
    navigate(`/app/workflow/${workflowId}`);
  };

  const handleDeleteWorkflow = async (workflowId: string, workflowName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${workflowName}"? This will remove all versions of this workflow.`)) {
      return;
    }

    try {
      const response = await apiService.deleteWorkflow(workflowId, true);
      
      if (response.success) {
        setWorkflows(prev => prev.filter(w => w.id !== workflowId));
      } else {
        alert(`Failed to delete workflow: ${response.message}`);
      }
    } catch (error) {
      console.error('Failed to delete workflow:', error);
      alert('Failed to delete workflow');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const WorkflowCard: React.FC<{ workflow: Workflow }> = ({ workflow }) => {
    const [showActions, setShowActions] = useState(false);

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">{workflow.name}</h3>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(workflow.status)}`}>
                {workflow.status}
              </span>
              
              {/* Version badge */}
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                <History className="w-3 h-3 mr-1" />
                v{workflow.version}
              </span>
              
              {/* Public/Private badge */}
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-50 text-gray-700">
                {workflow.is_public ? (
                  <>
                    <Globe className="w-3 h-3 mr-1" />
                    Public
                  </>
                ) : (
                  <>
                    <Lock className="w-3 h-3 mr-1" />
                    Private
                  </>
                )}
              </span>
            </div>
            
            {workflow.description && (
              <p className="text-gray-600 mb-4">{workflow.description}</p>
            )}
            
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center">
                <Activity className="w-4 h-4 mr-1" />
                <span>{workflow.node_count} nodes</span>
              </div>
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                <span>Updated {new Date(workflow.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
          
          <div className="relative ml-4">
            <button
              onClick={() => setShowActions(!showActions)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <MoreVertical className="w-4 h-4 text-gray-500" />
            </button>
            
            {showActions && (
              <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[140px]">
                <button
                  onClick={() => {
                    setShowActions(false);
                    handleEditWorkflow(workflow.id);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </button>
                
                <button
                  onClick={() => {
                    setShowActions(false);
                    navigate(`/app/schedules?workflow=${workflow.id}`);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <Clock className="w-4 h-4 mr-2" />
                  Schedule
                </button>
                
                <div className="border-t border-gray-100 my-1" />
                
                <button
                  onClick={() => {
                    setShowActions(false);
                    handleDeleteWorkflow(workflow.id, workflow.name);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <div className="text-xs text-gray-500">
            Created {new Date(workflow.created_at).toLocaleDateString()}
          </div>
          
          <button
            onClick={() => handleEditWorkflow(workflow.id)}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center"
          >
            <Edit className="w-3 h-3 mr-1" />
            Edit
          </button>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center text-gray-600">
          <Loader2 className="w-5 h-5 mr-3 animate-spin" />
          Loading workflows...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="text-gray-600 mt-2">
            Manage and organize your automated workflows
          </p>
        </div>
        
        <button
          onClick={handleCreateNew}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Workflow
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search workflows..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            {currentUserId && (
              <>
                {sharingFilter === 'public' ? <Globe className="w-4 h-4 text-gray-500" /> : 
                 sharingFilter === 'private' ? <Lock className="w-4 h-4 text-gray-500" /> : 
                 <Filter className="w-4 h-4 text-gray-500" />}
                <select
                  value={sharingFilter}
                  onChange={(e) => setSharingFilter(e.target.value as any)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Workflows</option>
                  <option value="public">Public Only</option>
                  <option value="private">Private Only</option>
                </select>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Workflows Grid */}
      {filteredWorkflows.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <Activity className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {workflows.length === 0 ? 'No workflows yet' : 'No workflows match your filters'}
          </h3>
          <p className="text-gray-600 mb-6">
            {workflows.length === 0 
              ? 'Create your first workflow to get started with automation.'
              : 'Try adjusting your search or filter criteria.'
            }
          </p>
          {workflows.length === 0 && (
            <button
              onClick={handleCreateNew}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Workflow
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorkflows.map((workflow) => (
            <WorkflowCard key={workflow.id} workflow={workflow} />
          ))}
        </div>
      )}

      {/* Summary */}
      {filteredWorkflows.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-sm text-gray-600 gap-2">
            <span>
              Showing {filteredWorkflows.length} of {workflows.length} workflows
            </span>
            <div className="flex flex-wrap items-center gap-4">
              <span className="flex items-center">
                <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                {workflows.filter(w => w.status === 'active').length} active
              </span>
              <span className="flex items-center">
                <span className="inline-block w-2 h-2 rounded-full bg-gray-500 mr-2"></span>
                {workflows.filter(w => w.status === 'draft').length} drafts
              </span>
              <span className="flex items-center">
                <Globe className="w-3 h-3 mr-1 text-blue-500" />
                {workflows.filter(w => w.is_public).length} public
              </span>
              <span className="flex items-center">
                <Lock className="w-3 h-3 mr-1 text-gray-500" />
                {workflows.filter(w => !w.is_public).length} private
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Workflows;
