# filepath: d:\site_usingcpilot\flask-welcome-app\app\routes.py
import os
from dotenv import load_dotenv

import json
import requests
from flask import current_app as app
from flask import render_template, request, jsonify
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
print("openai_api_key", openai_api_key)


@app.route('/')
def home():
    return render_template('home.html')

def get_weather(city: str) -> str:
    # Dummy function to simulate weather fetching
   # TODO!: Do an actual API Call
    print("🔨 Tool Called: get_weather", city)
    
    url = f'https://wttr.in/{city}?format=%C+%t'
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong"

avaiable_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and returns the current weather for the city"
    }
}

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()  # Get JSON data from the request
    ask_value = data.get('ask')  # Extract the 'ask' value
    # Define the system prompt
    
    system_prompt = """You are a helpful assistant.
    when user asked a question break the question into steps 
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - get_weather: Takes a city name as an input and returns the current weather for the city
    - run_command: Takes a command as input to execute on system and returns ouput
    
    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
    
    """  
   
    # Call OpenAI API
    client= OpenAI(
        api_key=openai_api_key) 
    
    messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ask_value}
            ]
    
    #print("1",messages)

    while True: 
        # Call the OpenAI API to get a response

        response = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type": "json_object"},
            messages=messages
        )
        
        #print("2",messages)
        
        # Extract the assistant's message
        parsed_assistant_message = json.loads(response.choices[0].message.content)
        print("assistant_message", parsed_assistant_message)
        messages.append({"role": "assistant", "content": json.dumps(parsed_assistant_message)})

        if parsed_assistant_message.get("step") == "plan":
            # If the step is 'plan', return the content
            messages.append({"role": "assistant", "content": parsed_assistant_message.get("content")})
            print(f'brain:  {parsed_assistant_message.get("content")}' )
            continue
        
        # Check if the step is 'action'
        if parsed_assistant_message.get("step") == "action":
            tool_name = parsed_assistant_message.get("function")
            input_value = parsed_assistant_message.get("input")
            
            # Call the appropriate function based on the function name
            if avaiable_tools.get(tool_name, False) != False:
                output = avaiable_tools[tool_name].get("fn")(input_value)
                messages.append({ "role": "assistant", "content": json.dumps({ "step": "observe", "output":  output}) })
                continue
        
        # If the step is 'output', return the final response
        if parsed_assistant_message.get("step") == "output":
            result =  json.dumps(parsed_assistant_message.get("content"))
            break

    return jsonify( {"ask" :ask_value, "response": result})
        
   

