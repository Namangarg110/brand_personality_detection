import pandas as pd
from PIL import Image
import ast
import os  # To handle file paths
import requests
import json
import base64
import os

def get_image_base64_encoding(image_path: str) -> str:
    """
    Function to return the base64 string representation of an image
    """
    with open(image_path, 'rb') as file:
        image_data = file.read()
    image_extension = os.path.splitext(image_path)[1]
    base64_encoded = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/{image_extension[1:]};base64,{base64_encoded}"
    
# API configurations
asticaAPI_key = 'D4959ECA-44FA-4D4C-BBC1-769414741D23B5AB16C4-41E9-486E-800E-AA34B6EEF6B7'  # visit https://astica.ai
asticaAPI_timeout = 25 # in seconds. "gpt" or "gpt_detailed" require increased timeouts
asticaAPI_endpoint = 'https://vision.astica.ai/describe'
asticaAPI_modelVersion = '2.1_full' # '1.0_full', '2.0_full', or '2.1_full'

# vision parameters:  https://astica.ai/vision/documentation/#parameters
asticaAPI_visionParams = 'describe,ocr'  # comma separated, defaults to "all". 
asticaAPI_gpt_prompt = '' # only used if visionParams includes "gpt" or "gpt_detailed"
asticaAPI_prompt_length = '90' # number of words in GPT response

'''    
    '1.0_full' supported visionParams:
        describe
        objects
        categories
        moderate
        tags
        brands
        color
        faces
        celebrities
        landmarks
        gpt               (Slow)
        gpt_detailed      (Slower)

    '2.0_full' supported visionParams:
        describe
        describe_all
        objects
        tags
        describe_all 
        text_read 
        gpt             (Slow)
        gpt_detailed    (Slower)
        
    '2.1_full' supported visionParams:
        Supports all options 
        
'''

# Define payload dictionary
asticaAPI_payload = {
    'tkn': asticaAPI_key,
    'modelVersion': asticaAPI_modelVersion,
    'visionParams': asticaAPI_visionParams,
    'input': "asticaAPI_input",
}



def asticaAPI(endpoint, payload, timeout):
    response = requests.post(endpoint, data=json.dumps(payload), timeout=timeout, headers={ 'Content-Type': 'application/json', })
    if response.status_code == 200:
        return response.json()
    else:
        return {'status': 'error', 'error': 'Failed to connect to the API.'}
    
def get_descriptions(csv_file,basedir):
    # Load the CSV file
    # csv_file = 'Data/apple.csv'
    df = pd.read_csv(csv_file)

    # Set the base directory
    # basedir = 'Data/apple/'
    if 'description' not in df.columns:
        df['description'] = ''

    # Find the last processed row
    last_processed = df['description'].last_valid_index()
    start_row = 0 

    # Loop through the rows in the DataFrame starting from the last unprocessed row
    for index, row in enumerate(df.itertuples(), start=start_row):
        print(index)
        # Skip already processed rows
        #  pd.notna(row.description) or
        if row.description != '':
            # print(row.description)
            # print(index)
            continue

        try:
            image_paths = ast.literal_eval(row._1)  # Adjust the index based on your DataFrame
            if not isinstance(image_paths, list):
                raise ValueError("The column value is not a list")
        except ValueError as e:
            print(f"Error in row {index}: {e}")
            df.at[index, 'description'] = 'Error: ' + str(e)
            df.to_csv(csv_file, index=False)
            continue

        descriptions = []
        for image_path in image_paths:
            full_path = os.path.join(basedir, image_path.split('/')[-1])
            try:
                asticaAPI_input = get_image_base64_encoding(full_path)
                asticaAPI_payload['input'] = asticaAPI_input
                api_result = asticaAPI(asticaAPI_endpoint, asticaAPI_payload, asticaAPI_timeout)

                # Extract description from API result
                if 'caption' in api_result and api_result['caption']['text'] != '':
                    descriptions.append(api_result['caption']['text'])
            except Exception as e:
                descriptions.append("")
                print(f"Error processing image at {full_path}: {e}")

        # Combine descriptions and update the DataFrame
        df.at[index, 'description'] = ' | '.join(descriptions)

        # Save progress
        df.to_csv(csv_file, index=False)


get_descriptions("Data/samsung.csv","Data/samsung")