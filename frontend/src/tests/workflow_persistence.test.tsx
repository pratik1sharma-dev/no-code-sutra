import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';

import Workflows from '../pages/Workflows';
import WorkflowPreview from '../components/ui/WorkflowPreview';
import WorkflowVersionSelector from '../components/ui/WorkflowVersionSelector';
import WorkflowSharingControls from '../components/ui/WorkflowSharingControls';
import apiService from '../services/api';
import { authService } from '../services/auth';
import { WorkflowVersion } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  listWorkflows: jest.fn(),
  getWorkflow: jest.fn(),
  getWorkflowVersions: jest.fn(),
  saveWorkflow: jest.fn(),
  deleteWorkflow: jest.fn()
}));

// Mock the auth service
jest.mock('../services/auth', () => ({
  getUser: jest.fn(),
  getAuthHeaders: jest.fn()
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

describe('Workflow Persistence Tests', () => {
  // Sample workflow data
  const mockWorkflows = [
    {
      id: 'workflow1',
      name: 'Test Workflow 1',
      description: 'A test workflow',
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-02T00:00:00Z',
      node_count: 5,
      status: 'active',
      user_id: 'user1',
      is_public: true,
      version: 2,
      parent_id: undefined
    },
    {
      id: 'workflow2',
      name: 'Test Workflow 2',
      description: 'Another test workflow',
      created_at: '2023-01-03T00:00:00Z',
      updated_at: '2023-01-04T00:00:00Z',
      node_count: 3,
      status: 'draft',
      user_id: 'user1',
      is_public: false,
      version: 1,
      parent_id: undefined
    }
  ];

  const mockVersions = [
    {
      id: 'workflow1_v2',
      version: 2,
      name: 'Version 2',
      is_current: true,
      created_at: '2023-01-02T00:00:00Z',
      updated_at: '2023-01-02T00:00:00Z'
    },
    {
      id: 'workflow1_v1',
      version: 1,
      name: 'Version 1',
      is_current: false,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    }
  ] as WorkflowVersion[];

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup default mock responses
    (apiService.listWorkflows as jest.MockedFunction<typeof apiService.listWorkflows>).mockResolvedValue({
      workflows: mockWorkflows,
      total: mockWorkflows.length,
      limit: 50,
      offset: 0,
      filters: {
        user_id: 'user1',
        include_public: true,
        show_versions: false
      }
    });

    (apiService.getWorkflowVersions as jest.MockedFunction<typeof apiService.getWorkflowVersions>).mockResolvedValue({
      workflow_id: 'workflow1',
      current_version: 2,
      total_versions: 2,
      versions: mockVersions
    });

    (apiService.getWorkflow as jest.MockedFunction<typeof apiService.getWorkflow>).mockResolvedValue(mockWorkflows[0]);

    (apiService.saveWorkflow as jest.MockedFunction<typeof apiService.saveWorkflow>).mockResolvedValue({
      success: true,
      workflow_id: 'workflow1',
      version: 3
    });

    (apiService.deleteWorkflow as jest.MockedFunction<typeof apiService.deleteWorkflow>).mockResolvedValue({
      success: true,
      message: 'Workflow deleted successfully',
      deleted_count: 1
    });

    // Mock auth service
    (authService.getUser as jest.MockedFunction<typeof authService.getUser>).mockReturnValue({
      user_id: 'user1',
      username: 'testuser',
      permissions: ['workflow:read', 'workflow:write']
    });

    (authService.getAuthHeaders as jest.MockedFunction<typeof authService.getAuthHeaders>).mockReturnValue({
      Authorization: 'Bearer test-token'
    });
  });

  test('Workflows page displays workflow version and sharing info', async () => {
    render(
      <BrowserRouter>
        <Workflows />
      </BrowserRouter>
    );

    // Wait for workflows to load
    await waitFor(() => {
      expect(apiService.listWorkflows).toHaveBeenCalledTimes(1);
    });

    // Check if workflows are displayed with version and sharing info
    await waitFor(() => {
      expect(screen.getByText('Test Workflow 1')).toBeInTheDocument();
      expect(screen.getByText('v2')).toBeInTheDocument();
      expect(screen.getByText('Public')).toBeInTheDocument();
      
      expect(screen.getByText('Test Workflow 2')).toBeInTheDocument();
      expect(screen.getByText('v1')).toBeInTheDocument();
      expect(screen.getByText('Private')).toBeInTheDocument();
    });
  });

  test('WorkflowVersionSelector loads and displays versions', async () => {
    const onVersionChange = jest.fn();

    render(
      <WorkflowVersionSelector 
        workflowId="workflow1" 
        currentVersion={2}
        onVersionChange={onVersionChange}
      />
    );

    // Wait for versions to load
    await waitFor(() => {
      expect(apiService.getWorkflowVersions).toHaveBeenCalledWith('workflow1');
    });

    // Check if version selector shows the current version
    expect(screen.getByText('Version 2')).toBeInTheDocument();

    // Open the dropdown
    fireEvent.click(screen.getByText('Version 2'));

    // Check if all versions are displayed
    await waitFor(() => {
      expect(screen.getByText('Version 1')).toBeInTheDocument();
    });

    // Select version 1
    fireEvent.click(screen.getByText('Version 1'));

    // Check if onVersionChange was called
    expect(onVersionChange).toHaveBeenCalled();
  });

  test('WorkflowSharingControls toggles public/private status', async () => {
    const onSharingChange = jest.fn();

    render(
      <WorkflowSharingControls 
        isPublic={true}
        onTogglePublic={onSharingChange}
      />
    );

    // Check if the toggle shows the correct initial state
    expect(screen.getByText('Public')).toBeInTheDocument();

    // Toggle to private
    fireEvent.click(screen.getByRole('checkbox'));

    // Check if onSharingChange was called with the correct value
    expect(onSharingChange).toHaveBeenCalledWith(false);
  });

  test('WorkflowPreview integrates version selector and sharing controls', async () => {
    const workflow = {
      ...mockWorkflows[0],
      data: {},
      nodes: [],
      edges: [],
      metadata: {}
    };
    const onVersionChange = jest.fn();
    const onSharingChange = jest.fn();

    render(
      <WorkflowPreview 
        workflow={workflow}
        showVersioning={true}
        showSharing={true}
        onVersionChange={onVersionChange}
        onSharingChange={onSharingChange}
        onCustomize={() => {}}
      />
    );

    // Check if both components are rendered
    await waitFor(() => {
      expect(screen.getByText('Version 2')).toBeInTheDocument();
      expect(screen.getByText('Public')).toBeInTheDocument();
    });

    // Test version change
    fireEvent.click(screen.getByText('Version 2'));
    await waitFor(() => {
      expect(screen.getByText('Version 1')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Version 1'));
    expect(onVersionChange).toHaveBeenCalledWith(1);

    // Test sharing toggle
    fireEvent.click(screen.getByRole('checkbox'));
    expect(onSharingChange).toHaveBeenCalledWith(false);
  });

  test('Workflows page filters by sharing status', async () => {
    render(
      <BrowserRouter>
        <Workflows />
      </BrowserRouter>
    );

    // Wait for workflows to load
    await waitFor(() => {
      expect(apiService.listWorkflows).toHaveBeenCalledTimes(1);
    });

    // Find and click the sharing filter dropdown
    const filterDropdown = screen.getByText('All Workflows');
    fireEvent.click(filterDropdown);

    // Select "Public Only"
    const publicOption = screen.getByText('Public Only');
    fireEvent.click(publicOption);

    // Check if API was called with the correct filter
    await waitFor(() => {
      expect(apiService.listWorkflows).toHaveBeenCalledWith(
        expect.objectContaining<Record<string, unknown>>({
          include_public: true
        })
      );
    });
  });

  test('Delete workflow with all versions', async () => {
    render(
      <BrowserRouter>
        <Workflows />
      </BrowserRouter>
    );

    // Wait for workflows to load
    await waitFor(() => {
      expect(apiService.listWorkflows).toHaveBeenCalledTimes(1);
    });

    // Mock window.confirm to return true
    window.confirm = jest.fn().mockImplementation(() => true) as jest.MockedFunction<typeof window.confirm>;

    // Find and click the more actions button for the first workflow
    const moreActionsButtons = screen.getAllByRole('button', { name: '' });
    fireEvent.click(moreActionsButtons[0]);

    // Find and click the delete button
    await waitFor(() => {
      const deleteButton = screen.getByText('Delete');
      fireEvent.click(deleteButton);
    });

    // Check if deleteWorkflow was called with the correct parameters
    await waitFor(() => {
      expect(apiService.deleteWorkflow).toHaveBeenCalledWith('workflow1', true);
    });
  });
});
