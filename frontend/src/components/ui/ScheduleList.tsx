import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Calendar, 
  Play, 
  Pause, 
  Trash2, 
  Edit, 
  MoreVertical, 
  Activity,
  AlertCircle,
  CheckCircle,
  Loader2,
  Filter,
  Search,
  X
} from 'lucide-react';
import type {
  Schedule,
  ScheduleStatus,
} from '../../types/scheduler';
import { SCHEDULE_STATUS_COLORS } from '../../types/scheduler';
import { apiService } from '../../services/api';
import type { ScheduleListItem } from '../../services/api';

interface ScheduleListProps {
  onEditSchedule?: (schedule: Schedule) => void;
  onCreateNew?: () => void;
  workflowId?: string; // Filter by specific workflow
}

interface ScheduleAction {
  id: string;
  type: 'pause' | 'resume' | 'delete';
  scheduleId: string;
}

const ScheduleList: React.FC<ScheduleListProps> = ({
  onEditSchedule,
  onCreateNew,
  workflowId
}) => {
  const [schedules, setSchedules] = useState<ScheduleListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'paused'>('all');
  const [actionLoading, setActionLoading] = useState<ScheduleAction | null>(null);

  // Load schedules
  const loadSchedules = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiService.listUserSchedules();
      
      // Filter by workflow if specified
      const filteredData = workflowId 
        ? data.filter(s => s.workflow_id === workflowId)
        : data;
      
      setSchedules(filteredData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schedules');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();
  }, [workflowId]);

  // Handle schedule actions
  const handleAction = async (action: ScheduleAction) => {
    try {
      setActionLoading(action);
      
      switch (action.type) {
        case 'pause':
          await apiService.pauseSchedule(action.scheduleId);
          break;
        case 'resume':
          await apiService.resumeSchedule(action.scheduleId);
          break;
        case 'delete':
          if (window.confirm('Are you sure you want to delete this schedule?')) {
            await apiService.deleteSchedule(action.scheduleId);
          } else {
            return;
          }
          break;
      }
      
      // Reload schedules after action
      await loadSchedules();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${action.type} schedule`);
    } finally {
      setActionLoading(null);
    }
  };

  // Filter schedules based on search and status
  const filteredSchedules = schedules.filter(schedule => {
    const matchesSearch = schedule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (schedule.description || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && schedule.is_active) ||
                         (statusFilter === 'paused' && !schedule.is_active);
    
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (isActive: boolean): string => {
    return isActive ? SCHEDULE_STATUS_COLORS.active : SCHEDULE_STATUS_COLORS.paused;
  };

  const formatNextRun = (dateString?: string): string => {
    if (!dateString) return 'Not scheduled';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    
    if (diffMs < 0) return 'Overdue';
    
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
      return `in ${diffDays} day${diffDays > 1 ? 's' : ''}`;
    } else if (diffHours > 0) {
      return `in ${diffHours} hour${diffHours > 1 ? 's' : ''}`;
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `in ${diffMinutes} minute${diffMinutes > 1 ? 's' : ''}`;
    }
  };

  const ScheduleCard: React.FC<{ schedule: ScheduleListItem }> = ({ schedule }) => {
    const [showActions, setShowActions] = useState(false);
    
    const isActionLoading = actionLoading?.scheduleId === schedule.schedule_id;
    const currentAction = actionLoading?.type;

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-lg font-medium text-gray-900">{schedule.name}</h3>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(schedule.is_active)}`}>
                {schedule.is_active ? 'Active' : 'Paused'}
              </span>
            </div>
            
            {schedule.description && (
              <p className="text-sm text-gray-600 mb-3">{schedule.description}</p>
            )}
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
              <div className="flex items-center text-gray-600">
                <Clock className="w-4 h-4 mr-2" />
                <span className="font-mono">{schedule.cron_expression}</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <Calendar className="w-4 h-4 mr-2" />
                <span>Next: {formatNextRun(schedule.next_execution_at)}</span>
              </div>
              
              <div className="flex items-center text-gray-600">
                <Activity className="w-4 h-4 mr-2" />
                <span>{schedule.execution_count} runs</span>
              </div>
            </div>
            
            <div className="mt-3 text-xs text-gray-500">
              Created: {new Date(schedule.created_at).toLocaleDateString()}
              {schedule.last_execution_at && (
                <span className="ml-4">
                  Last run: {new Date(schedule.last_execution_at).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
          
          <div className="relative ml-4">
            <button
              onClick={() => setShowActions(!showActions)}
              disabled={isActionLoading}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
            >
              {isActionLoading ? (
                <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
              ) : (
                <MoreVertical className="w-4 h-4 text-gray-500" />
              )}
            </button>
            
            {showActions && !isActionLoading && (
              <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10 min-w-[140px]">
                <button
                  onClick={() => {
                    setShowActions(false);
                    if (onEditSchedule) {
                      onEditSchedule({
                        id: schedule.schedule_id,
                        workflowId: schedule.workflow_id,
                        userId: 'default_user', // TODO: Get from auth
                        name: schedule.name,
                        description: schedule.description,
                        type: 'recurring', // TODO: Determine from cron_expression
                        status: schedule.is_active ? 'active' : 'paused',
                        cronExpression: schedule.cron_expression,
                        timezone: schedule.timezone,
                        createdAt: new Date(schedule.created_at),
                        updatedAt: new Date(schedule.created_at),
                        lastExecutionAt: schedule.last_execution_at ? new Date(schedule.last_execution_at) : undefined,
                        nextExecutionAt: schedule.next_execution_at ? new Date(schedule.next_execution_at) : undefined,
                        executionCount: schedule.execution_count,
                        backendType: schedule.backend_type,
                        backendJobId: schedule.schedule_id, // Using schedule_id as job_id
                        metadata: schedule.metadata
                      } as Schedule);
                    }
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </button>
                
                {schedule.is_active ? (
                  <button
                    onClick={() => {
                      setShowActions(false);
                      handleAction({
                        id: Date.now().toString(),
                        type: 'pause',
                        scheduleId: schedule.schedule_id
                      });
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      setShowActions(false);
                      handleAction({
                        id: Date.now().toString(),
                        type: 'resume',
                        scheduleId: schedule.schedule_id
                      });
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Resume
                  </button>
                )}
                
                <div className="border-t border-gray-100 my-1" />
                
                <button
                  onClick={() => {
                    setShowActions(false);
                    handleAction({
                      id: Date.now().toString(),
                      type: 'delete',
                      scheduleId: schedule.schedule_id
                    });
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
        
        {isActionLoading && (
          <div className="mt-3 flex items-center text-sm text-blue-600">
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            {currentAction === 'pause' && 'Pausing schedule...'}
            {currentAction === 'resume' && 'Resuming schedule...'}
            {currentAction === 'delete' && 'Deleting schedule...'}
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center text-gray-600">
          <Loader2 className="w-5 h-5 mr-3 animate-spin" />
          Loading schedules...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {workflowId ? 'Workflow Schedules' : 'All Schedules'}
          </h2>
          <p className="text-gray-600 mt-1">
            Manage your automated workflow executions
          </p>
        </div>
        
        {onCreateNew && (
          <button
            onClick={onCreateNew}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <Clock className="w-4 h-4 mr-2" />
            New Schedule
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search schedules..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
          </select>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
          <div className="flex items-center text-red-800">
            <AlertCircle className="w-5 h-5 mr-2" />
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-600 hover:text-red-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Schedule List */}
      {filteredSchedules.length === 0 ? (
        <div className="text-center py-12">
          <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {schedules.length === 0 ? 'No schedules yet' : 'No schedules match your filters'}
          </h3>
          <p className="text-gray-600 mb-4">
            {schedules.length === 0 
              ? 'Create your first automated workflow schedule to get started.'
              : 'Try adjusting your search or filter criteria.'
            }
          </p>
          {schedules.length === 0 && onCreateNew && (
            <button
              onClick={onCreateNew}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create First Schedule
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredSchedules.map((schedule) => (
            <ScheduleCard key={schedule.schedule_id} schedule={schedule} />
          ))}
        </div>
      )}

      {/* Summary */}
      {filteredSchedules.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              Showing {filteredSchedules.length} of {schedules.length} schedules
            </span>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                <span>{schedules.filter(s => s.is_active).length} active</span>
              </div>
              <div className="flex items-center">
                <Pause className="w-4 h-4 text-yellow-500 mr-1" />
                <span>{schedules.filter(s => !s.is_active).length} paused</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScheduleList;
