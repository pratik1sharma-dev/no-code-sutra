import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Workflow, 
  Settings, 
  BarChart3, 
  Users, 
  FileText,
  Plus
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Workflows', href: '/workflows', icon: Workflow },
    { name: 'Templates', href: '/templates', icon: FileText },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Team', href: '/team', icon: Users },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <div className="w-64 bg-white border-r border-secondary-200 flex flex-col">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 border-b border-secondary-200">
        <h1 className="text-2xl font-cormorant font-semibold text-primary-600">
          No Code Sutra
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                    : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                }`
              }
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>

      {/* Create New Workflow Button */}
      <div className="p-4 border-t border-secondary-200">
        <NavLink
          to="/workflow"
          className="flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Workflow
        </NavLink>
      </div>
    </div>
  );
};

export default Sidebar; 