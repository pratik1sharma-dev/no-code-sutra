import React from 'react';
import { 
  Workflow, 
  Play, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Clock,
  Users
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const stats = [
    {
      name: 'Total Workflows',
      value: '24',
      change: '+12%',
      changeType: 'positive',
      icon: Workflow,
    },
    {
      name: 'Active Executions',
      value: '8',
      change: '+3',
      changeType: 'positive',
      icon: Play,
    },
    {
      name: 'Success Rate',
      value: '94.2%',
      change: '+2.1%',
      changeType: 'positive',
      icon: CheckCircle,
    },
    {
      name: 'Failed Executions',
      value: '3',
      change: '-1',
      changeType: 'negative',
      icon: AlertCircle,
    },
  ];

  const recentWorkflows = [
    {
      id: '1',
      name: 'Lead Qualification',
      status: 'completed',
      lastRun: '2 hours ago',
      successRate: '98%',
    },
    {
      id: '2',
      name: 'Content Generation',
      status: 'running',
      lastRun: '5 minutes ago',
      successRate: '95%',
    },
    {
      id: '3',
      name: 'Email Campaign',
      status: 'failed',
      lastRun: '1 hour ago',
      successRate: '87%',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-cormorant font-semibold text-secondary-900">
          Dashboard
        </h1>
        <p className="text-secondary-600 mt-2">
          Welcome back! Here's what's happening with your workflows.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="card-content">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-600">
                      {stat.name}
                    </p>
                    <p className="text-2xl font-semibold text-secondary-900">
                      {stat.value}
                    </p>
                  </div>
                  <div className="p-2 bg-primary-50 rounded-lg">
                    <Icon className="h-6 w-6 text-primary-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <TrendingUp className={`h-4 w-4 ${
                    stat.changeType === 'positive' ? 'text-success-500' : 'text-danger-500'
                  }`} />
                  <span className={`ml-1 text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {stat.change}
                  </span>
                  <span className="ml-2 text-sm text-secondary-500">
                    from last month
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Workflows */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Workflows</h2>
          <p className="card-description">
            Your most recently executed workflows
          </p>
        </div>
        <div className="card-content">
          <div className="space-y-4">
            {recentWorkflows.map((workflow) => (
              <div
                key={workflow.id}
                className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-primary-50 rounded-lg">
                    <Workflow className="h-5 w-5 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-secondary-900">
                      {workflow.name}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-secondary-500">
                      <span className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {workflow.lastRun}
                      </span>
                      <span className="flex items-center">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        {workflow.successRate} success rate
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    workflow.status === 'completed'
                      ? 'bg-success-100 text-success-800'
                      : workflow.status === 'running'
                      ? 'bg-primary-100 text-primary-800'
                      : 'bg-danger-100 text-danger-800'
                  }`}>
                    {workflow.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 