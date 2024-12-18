from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
import traceback
from openai import OpenAI
import os

os.environ['OPENAI_API_KEY'] = "OPENAI_API_KEY"
client = OpenAI()

# Define input schema for code generation
class CodeGeneratorInput(BaseModel):
    query: str = Field(description="A natural language description of the code to generate and execute.")

# Define the code generation function
def code_tool(query: str) -> str:
    """
    Generates  and executes Python code based on a natural language query using LLM and returns the output, use it for any task that would require custom code or complex mathematical operations.
    NEVER use it for simple arithmetic operations, it would increase the cost.
    Eg: basic addition, subtraction, multiplication, division and comparisons (i.e arithmetic) should never involve any other tool. Strictly follow this rule.
    Only use this tool for complex mathematical operations or custom code generation. 
    :param query: A description of the desired functionality in natural language.
    :return: Output of the code.
    
    """
    # Uncomment and set up OpenAI API key if integrating
    # openai.api_key = "your_openai_api_key"

    try:
        response = client.chat.completions.create(
                    messages=[{
                    "role": "user",
                    "content": f'''Generate python code for this task: {query}. 
                    Try not to use third party libraries as much as possible. Never take user input (i.e. never use 'input()').
                    Be mindful that you take the inputs from the task properly, and write code in steps.  
                    Return only the final code nothing else. Store the final answer in a variable called result.''',
                    }],
                    model="gpt-4o-mini",
                    )
        # print('Raw Response:\n',response)
        code =  response.choices[0].message.content.strip()[10:-4]
        print('---------------------------------------------------------')
        print('CODE:\n')
        print(code)
        print('---------------------------------------------------------')
    except Exception as e:
        return f"Code generation failed. Error: {traceback.format_exc()}"

    try:
        # Execute the generated code to get the result
        local_namespace = {}
        global_namespace = {}
        exec(code, global_namespace, local_namespace)
        try:
            output = local_namespace['result']
        except KeyError:
            output = local_namespace
        return f"Execution successful. Output: {output}"
    except Exception as e:
        return f"Code generation successful. Generated code:\n{code}\nExecution or result extraction failed. Got this {local_namespace} Error: {traceback.format_exc()}"
    

# Create a structured tool for code generation
code_tool = StructuredTool.from_function(
    func=code_tool,
    name="code_tool",
    description='''code_tool(natural_language_query: str) -> str:
    Generates and executes Python code based on a natural language query using LLM and returns the output, use it for any task that would require custom code or to execute general maths operations using code.
    NEVER use it or call it for simple arithmetic operations, it would increase the cost.
    Eg: basic addition, subtraction, multiplication, division and comparisons (i.e arithmetic) should never involve any other tool. Strictly follow this rule.
    Only use this tool for complex mathematical operations or custom code generation else NEVER. ''',
    args_schema=CodeGeneratorInput,
    return_direct=True,
)


