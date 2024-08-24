#!/usr/bin/env python3

import os, sys, time
import json
from termcolor import colored

project_improvements = {
    "Code Organization and Structure": [
        {"task": "Implement a consistent naming convention across all files and functions", "completed": False},
        {"task": "Create a unified error handling and logging system", "completed": False},
        {"task": "Consider using a configuration file for common settings across scripts", "completed": False}
    ],
    "AI Model Integration": [
        {"task": "Implement a fallback mechanism if the primary AI model fails", "completed": False},
        {"task": "Add support for more AI models or services", "completed": False},
        {"task": "Optimize token usage and implement better chunking strategies for long content", "completed": False}
    ],
    "Web Scraping and Data Fetching": [
        {"task": "Implement rate limiting and respect robots.txt for web scraping", "completed": False},
        {"task": "Add caching mechanisms for fetched data to reduce API calls and improve performance", "completed": False},
        {"task": "Enhance error handling for network requests and parsing", "completed": False}
    ],
    "User Experience": [
        {"task": "Create a unified CLI interface for all scripts", "completed": False},
        {"task": "Implement a simple GUI for easier interaction", "completed": False},
        {"task": "Add progress bars or spinners for long-running operations", "completed": False}
    ],
    "Data Management": [
        {"task": "Implement a database (e.g., SQLite) for storing and managing analyzed content", "completed": False},
        {"task": "Add functionality to export/import user data and settings", "completed": False}
    ],
    "Security": [
        {"task": "Implement proper API key management (avoid hardcoding or storing in plain text)", "completed": False},
        {"task": "Add input validation and sanitization across all user inputs", "completed": False}
    ],
    "Testing": [
        {"task": "Develop unit tests for core functions", "completed": False},
        {"task": "Implement integration tests for AI model interactions", "completed": False},
        {"task": "Add automated testing to your development workflow", "completed": False}
    ],
    "Documentation": [
        {"task": "Create comprehensive README files for each main component", "completed": False},
        {"task": "Generate API documentation for key functions and classes", "completed": False},
        {"task": "Provide usage examples and tutorials", "completed": False}
    ],
    "Performance Optimization": [
        {"task": "Profile the code to identify and optimize bottlenecks", "completed": False},
        {"task": "Implement multithreading or asyncio for concurrent operations", "completed": False}
    ],
    "Feature Enhancements": [
        {"task": "Implement cross-referencing between different content types (e.g., related TED talks and YouTube videos)", "completed": False},
        {"task": "Add sentiment analysis for comments and feedback", "completed": False},
        {"task": "Implement a recommendation system based on user interaction history", "completed": False}
    ],
    "Dependency Management": [
        {"task": "Use a tool like Poetry or Pipenv for better dependency management", "completed": False},
        {"task": "Regularly update and audit dependencies for security vulnerabilities", "completed": False}
    ],
    "Continuous Integration/Continuous Deployment (CI/CD)": [
        {"task": "Set up a CI/CD pipeline for automated testing and deployment", "completed": False}
    ],
    "Accessibility": [
        {"task": "Ensure all output is screen-reader friendly", "completed": False},
        {"task": "Implement keyboard shortcuts for common actions", "completed": False}
    ],
    "Internationalization": [
        {"task": "Add support for multiple languages in the UI and content analysis", "completed": False}
    ],
    "Data Visualization": [
        {"task": "Implement charts or graphs to visualize analysis results", "completed": False}
    ],
    "Project Tasks": [
        {"task": "youtube.py", "completed": True},
        {"task": "tedtalk.py", "completed": True},
        {"task": "tedtalk2", "completed": True},
        {"task": "nexus.py", "completed": True},
        {"task": "Fix web browsing", "completed": True},
        {"task": "Make up-to-date web browsing", "completed": True},
        {"task": "nexus2(make it make a title for the respective file, make it work using both functionalities, analysis)", "completed": True},
        {"task": "Nexus3(data visualization, creating and running data GUIs)", "completed": False},
        {"task": "Improve prompt-engineering for nexus, particularly on its searching being impressive, fast and effectively, making sure nothing's getting missed out", "completed": True},
        {"task": "sight.py", "completed": True},
        {"task": "news.py (news-api)", "completed": False},
        {"task": "mit.py", "completed": False}
    ]
}

class InteractiveChecklist:
    def __init__(self):
        self.improvements = project_improvements
        self.filename = 'project_checklist.json'
        self.load_checklist()

    def load_checklist(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                saved_data = json.load(f)
                for category, items in self.improvements.items():
                    if category in saved_data:
                        for i, item in enumerate(items):
                            if i < len(saved_data[category]):
                                items[i] = saved_data[category][i]

    def save_checklist(self):
        with open(self.filename, 'w') as f:
            json.dump(self.improvements, f, indent=2)

    def print_checklist(self):
        for category, items in self.improvements.items():
            print(f"\n{colored(category, 'cyan', attrs=['bold'])}")
            for i, item in enumerate(items, 1):
                checkbox = colored('✓', 'green', attrs=['bold']) if item['completed'] else colored('☐', 'red')
                task = colored(item['task'], 'green') if item['completed'] else item['task']
                print(f"{checkbox} {i}. {task}")

    def toggle_task(self, task_number):
        for category, items in self.improvements.items():
            if 1 <= task_number <= len(items):
                item = items[task_number - 1]
                item['completed'] = not item['completed']
                self.save_checklist()
                return True
        return False

    def add_task(self, category, task):
        if category not in self.improvements:
            self.improvements[category] = []
        self.improvements[category].append({"task": task, "completed": False})
        self.save_checklist()

    def remove_task(self, task_number):
        for category, items in self.improvements.items():
            if 1 <= task_number <= len(items):
                del items[task_number - 1]
                self.save_checklist()
                return True
        return False

def main():
    checklist = InteractiveChecklist()

    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
            checklist.print_checklist()
            print(colored("\nOptions:", 'yellow', attrs=['bold']))
            print("1. Toggle task completion")
            print("2. Add new task")
            print("3. Remove task")
            print("4. Exit")

            choice = input(colored("\nEnter your choice (1-4): ", 'yellow'))

            if choice == '1':
                task_number = int(input("Enter task number: "))
                if checklist.toggle_task(task_number):
                    print(colored("Task toggled successfully!", 'green'))
                else:
                    print(colored("Invalid task number.", 'red'))

            elif choice == '2':
                category = input("Enter category (existing or new): ")
                task = input("Enter new task: ")
                checklist.add_task(category, task)
                print(colored("Task added successfully!", 'green'))

            elif choice == '3':
                task_number = int(input("Enter task number to remove: "))
                if checklist.remove_task(task_number):
                    print(colored("Task removed successfully!", 'green'))
                else:
                    print(colored("Invalid task number.", 'red'))

            elif choice == '4':
                print(colored("Exiting. Your checklist has been saved.", 'yellow'))
                break

            else:
                print(colored("Invalid choice. Please try again.", 'red'))

            input("\nPress Enter to continue...")
        except KeyboardInterrupt: # Handle Ctrl+C to exit the program
            os.system('clear')
            print("\nExiting...")
            time.sleep(.75)
            os.system('clear')
            sys.exit()
            
    
    # handle ctrl+c
    

if __name__ == "__main__":
    main()