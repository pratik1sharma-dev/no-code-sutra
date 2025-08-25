# 🏗️ Design Guidelines & Architecture Standards

## 📋 **Design Philosophy**

**"Consistency over Innovation"** - We prioritize maintaining a stable, predictable architecture over introducing new design patterns unless there's a compelling technical reason.

## 🎯 **Core Design Principles**

### 1. **State-Based Data Flow** (IMMUTABLE)
```
AI Workflow Generator → Workflow JSON → Node Config → Workflow Executor → State → Node
     ↓                           ↓              ↓              ↓         ↓      ↓
Generates prompt    → {"config": {"prompt": → config.get() → state['prompt'] → Node reads
                    "Create..."}}           copies to state              from state
```

**This pattern is FIXED and should NOT be changed without thorough discussion.**

### 2. **Separation of Concerns**
- **AI Workflow Generator**: Generates workflow structure and node configurations
- **Workflow Executor**: Orchestrates execution and manages state
- **Nodes**: Execute business logic and read from state
- **State**: Single source of truth for runtime data

### 3. **Consistency Across All Nodes**
All nodes MUST follow the same pattern:
```python
def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    # Read from state (NEVER from node_config directly)
    param1 = state.get('param1', '')
    param2 = state.get('param2', 'default')
    
    # Execute business logic
    result = process_data(param1, param2)
    
    # Update state with results
    state['result'] = result
    state['status'] = 'completed'
    return state
```

## 🚫 **Forbidden Design Changes**

### ❌ **NEVER Change These Patterns**

1. **Node Reading from Config Directly**
   ```python
   # ❌ FORBIDDEN - Don't do this
   def execute(state: Dict[str, Any]) -> Dict[str, Any]:
       node_config = state.get('node_config', {})
       prompt = node_config.get('prompt', '')  # WRONG!
   ```

2. **Workflow Executor Passing Config Directly**
   ```python
   # ❌ FORBIDDEN - Don't do this
   if node_type == 'aiAgent':
       state['node_config'] = config  # WRONG!
   ```

3. **Hybrid Approaches**
   ```python
   # ❌ FORBIDDEN - Don't do this
   prompt = state.get('prompt', '') or node_config.get('prompt', '')  # WRONG!
   ```

### ✅ **Correct Pattern (MANDATORY)**

1. **Workflow Executor Copies Config to State**
   ```python
   # ✅ CORRECT - Always do this
   if node_type == 'aiAgent':
       state['prompt'] = config.get('prompt', '')
       state['task'] = config.get('task', 'generate')
       state['topic'] = config.get('topic', 'content generation')
   ```

2. **Nodes Read from State**
   ```python
   # ✅ CORRECT - Always do this
   def execute(state: Dict[str, Any]) -> Dict[str, Any]:
       prompt = state.get('prompt', '')
       task = state.get('task', 'generate')
       topic = state.get('topic', 'content generation')
   ```

## 🔄 **Data Flow Standards**

### **Workflow Generation Phase**
```
User Request → AI Workflow Generator → Workflow JSON
     ↓                    ↓                    ↓
"Create Instagram" → Generates contextual → {"config": {"prompt":
   post about AI"      prompt for AI Agent    "Create Instagram..."}}
```

### **Workflow Execution Phase**
```
Workflow JSON → Workflow Executor → State → Node Execution
     ↓              ↓              ↓           ↓
{"config": {"prompt": → copies to → state['prompt'] → Node reads
 "Create..."}}        state         = "Create..."    from state
```

### **State Management Rules**
1. **State is the single source of truth** during execution
2. **Config values are copied to state** at the beginning of node execution
3. **Nodes only read from state**, never from config
4. **State is passed between nodes** for data flow
5. **State accumulates results** from each node

## 📝 **Node Development Standards**

### **Required Node Structure**
```python
def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # 1. Read parameters from state
        param1 = state.get('param1', '')
        param2 = state.get('param2', 'default')
        
        # 2. Execute business logic
        result = process_business_logic(param1, param2)
        
        # 3. Update state with results
        state['result'] = result
        state['output'] = result
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        
        return state
        
    except Exception as e:
        # 4. Error handling
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state
```

