#!/usr/bin/env python3
"""
Test script for the centralized node registry
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.node_registry import node_registry

def test_node_registry():
    """Test the centralized node registry"""
    print("🧪 Testing Centralized Node Registry")
    print("=" * 50)
    
    # Test basic functionality
    print(f"📊 Total node types: {node_registry.get_node_count()}")
    print(f"✅ Active node types: {len(node_registry.get_active_node_types())}")
    
    # Test specific node types
    print("\n🔍 Testing specific node types:")
    test_types = ['aiAgent', 'instagram_post', 'email', 'webScraper']
    
    for node_type in test_types:
        metadata = node_registry.get_node_metadata(node_type)
        if metadata:
            print(f"  ✅ {node_type}: {metadata.label} ({metadata.category.value})")
        else:
            print(f"  ❌ {node_type}: Not found")
    
    # Test categories
    print("\n📂 Testing categories:")
    categories = ['AI & ML', 'Social Media', 'Communication', 'Data']
    for category in categories:
        nodes = node_registry.get_nodes_by_category(category)
        print(f"  📁 {category}: {len(nodes)} nodes - {', '.join(nodes[:3])}{'...' if len(nodes) > 3 else ''}")
    
    # Test frontend config
    print("\n🌐 Testing frontend configuration:")
    frontend_config = node_registry.get_frontend_config()
    print(f"  📱 Frontend config generated for {len(frontend_config)} nodes")
    
    # Test validation
    print("\n✅ Testing validation:")
    valid_types = ['aiAgent', 'instagram_post', 'invalid_type']
    for node_type in valid_types:
        is_valid = node_registry.is_valid_node_type(node_type)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  {status}: {node_type}")
    
    print("\n🎉 Node registry test completed!")

if __name__ == "__main__":
    test_node_registry()
