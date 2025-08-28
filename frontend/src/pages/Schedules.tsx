import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, Activity, AlertTriangle } from 'lucide-react';
import ScheduleList from '../components/ui/ScheduleList';
import ScheduleModal from '../components/ui/ScheduleModal';
import { Schedule, ScheduleConfig } from '../types/scheduler';
import { apiService, SchedulerStatusResponse } from '../services/api';

const Schedules: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatusResponse | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Load scheduler status
  useEffect(() => {
    const loadSchedulerStatus = async () => {
      try {
        const status = await apiService.getSchedulerStatus();
        setSchedulerStatus(status);
      } catch (error) {
        console.error('Failed to load scheduler status:', error);
      }
    };

    loadSchedulerStatus();
    
    // Refresh status every 30 seconds
    const interval = setInterval(loadSchedulerStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateSchedule = async (config: ScheduleConfig) => {
    try {
      if (config.type === 'recurring') {
        await apiService.createRecurringSchedule({
          workflow_id: 'default-workflow', // TODO: Get from context or selection
          name: config.name,
          cron_expression: config.cronExpression,
          timezone: config.timezone,
          description: config.description,
          metadata: config.metadata
        });
      } else {
        await apiService.createOneTimeSchedule({
          workflow_id: 'default-workflow', // TODO: Get from context or selection
          name: config.name,
          run_at: config.runAt.toISOString(),
          description: config.description,
          metadata: config.metadata
        });
      }
      
      // Refresh the list
      setRefreshKey(prev => prev + 1);
    } catch (error) {
      throw error; // Let the modal handle the error
    }
  };

  const handleEditSchedule = async (config: ScheduleConfig) => {
    // TODO: Implement schedule editing
    // For now, just close the modal
    setEditingSchedule(null);
    setRefreshKey(prev => prev + 1);
  };

  const StatusCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ElementType;
    color: string;
    description?: string;
  }> = ({ title, value, icon: Icon, color, description }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-gray-200 pb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Schedules</h1>
            <p className="text-gray-600 mt-2">
              Manage automated workflow executions and monitor scheduler performance
            </p>
          </div>
          
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <Clock className="w-4 h-4 mr-2" />
            New Schedule
          </button>
        </div>
      </div>

      {/* Status Cards */}
      {schedulerStatus && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatusCard
            title="Active Schedules"
            value={schedulerStatus.active_schedules}
            icon={Clock}
            color="bg-blue-500"
            description="Currently running"
          />
          
          <StatusCard
            title="24h Executions"
            value={schedulerStatus.executions_24h}
            icon={Activity}
            color="bg-green-500"
            description="Past 24 hours"
          />
          
          <StatusCard
            title="Success Rate"
            value={`${schedulerStatus.success_rate_24h}%`}
            icon={TrendingUp}
            color="bg-purple-500"
            description="Last 24 hours"
          />
          
          <StatusCard
            title="Scheduler Status"
            value={schedulerStatus.status === 'healthy' ? 'Healthy' : 'Issues'}
            icon={schedulerStatus.status === 'healthy' ? Activity : AlertTriangle}
            color={schedulerStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}
            description={`Backend: ${schedulerStatus.backend}`}
          />
        </div>
      )}

      {/* Scheduler Health Alert */}
      {schedulerStatus && schedulerStatus.status !== 'healthy' && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-500 mr-3" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Scheduler Issues Detected</h3>
              <p className="text-sm text-red-700 mt-1">
                {schedulerStatus.error || 'The scheduler is experiencing problems. Some schedules may not execute as expected.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Schedule List */}
      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="p-6">
          <ScheduleList
            key={refreshKey}
            onEditSchedule={setEditingSchedule}
            onCreateNew={() => setShowCreateModal(true)}
          />
        </div>
      </div>

      {/* Create Schedule Modal */}
      <ScheduleModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSave={handleCreateSchedule}
      />

      {/* Edit Schedule Modal */}
      <ScheduleModal
        isOpen={!!editingSchedule}
        onClose={() => setEditingSchedule(null)}
        schedule={editingSchedule || undefined}
        onSave={handleEditSchedule}
      />
    </div>
  );
};

export default Schedules;