### **Parameter Reading Standards**
```python
# ✅ CORRECT - Read from state with defaults
prompt = state.get('prompt', '')
style = state.get('style', 'modern')
image_url = state.get('image_url', '')

# ❌ FORBIDDEN - Don't read from config directly
node_config = state.get('node_config', {})
prompt = node_config.get('prompt', '')  # WRONG!
```

## 🔧 **Workflow Executor Standards**

### **Node Configuration Pattern**
```python
def execute_node(self, node_type: str, node_config: Dict[str, Any], input_data: Dict[str, Any], edges: Optional[List[Dict[str, Any]]] = None, current_node_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        # 1. Initialize state with input data
        state = input_data.copy()
        
        # 2. Get node configuration
        config = node_config.get('config', {})
        
        # 3. Copy config values to state (MANDATORY)
        if node_type == 'aiAgent':
            state['prompt'] = config.get('prompt', '')
            state['task'] = config.get('task', 'generate')
            state['topic'] = config.get('topic', 'content generation')
        elif node_type == 'imageGenerator':
            state['prompt'] = config.get('prompt', state.get('prompt', ''))
            state['style'] = config.get('style', state.get('style', 'modern'))
        # ... other node types
        
        # 4. Execute node
        executor = self.dispatcher.get_executor(node_type)
        result = executor(state)
        
        # 5. Add metadata
        result['node_id'] = current_node_id
        result['node_type'] = node_type
        result['timestamp'] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'node_type': node_type,
            'timestamp': datetime.now().isoformat()
        }
```

## 🚨 **Change Control Process**

### **Before Making ANY Design Changes**

1. **Document the Problem**
   - What specific issue are you trying to solve?
   - What are the current limitations?
   - What are the expected benefits?

2. **Propose the Solution**
   - Detailed technical proposal
   - Impact analysis on existing code
   - Migration plan for existing nodes

3. **Get Approval**
   - Discuss with the team
   - Get explicit approval before implementation
   - Document the decision

4. **Implementation**
   - Follow the approved design
   - Update all affected nodes consistently
   - Maintain backward compatibility

5. **Testing**
   - Comprehensive testing of all nodes
   - Verify data flow integrity
   - Performance impact assessment

### **Emergency Changes**
- Only for critical bugs or security issues
- Must be reverted within 24 hours if not approved
- Requires immediate team notification

## 📊 **Compliance Checklist**

### **For New Nodes**
- [ ] Reads parameters from `state` only
- [ ] Follows standard `execute(state)` signature
- [ ] Returns updated state with results
- [ ] Includes proper error handling
- [ ] Uses consistent parameter naming

### **For Workflow Executor Changes**
- [ ] Copies config values to state
- [ ] Maintains existing node compatibility
- [ ] Follows established patterns
- [ ] Includes proper error handling
- [ ] Updates documentation

### **For Architecture Changes**
- [ ] Documented problem and solution
- [ ] Team approval obtained
- [ ] Impact analysis completed
- [ ] Migration plan created
- [ ] Testing plan defined

## 🎯 **Success Metrics**

### **Stability Metrics**
- **Zero breaking changes** to existing workflows
- **Consistent data flow** across all nodes
- **Predictable behavior** for developers
- **Maintainable codebase** with clear patterns

### **Quality Metrics**
- **100% test coverage** for data flow
- **Consistent error handling** across nodes
- **Clear documentation** for all patterns
- **Developer satisfaction** with architecture

## 📚 **References**

### **Current Implementation**
- **AI Agent**: `src/services/nodes/ai_agent.py`
- **Workflow Executor**: `src/services/langgraph_workflows/workflow_executor.py`
- **Instagram Nodes**: `src/services/nodes/social_media.py`, `src/services/nodes/text_overlay.py`

### **Documentation**
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Instagram Review**: `INSTAGRAM_IMPLEMENTATION_REVIEW.md`
- **Setup Guides**: `INSTAGRAM_SETUP.md`, `BEDROCK_SETUP_GUIDE.md`

## 🚀 **Conclusion**

**This design pattern is the foundation of our system. Respect it, maintain it, and only change it with thorough discussion and approval.**

The state-based approach provides:
- ✅ **Predictability**: Developers know exactly how data flows
- ✅ **Consistency**: All nodes follow the same pattern
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Reliability**: Proven to work in production

**Remember: Consistency over Innovation!** 🎯
