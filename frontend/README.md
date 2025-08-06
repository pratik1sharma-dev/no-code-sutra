# No Code Sutra - Frontend Foundation

## 🎯 Project Overview

**No Code Sutra** is a visual drag-and-drop platform that enables non-technical users to create, deploy, and monitor AI-powered workflows. This repository contains the frontend application built with React, TypeScript, and Tailwind CSS.

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🏗️ Architecture

### Tech Stack
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Flow** - Visual workflow builder
- **React Router** - Navigation
- **Zustand** - State management
- **Lucide React** - Icons

### Project Structure
```
src/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── layout/       # Layout components (Header, Sidebar)
│   ├── nodes/        # Workflow node components
│   └── canvas/       # React Flow canvas components
├── pages/            # Page components
├── hooks/            # Custom React hooks
├── stores/           # Zustand state stores
├── services/         # API service layer
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
```

## 🎨 Design System

### Colors
- **Primary**: Blue shades for main actions and branding
- **Secondary**: Gray shades for text and backgrounds
- **Success**: Green shades for positive states
- **Warning**: Yellow shades for caution states
- **Danger**: Red shades for error states

### Typography
- **Headings**: Cormorant Garamond (serif)
- **Body**: Inter (sans-serif)

### Components
- **Buttons**: Primary, secondary, and danger variants
- **Cards**: Consistent card layouts
- **Inputs**: Form inputs with validation states
- **Loading**: Spinner components

## 📱 Features Implemented

### ✅ Foundation (Phase 1)
- [x] Project setup with Vite + React + TypeScript
- [x] Tailwind CSS configuration with custom design system
- [x] Basic routing with React Router
- [x] Layout components (Header, Sidebar)
- [x] Dashboard page with stats and recent workflows
- [x] Login page with form validation
- [x] Basic React Flow canvas integration
- [x] Responsive design

### 🔄 In Progress
- [ ] Node library implementation
- [ ] Workflow builder functionality
- [ ] State management with Zustand
- [ ] API integration

### 📋 Planned
- [ ] AI Agent nodes
- [ ] Email and Slack integration nodes
- [ ] Content creation nodes
- [ ] Scheduling system
- [ ] Analytics and monitoring
- [ ] User authentication
- [ ] Backend integration

## 🎯 Key Components

### Layout
- **Sidebar**: Navigation with workflow categories
- **Header**: Search, notifications, and user menu
- **Main Content**: Dynamic content area

### Pages
- **Dashboard**: Overview with stats and recent workflows
- **Workflow Builder**: Visual canvas for creating workflows
- **Login**: Authentication page

### UI Components
- **LoadingSpinner**: Reusable loading component
- **Cards**: Consistent card layouts
- **Buttons**: Styled button variants
- **Forms**: Input components with validation

## 🔧 Development

### Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Code Style
- TypeScript strict mode enabled
- ESLint with Airbnb configuration
- Prettier for code formatting
- Tailwind CSS for styling

## 🚀 Next Steps

1. **Node Library**: Implement workflow node components
2. **State Management**: Set up Zustand stores
3. **API Integration**: Connect to backend services
4. **Authentication**: Implement user auth flow
5. **Workflow Execution**: Add execution monitoring

## 📄 License

This project is part of the No Code Sutra platform.

---

**No Code Sutra** - Visual AI Workflows for Everyone
