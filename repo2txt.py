import os
import requests
import json
from py_mini_racer import MiniRacer

class Repo2Txt:
    def __init__(self):
        # Load the JavaScript code
        with open('script.js', 'r') as f:
            js_code = f.read()
        
        # Create a JavaScript context
        self.context = MiniRacer()
        
        # Create mock browser environment
        mock_browser_env = """
        var document = {
            getElementById: function(id) {
                return {
                    addEventListener: function(event, callback) {},
                    value: '',
                    style: { display: '' },
                    select: function() {},
                    appendChild: function(child) {},
                    querySelector: function(selector) { return null; },
                    querySelectorAll: function(selector) { return []; }
                };
            },
            createElement: function(tag) {
                return {
                    setAttribute: function(attr, value) {},
                    appendChild: function(child) {},
                    click: function() {}
                };
            },
            createTextNode: function(text) { return {}; },
            querySelector: function(selector) { return this.getElementById(selector); },
            addEventListener: function(event, callback) {
                if (event === 'DOMContentLoaded') {
                    callback();
                }
            }
        };
        var window = {
            URL: {
                createObjectURL: function(blob) { return ''; },
                revokeObjectURL: function(url) {}
            }
        };
        var navigator = {
            clipboard: {
                writeText: function(text) { return Promise.resolve(); }
            }
        };
        var console = {
            log: function(msg) { py_console_log(msg); },
            error: function(msg) { py_console_error(msg); }
        };
        function fetch(url, options) {
            return Promise.resolve(py_fetch(url, options));
        }
        var lucide = {
            createIcons: function() {}
        };
        """
        
        # Add Python functions to the JavaScript context
        self.context.eval(mock_browser_env)
        self.context.eval("""
        function py_fetch(url, options) {
            return JSON.parse(py_fetch_impl(url, JSON.stringify(options)));
        }
        """)
        
        # Execute the JavaScript code
        self.context.eval(js_code)

    def repo2txt(self, repo_url, access_token=None, filters=None):
        # Set up the mock form values
        self.context.eval(f"""
        document.getElementById('repoUrl').value = '{repo_url}';
        document.getElementById('accessToken').value = '{access_token or ""}';
        """)

        # Trigger the form submission
        self.context.eval("""
        var event = { preventDefault: function() {} };
        document.getElementById('repoForm').dispatchEvent(new Event('submit'));
        """)

        # Wait for the asynchronous operations to complete
        self.context.eval("""
        function waitForCompletion() {
            return new Promise((resolve) => {
                var checkInterval = setInterval(function() {
                    if (document.getElementById('generateTextButton').style.display === 'flex') {
                        clearInterval(checkInterval);
                        resolve();
                    }
                }, 100);
            });
        }
        """)
        self.context.eval("await waitForCompletion();")

        # Trigger the text generation
        self.context.eval("document.getElementById('generateTextButton').click();")

        # Get the generated text
        formatted_text = self.context.eval("document.getElementById('outputText').value")

        return formatted_text

    def py_fetch_impl(self, url, options_json):
        options = json.loads(options_json)
        headers = options.get('headers', {})
        
        response = requests.get(url, headers=headers)
        return json.dumps({
            'ok': response.ok,
            'status': response.status_code,
            'json': response.json() if response.ok else None,
            'text': response.text if response.ok else None
        })

    def py_console_log(self, message):
        print("JS Console Log:", message)

    def py_console_error(self, message):
        print("JS Console Error:", message)

# Create a global instance
repo2txt_instance = Repo2Txt()

def repo2txt(repo_url, access_token=None, filters=None):
    return repo2txt_instance.repo2txt(repo_url, access_token, filters)

# Testing
if __name__ == "__main__":
    repo_url = "https://github.com/abinthomasonline/repo2txt/"
    github_token = os.getenv("GITHUB_ACCESS_TOKEN")

    filters = [".js", ".py", "!*test*"]  # Example filters

    combined_text = repo2txt(repo_url, github_token, filters)
    
    print(combined_text)

