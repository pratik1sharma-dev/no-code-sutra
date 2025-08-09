import openai
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import json
from datetime import datetime
import os

class SimpleAIWorkflowNodes:
    def __init__(self):
        # Initialize OpenAI client only if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                self.client = openai.OpenAI(api_key=api_key)
                self.openai_available = True
            except Exception as e:
                print(f"Warning: OpenAI initialization failed: {e}")
                self.openai_available = False
                self.client = None
        else:
            self.openai_available = False
            self.client = None
    
    def research_company(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered company research"""
        try:
            company_name = state.get('company_name')
            if not company_name:
                raise ValueError("Company name not provided")
            
            # Step 1: Simple web search simulation
            search_results = self._simple_search(company_name)
            
            # Step 2: AI extracts structured data
            extraction_prompt = f"""
            Extract the following information about {company_name} from this search result:
            {search_results}
            
            Return a JSON object with:
            - company_name: string
            - industry: string
            - revenue_range: string (e.g., "$1M-$10M", "$10M-$100M", etc.)
            - employee_count: string
            - location: string
            - website: string
            - description: string
            - growth_signals: array of strings (e.g., "recent funding", "hiring", "expansion")
            """
            
            if self.openai_available and self.client:
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": extraction_prompt}],
                        temperature=0.1
                    )
                    
                    try:
                        company_data = json.loads(response.choices[0].message.content)
                    except json.JSONDecodeError:
                        company_data = self._get_default_company_data(company_name)
                except Exception as e:
                    print(f"OpenAI API call failed: {e}")
                    company_data = self._get_default_company_data(company_name)
            else:
                # Use simulated data when OpenAI is not available
                company_data = self._get_default_company_data(company_name)
            
            state['research_data'] = company_data
            state['research_status'] = 'completed'
            state['research_timestamp'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state['research_status'] = 'failed'
            state['research_error'] = str(e)
            return state
    
    def analyze_lead(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """AI analyzes lead quality and potential"""
        try:
            research_data = state.get('research_data', {})
            
            analysis_prompt = f"""
            Analyze this company data for lead qualification:
            {json.dumps(research_data, indent=2)}
            
            Provide a detailed analysis including:
            1. Company size and growth potential
            2. Industry relevance
            3. Budget indicators
            4. Decision-making timeline
            5. Overall lead quality assessment
            
            Return your analysis in a clear, structured format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1
            )
            
            state['lead_analysis'] = response.choices[0].message.content
            state['qualification_status'] = 'analyzed'
            
            return state
            
        except Exception as e:
            state['qualification_status'] = 'failed'
            state['qualification_error'] = str(e)
            return state
    
    def score_lead(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """AI scores the lead (0-100)"""
        try:
            research_data = state.get('research_data', {})
            lead_analysis = state.get('lead_analysis', '')
            
            scoring_prompt = f"""
            Score this lead from 0-100 based on the following criteria:
            
            Company Data: {json.dumps(research_data, indent=2)}
            Analysis: {lead_analysis}
            
            Scoring Criteria:
            - Company size and revenue (0-25 points)
            - Industry fit (0-20 points)
            - Growth signals (0-20 points)
            - Contact accessibility (0-15 points)
            - Overall potential (0-20 points)
            
            Return only the numerical score (0-100).
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": scoring_prompt}],
                temperature=0.1
            )
            
            try:
                lead_score = int(response.choices[0].message.content.strip())
                # Ensure score is between 0-100
                lead_score = max(0, min(100, lead_score))
            except ValueError:
                lead_score = 50  # Default score if parsing fails
            
            state['lead_score'] = lead_score
            state['qualification_status'] = 'scored'
            
            return state
            
        except Exception as e:
            state['qualification_status'] = 'failed'
            state['qualification_error'] = str(e)
            return state
    
    def route_lead(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """AI decides where to route the lead"""
        try:
            lead_score = state.get('lead_score', 0)
            research_data = state.get('research_data', {})
            
            routing_prompt = f"""
            Based on this lead score ({lead_score}/100) and company data:
            {json.dumps(research_data, indent=2)}
            
            Decide the best route for this lead:
            
            - HOT LEAD (80-100): Immediate sales follow-up
            - WARM LEAD (60-79): Nurture sequence
            - COLD LEAD (40-59): Long-term nurture
            - DISQUALIFIED (0-39): Archive
            
            Return only the route decision: HOT_LEAD, WARM_LEAD, COLD_LEAD, or DISQUALIFIED
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": routing_prompt}],
                temperature=0.1
            )
            
            route_decision = response.choices[0].message.content.strip().upper()
            
            # Validate route decision
            valid_routes = ['HOT_LEAD', 'WARM_LEAD', 'COLD_LEAD', 'DISQUALIFIED']
            if route_decision not in valid_routes:
                route_decision = 'COLD_LEAD'  # Default route
            
            state['route_decision'] = route_decision
            state['qualification_status'] = 'completed'
            state['qualification_timestamp'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state['qualification_status'] = 'failed'
            state['qualification_error'] = str(e)
            return state
    
    def _simple_search(self, company_name: str) -> str:
        """Simple search simulation"""
        # This is a simplified search - in production you'd use a real search API
        return f"Search results for {company_name}: This is a simulated search result for demonstration purposes. {company_name} appears to be a technology company with potential for automation solutions." 