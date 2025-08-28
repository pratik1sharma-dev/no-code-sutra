/**
 * Comprehensive TypeScript types for the scheduling system
 */

export type ScheduleType = 'recurring' | 'one_time';
export type ScheduleStatus = 'active' | 'paused' | 'completed' | 'failed' | 'cancelled';
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

// Cron Expression Builder Types
export interface CronField {
  minute: string;
  hour: string;
  dayOfMonth: string;
  month: string;
  dayOfWeek: string;
}

export interface CronPreset {
  id: string;
  label: string;
  description: string;
  expression: string;
  category: 'common' | 'daily' | 'weekly' | 'monthly';
}

export interface CronBuilderState {
  mode: 'preset' | 'custom' | 'advanced';
  preset?: string;
  fields: CronField;
  expression: string;
  isValid: boolean;
  nextRuns: Date[];
}

// Schedule Configuration Types
export interface BaseScheduleConfig {
  name: string;
  description?: string;
  timezone: string;
  metadata?: Record<string, any>;
}

export interface RecurringScheduleConfig extends BaseScheduleConfig {
  type: 'recurring';
  cronExpression: string;
  endDate?: Date;
  maxExecutions?: number;
}

export interface OneTimeScheduleConfig extends BaseScheduleConfig {
  type: 'one_time';
  runAt: Date;
}

export type ScheduleConfig = RecurringScheduleConfig | OneTimeScheduleConfig;

// Schedule Entity Types
export interface Schedule {
  id: string;
  workflowId: string;
  userId: string;
  name: string;
  description?: string;
  type: ScheduleType;
  status: ScheduleStatus;
  
  // Timing
  cronExpression?: string; // For recurring schedules
  runAt?: Date; // For one-time schedules
  timezone: string;
  
  // Execution tracking
  createdAt: Date;
  updatedAt: Date;
  lastExecutionAt?: Date;
  nextExecutionAt?: Date;
  executionCount: number;
  
  // Backend details
  backendType: string;
  backendJobId: string;
  
  // Additional data
  metadata?: Record<string, any>;
}

// Execution Types
export interface ScheduledExecution {
  id: string;
  scheduleId: string;
  workflowId: string;
  userId: string;
  
  // Status and timing
  status: ExecutionStatus;
  startedAt: Date;
  completedAt?: Date;
  durationMs?: number;
  
  // Results
  success?: boolean;
  error?: string;
  nodeResults?: Record<string, any>;
  nodeResultsCount: number;
  
  // Metadata
  executionType: 'scheduled' | 'manual';
  triggerInfo?: {
    scheduledTime: Date;
    actualTime: Date;
    delay: number;
  };
}

// UI State Types
export interface ScheduleFormState {
  workflowId: string;
  config: Partial<ScheduleConfig>;
  isValid: boolean;
  errors: Record<string, string>;
  isSubmitting: boolean;
}

export interface ScheduleListState {
  schedules: Schedule[];
  isLoading: boolean;
  error?: string;
  filters: {
    status?: ScheduleStatus[];
    type?: ScheduleType[];
    workflowId?: string;
  };
  sortBy: 'name' | 'createdAt' | 'nextExecutionAt' | 'executionCount';
  sortOrder: 'asc' | 'desc';
}

export interface ExecutionHistoryState {
  executions: ScheduledExecution[];
  isLoading: boolean;
  error?: string;
  workflowId?: string;
  pagination: {
    page: number;
    limit: number;
    total: number;
  };
}

// Component Props Types
export interface ScheduleCardProps {
  schedule: Schedule;
  onEdit: (schedule: Schedule) => void;
  onPause: (scheduleId: string) => void;
  onResume: (scheduleId: string) => void;
  onDelete: (scheduleId: string) => void;
  onViewHistory: (workflowId: string) => void;
}

export interface CronBuilderProps {
  value: string;
  onChange: (expression: string) => void;
  timezone?: string;
  showPreview?: boolean;
  className?: string;
}

export interface ScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  workflowId?: string;
  schedule?: Schedule; // For editing
  onSave: (config: ScheduleConfig) => Promise<void>;
}

export interface ExecutionHistoryProps {
  workflowId: string;
  limit?: number;
  showScheduleInfo?: boolean;
}

// Utility Types
export interface ScheduleValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
  warnings?: string[];
}

export interface ScheduleMetrics {
  totalSchedules: number;
  activeSchedules: number;
  pausedSchedules: number;
  totalExecutions24h: number;
  successRate24h: number;
  avgExecutionTime: number;
  upcomingExecutions: Array<{
    scheduleId: string;
    scheduleName: string;
    nextRun: Date;
  }>;
}

