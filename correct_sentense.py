import requests

def correct_text_with_languagetool(text):
    # LanguageTool API endpoint
    url = 'https://languagetool.org/api/v2/check'

    # Parameters for the API request
    params = {
        'text': text,
        'language': 'en-US',  # Language code for English (United States)
        'enabledOnly': 'false',  # Allow all rules to be checked
    }

    try:
        # Send POST request to LanguageTool API
        response = requests.post(url, data=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            data = response.json()
            # Extract corrections from the response
            corrections = [(error['offset'], error['length'], error['replacements'][0]['value']) for error in data['matches']]
            
            # Apply corrections to the text
            corrected_text = text
            offset_correction = 0
            for offset, length, replacement in corrections:
                corrected_text = corrected_text[:offset + offset_correction] + replacement + corrected_text[offset + length + offset_correction:]
                offset_correction += len(replacement) - length
            print(corrected_text)
            return corrected_text
        
        else:
            print(f"Error: HTTP status code {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

