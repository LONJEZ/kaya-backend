"""Interactive chat demo"""

import requests
import json
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def chat(query: str, token: str):
    """Send chat query"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {"query": query, "user_id": "demo-user-001"}
    
    response = requests.post(f"{BASE_URL}/api/chat/query", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"answer_text": f"Error: {response.text}", "confidence": 0}


def main():
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}🤖 Kaya AI Chat - Interactive Demo")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    token = get_demo_token()
    
    print(f"{Fore.GREEN}Welcome! Ask me questions about your business.")
    print(f"{Fore.YELLOW}Examples:")
    print("  - What are my top products?")
    print("  - How much revenue did I make last month?")
    print("  - Show me sales by category")
    print("  - Which payment method is most popular?\n")
    print(f"{Fore.MAGENTA}Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input(f"{Fore.BLUE}You: {Style.RESET_ALL}")
            
            if query.lower() in ['exit', 'quit', 'bye']:
                print(f"\n{Fore.GREEN}Goodbye! 👋")
                break
            
            if not query.strip():
                continue
            
            print(f"{Fore.YELLOW}Kaya AI: Thinking...")
            
            response = chat(query, token)
            
            print(f"\r{Fore.GREEN}Kaya AI: {response['answer_text']}")
            
            if response.get('visualization'):
                viz = response['visualization']
                print(f"{Fore.CYAN}📊 Visualization: {viz.get('type', 'N/A')}")
            
            print()
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Goodbye! 👋")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}\n")


if __name__ == "__main__":
    main()