// Hook Return Types
export interface UseScheduleListReturn {
  schedules: Schedule[];
  isLoading: boolean;
  error?: string;
  refresh: () => Promise<void>;
  createSchedule: (config: ScheduleConfig, workflowId: string) => Promise<void>;
  updateSchedule: (scheduleId: string, updates: Partial<ScheduleConfig>) => Promise<void>;
  pauseSchedule: (scheduleId: string) => Promise<void>;
  resumeSchedule: (scheduleId: string) => Promise<void>;
  deleteSchedule: (scheduleId: string) => Promise<void>;
}

export interface UseExecutionHistoryReturn {
  executions: ScheduledExecution[];
  isLoading: boolean;
  error?: string;
  refresh: () => Promise<void>;
  loadMore: () => Promise<void>;
  hasMore: boolean;
}

export interface UseCronBuilderReturn {
  state: CronBuilderState;
  setMode: (mode: CronBuilderState['mode']) => void;
  setPreset: (presetId: string) => void;
  setField: (field: keyof CronField, value: string) => void;
  setExpression: (expression: string) => void;
  validate: () => boolean;
  getNextRuns: (count?: number) => Date[];
  reset: () => void;
}

// Constants
export const CRON_PRESETS: CronPreset[] = [
  {
    id: 'every_minute',
    label: 'Every minute',
    description: 'Runs every minute',
    expression: '* * * * *',
    category: 'common'
  },
  {
    id: 'every_5_minutes',
    label: 'Every 5 minutes',
    description: 'Runs every 5 minutes',
    expression: '*/5 * * * *',
    category: 'common'
  },
  {
    id: 'every_15_minutes',
    label: 'Every 15 minutes',
    description: 'Runs every 15 minutes',
    expression: '*/15 * * * *',
    category: 'common'
  },
  {
    id: 'every_hour',
    label: 'Every hour',
    description: 'Runs at the top of every hour',
    expression: '0 * * * *',
    category: 'common'
  },
  {
    id: 'daily_9am',
    label: 'Daily at 9:00 AM',
    description: 'Runs every day at 9:00 AM',
    expression: '0 9 * * *',
    category: 'daily'
  },
  {
    id: 'daily_6pm',
    label: 'Daily at 6:00 PM',
    description: 'Runs every day at 6:00 PM',
    expression: '0 18 * * *',
    category: 'daily'
  },
  {
    id: 'weekdays_9am',
    label: 'Weekdays at 9:00 AM',
    description: 'Runs Monday through Friday at 9:00 AM',
    expression: '0 9 * * 1-5',
    category: 'daily'
  },
  {
    id: 'weekly_monday_9am',
    label: 'Weekly on Monday at 9:00 AM',
    description: 'Runs every Monday at 9:00 AM',
    expression: '0 9 * * 1',
    category: 'weekly'
  },
  {
    id: 'weekly_friday_5pm',
    label: 'Weekly on Friday at 5:00 PM',
    description: 'Runs every Friday at 5:00 PM',
    expression: '0 17 * * 5',
    category: 'weekly'
  },
  {
    id: 'monthly_1st_9am',
    label: 'Monthly on 1st at 9:00 AM',
    description: 'Runs on the 1st day of every month at 9:00 AM',
    expression: '0 9 1 * *',
    category: 'monthly'
  },
  {
    id: 'monthly_15th_12pm',
    label: 'Monthly on 15th at 12:00 PM',
    description: 'Runs on the 15th day of every month at 12:00 PM',
    expression: '0 12 15 * *',
    category: 'monthly'
  }
];

export const TIMEZONE_OPTIONS = [
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
  { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
  { value: 'America/Chicago', label: 'Central Time (US & Canada)' },
  { value: 'America/Denver', label: 'Mountain Time (US & Canada)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (US & Canada)' },
  { value: 'Europe/London', label: 'London (GMT/BST)' },
  { value: 'Europe/Paris', label: 'Paris (CET/CEST)' },
  { value: 'Europe/Berlin', label: 'Berlin (CET/CEST)' },
  { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
  { value: 'Asia/Shanghai', label: 'Shanghai (CST)' },
  { value: 'Asia/Kolkata', label: 'India (IST)' },
  { value: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)' }
];

export const SCHEDULE_STATUS_COLORS: Record<ScheduleStatus, string> = {
  active: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-blue-100 text-blue-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800'
};

export const EXECUTION_STATUS_COLORS: Record<ExecutionStatus, string> = {
  pending: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-yellow-100 text-yellow-800'
};
