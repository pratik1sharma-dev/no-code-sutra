import React, { useState, useEffect } from 'react';
import { Clock, ChevronDown, History, Check } from 'lucide-react';
import { WorkflowVersion, WorkflowVersionsResponse } from '../../services/api';
import apiService from '../../services/api';

interface WorkflowVersionSelectorProps {
  workflowId: string;
  currentVersion?: number;
  onVersionChange: (version: WorkflowVersion) => void;
}

const WorkflowVersionSelector: React.FC<WorkflowVersionSelectorProps> = ({
  workflowId,
  currentVersion,
  onVersionChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [versions, setVersions] = useState<WorkflowVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<WorkflowVersion | null>(null);

  useEffect(() => {
    if (workflowId) {
      loadVersions();
    }
  }, [workflowId]);

  const loadVersions = async () => {
    setLoading(true);
    try {
      const response = await apiService.getWorkflowVersions(workflowId, false);
      setVersions(response.versions);
      
      // Set the current version as selected
      const current = response.versions.find(v => 
        (currentVersion && v.version === currentVersion) || v.is_current
      );
      if (current) {
        setSelectedVersion(current);
      }
    } catch (error) {
      console.error('Failed to load workflow versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectVersion = (version: WorkflowVersion) => {
    setSelectedVersion(version);
    onVersionChange(version);
    setIsOpen(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (!workflowId) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        disabled={loading}
      >
        <History className="w-4 h-4 text-gray-600" />
        {loading ? (
          'Loading versions...'
        ) : (
          <>
            {selectedVersion ? (
              <>Version {selectedVersion.version}</>
            ) : (
              <>Select Version</>
            )}
            <ChevronDown className="w-4 h-4 ml-1" />
          </>
        )}
      </button>

      {isOpen && (
        <div className="absolute z-10 mt-1 w-64 bg-white border border-gray-200 rounded-md shadow-lg">
          <div className="py-1 max-h-60 overflow-y-auto">
            {versions.length === 0 ? (
              <div className="px-4 py-2 text-sm text-gray-500">No versions available</div>
            ) : (
              versions.map((version) => (
                <button
                  key={version.id}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center justify-between ${
                    selectedVersion?.id === version.id ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleSelectVersion(version)}
                >
                  <div>
                    <div className="font-medium">Version {version.version}</div>
                    <div className="text-xs text-gray-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(version.updated_at)}
                    </div>
                  </div>
                  {selectedVersion?.id === version.id && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowVersionSelector;
