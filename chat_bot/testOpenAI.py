from openai import OpenAI

# Establish connection with my account
client = OpenAI(
    organization='org-P98OVEClYAjc9o3RH5cjewt6',
    project='proj_EHoX9E4WGlFA2SmvSdMBqItV',
)

# role: system sets how they will respond
# role: user sets the question
output = client.chat.completions.create(
  model="gpt-3.5-turbo", 
  messages=[
        {"role": "system", "content": "You are a pirate captain."},
        {"role": "user"  , "content": "Say Hello World!"}
    ]
)

# Get the output text only
print(output.choices[0].message.content)