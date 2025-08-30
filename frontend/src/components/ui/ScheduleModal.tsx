import React, { useState, useEffect } from 'react';
import { X, Clock, Calendar, AlertTriangle, Check, Loader2 } from 'lucide-react';
import CronBuilder from './CronBuilder';
import type {
  ScheduleModalProps,
  ScheduleConfig,
  RecurringScheduleConfig,
  OneTimeScheduleConfig,
} from '../../types/scheduler';
import { TIMEZONE_OPTIONS } from '../../types/scheduler';

const ScheduleModal: React.FC<ScheduleModalProps> = ({
  isOpen,
  onClose,
  workflowId,
  schedule,
  onSave
}) => {
  const [scheduleType, setScheduleType] = useState<'recurring' | 'one_time'>('recurring');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    timezone: 'UTC',
    cronExpression: '0 9 * * *',
    runAt: '',
    metadata: {}
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form when modal opens or schedule changes
  useEffect(() => {
    if (isOpen) {
      if (schedule) {
        // Edit mode
        setScheduleType(schedule.type === 'recurring' ? 'recurring' : 'one_time');
        setFormData({
          name: schedule.name,
          description: schedule.description || '',
          timezone: schedule.timezone,
          cronExpression: (schedule as any).cronExpression || '0 9 * * *',
          runAt: (schedule as any).runAt ? new Date((schedule as any).runAt).toISOString().slice(0, 16) : '',
          metadata: schedule.metadata || {}
        });
      } else {
        // Create mode - reset form
        setScheduleType('recurring');
        setFormData({
          name: '',
          description: '',
          timezone: 'UTC',
          cronExpression: '0 9 * * *',
          runAt: '',
          metadata: {}
        });
      }
      setErrors({});
      setIsSubmitting(false);
    }
  }, [isOpen, schedule]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Schedule name is required';
    }

    if (scheduleType === 'recurring') {
      if (!formData.cronExpression.trim()) {
        newErrors.cronExpression = 'Cron expression is required';
      } else {
        const parts = formData.cronExpression.trim().split(/\s+/);
        if (parts.length !== 5) {
          newErrors.cronExpression = 'Invalid cron expression format';
        }
      }
    } else {
      if (!formData.runAt) {
        newErrors.runAt = 'Run time is required';
      } else {
        const runTime = new Date(formData.runAt);
        if (runTime <= new Date()) {
          newErrors.runAt = 'Run time must be in the future';
        }
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      let config: ScheduleConfig;

      if (scheduleType === 'recurring') {
        config = {
          type: 'recurring',
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          timezone: formData.timezone,
          cronExpression: formData.cronExpression.trim(),
          metadata: formData.metadata
        } as RecurringScheduleConfig;
      } else {
        config = {
          type: 'one_time',
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          timezone: formData.timezone,
          runAt: new Date(formData.runAt),
          metadata: formData.metadata
        } as OneTimeScheduleConfig;
      }

      await onSave(config);
      onClose();
    } catch (error) {
      setErrors({
        submit: error instanceof Error ? error.message : 'Failed to save schedule'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {schedule ? 'Edit Schedule' : 'Create Schedule'}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {workflowId ? `For workflow: ${workflowId.slice(0, 8)}...` : 'Set up automated workflow execution'}
            </p>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[calc(90vh-140px)] overflow-y-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Schedule Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Schedule Type
              </label>
              <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                <button
                  type="button"
                  onClick={() => setScheduleType('recurring')}
                  className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    scheduleType === 'recurring'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Clock className="w-4 h-4 inline mr-2" />
                  Recurring
                </button>
                <button
                  type="button"
                  onClick={() => setScheduleType('one_time')}
                  className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    scheduleType === 'one_time'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Calendar className="w-4 h-4 inline mr-2" />
                  One Time
                </button>
              </div>
            </div>

            {/* Basic Information */}
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Schedule Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Daily Instagram Posts"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.name ? 'border-red-300 bg-red-50' : 'border-gray-300'
                  }`}
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Optional description of what this schedule does..."
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timezone
                </label>
                <select
                  value={formData.timezone}
                  onChange={(e) => setFormData(prev => ({ ...prev, timezone: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {TIMEZONE_OPTIONS.map((tz) => (
                    <option key={tz.value} value={tz.value}>
                      {tz.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Schedule Configuration */}
            {scheduleType === 'recurring' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Schedule Pattern *
                </label>
                <CronBuilder
                  value={formData.cronExpression}
                  onChange={(expression) => setFormData(prev => ({ ...prev, cronExpression: expression }))}
                  timezone={formData.timezone}
                  showPreview={true}
                />
                {errors.cronExpression && (
                  <p className="mt-2 text-sm text-red-600">{errors.cronExpression}</p>
                )}
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Run At *
                </label>
                <input
                  type="datetime-local"
                  value={formData.runAt}
                  onChange={(e) => setFormData(prev => ({ ...prev, runAt: e.target.value }))}
                  min={new Date().toISOString().slice(0, 16)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.runAt ? 'border-red-300 bg-red-50' : 'border-gray-300'
                  }`}
                />
                {errors.runAt && (
                  <p className="mt-1 text-sm text-red-600">{errors.runAt}</p>
                )}
                {formData.runAt && (
                  <p className="mt-1 text-xs text-gray-500">
                    Will run: {new Date(formData.runAt).toLocaleString('en-US', {
                      timeZone: formData.timezone,
                      weekday: 'long',
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                      timeZoneName: 'short'
                    })}
                  </p>
                )}
              </div>
            )}

            {/* Error Display */}
            {errors.submit && (
              <div className="bg-red-50 border border-red-200 p-3 rounded-lg">
                <div className="flex items-center text-red-800">
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  <span className="text-sm">{errors.submit}</span>
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Check className="w-4 h-4 mr-2" />
                {schedule ? 'Update Schedule' : 'Create Schedule'}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ScheduleModal;
