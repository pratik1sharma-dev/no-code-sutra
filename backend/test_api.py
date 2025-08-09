import requests
import json

def test_workflow_generation():
    url = "http://localhost:8000/generate-workflow"
    headers = {"Content-Type": "application/json"}
    data = {"user_prompt": "Generate a workflow to post AI-generated content to Instagram"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nParsed Response: {json.dumps(result, indent=2)}")
            
            # Check if the workflow uses instagram_post node
            if 'workflow' in result and 'nodes' in result['workflow']:
                nodes = result['workflow']['nodes']
                instagram_nodes = [node for node in nodes if node.get('type') == 'instagram_post']
                api_nodes = [node for node in nodes if node.get('type') == 'apiCall']
                
                print(f"\nInstagram Post nodes: {len(instagram_nodes)}")
                print(f"API Call nodes: {len(api_nodes)}")
                
                if instagram_nodes:
                    print("✅ SUCCESS: Workflow uses instagram_post node")
                else:
                    print("❌ FAILURE: Workflow does not use instagram_post node")
                    
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_workflow_generation()
