import React, { useState, useEffect, useMemo } from 'react';
import { Clock, Calendar, Info, ChevronDown, ChevronRight } from 'lucide-react';
import type {
  CronBuilderProps,
  CronBuilderState,
  CronPreset,
} from '../../types/scheduler';
import { CRON_PRESETS, TIMEZONE_OPTIONS } from '../../types/scheduler';

const CronBuilder: React.FC<CronBuilderProps> = ({
  value,
  onChange,
  timezone = 'UTC',
  showPreview = true,
  className = ''
}) => {
  const [state, setState] = useState<CronBuilderState>({
    mode: 'preset',
    fields: {
      minute: '0',
      hour: '9',
      dayOfMonth: '*',
      month: '*',
      dayOfWeek: '*'
    },
    expression: value || '0 9 * * *',
    isValid: true,
    nextRuns: []
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  // Parse incoming cron expression
  useEffect(() => {
    if (value && value !== state.expression) {
      const parts = value.split(' ');
      if (parts.length === 5) {
        setState(prev => ({
          ...prev,
          expression: value,
          fields: {
            minute: parts[0],
            hour: parts[1],
            dayOfMonth: parts[2],
            month: parts[3],
            dayOfWeek: parts[4]
          },
          mode: CRON_PRESETS.find(p => p.expression === value) ? 'preset' : 'custom'
        }));
      }
    }
  }, [value]);

  // Calculate next run times (simplified calculation)
  const nextRuns = useMemo(() => {
    try {
      // This is a simplified preview - in production you'd use a proper cron library
      const now = new Date();
      const runs: Date[] = [];
      
      // Generate next 5 runs (simplified logic)
      for (let i = 1; i <= 5; i++) {
        const next = new Date(now);
        
        // Simple daily schedule preview
        if (state.expression === '0 9 * * *') {
          next.setDate(now.getDate() + i);
          next.setHours(9, 0, 0, 0);
        } else if (state.expression === '0 18 * * *') {
          next.setDate(now.getDate() + i);
          next.setHours(18, 0, 0, 0);
        } else if (state.expression === '0 9 * * 1-5') {
          // Weekdays only
          let daysToAdd = i;
          const nextDate = new Date(now);
          nextDate.setDate(now.getDate() + daysToAdd);
          while (nextDate.getDay() === 0 || nextDate.getDay() === 6) {
            daysToAdd++;
            nextDate.setDate(now.getDate() + daysToAdd);
          }
          nextDate.setHours(9, 0, 0, 0);
          runs.push(nextDate);
          continue;
        } else {
          // Default: add hours
          next.setHours(now.getHours() + i);
        }
        
        runs.push(next);
      }
      
      return runs;
    } catch {
      return [];
    }
  }, [state.expression, timezone]);

  const handleModeChange = (mode: CronBuilderState['mode']) => {
    setState(prev => ({ ...prev, mode }));
  };

  const handlePresetSelect = (preset: CronPreset) => {
    const newExpression = preset.expression;
    setState(prev => ({
      ...prev,
      preset: preset.id,
      expression: newExpression,
      isValid: true
    }));
    onChange(newExpression);
  };

  const handleFieldChange = (field: keyof typeof state.fields, fieldValue: string) => {
    const newFields = { ...state.fields, [field]: fieldValue };
    const newExpression = `${newFields.minute} ${newFields.hour} ${newFields.dayOfMonth} ${newFields.month} ${newFields.dayOfWeek}`;
    
    setState(prev => ({
      ...prev,
      fields: newFields,
      expression: newExpression,
      isValid: validateCronExpression(newExpression)
    }));
    
    onChange(newExpression);
  };

  const handleExpressionChange = (expression: string) => {
    setState(prev => ({
      ...prev,
      expression,
      isValid: validateCronExpression(expression),
      mode: 'advanced'
    }));
    onChange(expression);
  };

  const validateCronExpression = (expression: string): boolean => {
    const parts = expression.trim().split(/\s+/);
    return parts.length === 5;
  };

  const presetsByCategory = useMemo(() => {
    return CRON_PRESETS.reduce((acc, preset) => {
      if (!acc[preset.category]) {
        acc[preset.category] = [];
      }
      acc[preset.category].push(preset);
      return acc;
    }, {} as Record<string, CronPreset[]>);
  }, []);

  const selectedPreset = CRON_PRESETS.find(p => p.expression === state.expression);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Mode Selection */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {(['preset', 'custom', 'advanced'] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => handleModeChange(mode)}
            className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              state.mode === mode
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {mode === 'preset' && 'Quick Select'}
            {mode === 'custom' && 'Custom'}
            {mode === 'advanced' && 'Advanced'}
          </button>
        ))}
      </div>

      {/* Preset Mode */}
      {state.mode === 'preset' && (
        <div className="space-y-3">
          {Object.entries(presetsByCategory).map(([category, presets]) => (
            <div key={category}>
              <h4 className="text-sm font-medium text-gray-700 mb-2 capitalize">
                {category.replace('_', ' ')} Schedules
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {presets.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => handlePresetSelect(preset)}
                    className={`text-left p-3 rounded-lg border transition-colors ${
                      selectedPreset?.id === preset.id
                        ? 'border-blue-500 bg-blue-50 text-blue-900'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-sm">{preset.label}</div>
                    <div className="text-xs text-gray-500 mt-1">{preset.description}</div>
                    <div className="text-xs font-mono text-gray-400 mt-1">{preset.expression}</div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Custom Mode */}
      {state.mode === 'custom' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Minute</label>
              <select
                value={state.fields.minute}
                onChange={(e) => handleFieldChange('minute', e.target.value)}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="*">Every minute</option>
                <option value="0">:00</option>
                <option value="15">:15</option>
                <option value="30">:30</option>
                <option value="45">:45</option>
                <option value="*/5">Every 5 min</option>
                <option value="*/15">Every 15 min</option>
                <option value="*/30">Every 30 min</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Hour</label>
              <select
                value={state.fields.hour}
                onChange={(e) => handleFieldChange('hour', e.target.value)}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="*">Every hour</option>
                {Array.from({ length: 24 }, (_, i) => (
                  <option key={i} value={i.toString()}>
                    {i.toString().padStart(2, '0')}:00
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Day</label>
              <select
                value={state.fields.dayOfMonth}
                onChange={(e) => handleFieldChange('dayOfMonth', e.target.value)}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="*">Every day</option>
                {Array.from({ length: 31 }, (_, i) => (
                  <option key={i + 1} value={(i + 1).toString()}>
                    {i + 1}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Month</label>
              <select
                value={state.fields.month}
                onChange={(e) => handleFieldChange('month', e.target.value)}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="*">Every month</option>
                <option value="1">January</option>
                <option value="2">February</option>
                <option value="3">March</option>
                <option value="4">April</option>
                <option value="5">May</option>
                <option value="6">June</option>
                <option value="7">July</option>
                <option value="8">August</option>
                <option value="9">September</option>
                <option value="10">October</option>
                <option value="11">November</option>
                <option value="12">December</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Day of Week</label>
              <select
                value={state.fields.dayOfWeek}
                onChange={(e) => handleFieldChange('dayOfWeek', e.target.value)}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="*">Every day</option>
                <option value="1-5">Weekdays</option>
                <option value="0,6">Weekends</option>
                <option value="0">Sunday</option>
                <option value="1">Monday</option>
                <option value="2">Tuesday</option>
                <option value="3">Wednesday</option>
                <option value="4">Thursday</option>
                <option value="5">Friday</option>
                <option value="6">Saturday</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Advanced Mode */}
      {state.mode === 'advanced' && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cron Expression
            </label>
            <input
              type="text"
              value={state.expression}
              onChange={(e) => handleExpressionChange(e.target.value)}
              placeholder="0 9 * * *"
              className={`w-full px-3 py-2 font-mono text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                state.isValid ? 'border-gray-300' : 'border-red-300 bg-red-50'
              }`}
            />
            {!state.isValid && (
              <p className="mt-1 text-xs text-red-600">
                Invalid cron expression. Must have 5 fields: minute hour day month day-of-week
              </p>
            )}
          </div>

          <div className="bg-gray-50 p-3 rounded-lg">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center text-sm text-gray-600 hover:text-gray-900"
            >
              {showAdvanced ? <ChevronDown className="w-4 h-4 mr-1" /> : <ChevronRight className="w-4 h-4 mr-1" />}
              Cron Expression Help
            </button>
            {showAdvanced && (
              <div className="mt-3 text-xs text-gray-600 space-y-1">
                <div className="font-mono">* * * * *</div>
                <div>│ │ │ │ └─ Day of Week (0-6, Sunday=0)</div>
                <div>│ │ │ └─── Month (1-12)</div>
                <div>│ │ └───── Day of Month (1-31)</div>
                <div>│ └─────── Hour (0-23)</div>
                <div>└───────── Minute (0-59)</div>
                <div className="mt-2">
                  <strong>Examples:</strong>
                  <div>0 9 * * * = Daily at 9:00 AM</div>
                  <div>0 9 * * 1-5 = Weekdays at 9:00 AM</div>
                  <div>*/15 * * * * = Every 15 minutes</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Current Expression Display */}
      <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg">
        <div className="flex items-center text-sm text-blue-800">
          <Clock className="w-4 h-4 mr-2" />
          <span className="font-medium">Expression: </span>
          <code className="ml-1 font-mono bg-blue-100 px-2 py-1 rounded text-xs">
            {state.expression}
          </code>
        </div>
        {selectedPreset && (
          <div className="mt-1 text-xs text-blue-600">
            {selectedPreset.description}
          </div>
        )}
      </div>

      {/* Preview */}
      {showPreview && nextRuns.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 p-3 rounded-lg">
          <div className="flex items-center text-sm text-gray-700 mb-2">
            <Calendar className="w-4 h-4 mr-2" />
            <span className="font-medium">Next 5 runs ({timezone}):</span>
          </div>
          <div className="space-y-1">
            {nextRuns.slice(0, 5).map((date, index) => (
              <div key={index} className="text-xs text-gray-600 font-mono">
                {date.toLocaleString('en-US', {
                  timeZone: timezone,
                  weekday: 'short',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  timeZoneName: 'short'
                })}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Validation Status */}
      {!state.isValid && (
        <div className="flex items-center text-sm text-red-600 bg-red-50 border border-red-200 p-3 rounded-lg">
          <Info className="w-4 h-4 mr-2 flex-shrink-0" />
          Please fix the cron expression above
        </div>
      )}
    </div>
  );
};

export default CronBuilder;
