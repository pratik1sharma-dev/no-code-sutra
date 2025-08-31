import React, { useState } from 'react';
import { Globe, Lock, Share2, Check } from 'lucide-react';

interface WorkflowSharingControlsProps {
  isPublic: boolean;
  onTogglePublic: (isPublic: boolean) => void;
  disabled?: boolean;
}

const WorkflowSharingControls: React.FC<WorkflowSharingControlsProps> = ({
  isPublic,
  onTogglePublic,
  disabled = false
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const handleToggle = () => {
    if (!disabled) {
      onTogglePublic(!isPublic);
      
      // Show confirmation tooltip briefly
      setShowTooltip(true);
      setTimeout(() => setShowTooltip(false), 2000);
    }
  };

  return (
    <div className="relative">
      <div className="flex items-center gap-3">
        <button
          onClick={handleToggle}
          disabled={disabled}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isPublic
              ? 'bg-green-100 text-green-800 hover:bg-green-200'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isPublic ? (
            <>
              <Globe className="w-4 h-4" />
              Public
            </>
          ) : (
            <>
              <Lock className="w-4 h-4" />
              Private
            </>
          )}
        </button>
        
        <button
          className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors"
          onClick={() => {
            if (navigator.clipboard) {
              navigator.clipboard.writeText(window.location.href);
              setShowTooltip(true);
              setTimeout(() => setShowTooltip(false), 2000);
            }
          }}
        >
          <Share2 className="w-4 h-4" />
          Share Link
        </button>
      </div>
      
      {showTooltip && (
        <div className="absolute top-full mt-2 left-0 bg-gray-800 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
          <Check className="w-3 h-3" />
          {isPublic ? 'Workflow is now public' : navigator.clipboard ? 'Link copied to clipboard' : 'Workflow is now private'}
        </div>
      )}
    </div>
  );
};

export default WorkflowSharingControls;
