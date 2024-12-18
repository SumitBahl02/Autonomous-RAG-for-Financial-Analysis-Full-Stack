
from typing_extensions import TypedDict


def get_response(query, socketio):
    import warnings 
    warnings.filterwarnings('ignore', module="langsmith.client")
    from services.constants import get_object, set_object, socket_emitter
    set_object(socketio)
    from services.modular_agent import create_agent
    from langchain.tools import StructuredTool
    from langchain_openai import ChatOpenAI
    from services.finance.finance_group import finance_group_tool
    from services.maths.code_executor import code_tool
    from pydantic import BaseModel, Field
    from langchain_core.messages import HumanMessage
    from langchain import hub
    # from services.new_adaptive_rag import data_node_tool
    from services.Bad_queries import QueryValidator
    from services.response_transformation import ResponseTransformer
    from langchain_core.runnables.config import RunnableConfig
    from langchain.tools import StructuredTool
    from services.new_adaptive_rag import DataNode
    from langchain_core.prompts import ChatPromptTemplate
    from services.new_adaptive_rag import data_node_function
    from services.report_gen.report_gen import report_node_function, ReporGenNode
    # 
    reportgen_tool = StructuredTool.from_function(
        report_node_function,
        name="reportgen_tool",
        description="""reportgen_tool(query: str) -> str:
        NEVER use this tool unless you are asked to generate a report explicitly.
        ALWAYS REMEMBER: this tool can only be used to generate reports for the user not for information retrieval, for information retrieval refer to the data node tool.
        This tool cannot access specific data to answer a user's query, it just fetches data from certain apis to generate reports, so it should be used only when the user explicitly asks for a report.
        Only that part of query should be passed to this tool which demands for report generation. Other forms of data requested should be handled by other tools.
        An LLM agent with access to a structured tool that generates comprehensive reports on query provided 
        which contains the companies name, user query and generates report from data fetched form its internal tools. 
        Provide concise queries to this tool which contains company name AND always include the user query details, DO NOT give vague queries for search like
        - 'Generate report for the company whose CEO is Elon Musk'
        - 'Generate report for the most valued company of the world'
        Instead, provide specific queries with what exactly the user demanded for like
        - 'Report for Tesla'
        - 'Report for Tesla for financial year 2021'
        - 'Report for Tesla and analysis of their autonomous vechile division'
        ALWAYS mention company name for generating reports
        ALWAYS provide with the user query details to get the accurate results (in case user query wasn't too specific, don't add any aditional details)
        PROVIDE with what exactly the user has demanded for in the query
        Eg: Always use standard names for companies while sending queries.
        ALWAYS provide specific queries to get accurate results.
        ENSURE to keep in mind, the number of reports the user wants. Don't overcall this tool ever (if the user wants one report, 
        this tool shall be call only one. Depending upon the company names or how many reports specfically wants - this tool shall be called)
        DO NOT try to fetch multiple results in a single query, instead, make multiple queries.
        NEVER use this tool unless you are asked to generate a report explicitly.
        """,
        args_schema=ReporGenNode,
    )
    data_node_tool = StructuredTool.from_function(
        data_node_function,
        name="data_node_tool",
        description="""data_node_tool(query: str) -> str:
        An LLM agent with access to a structured tool for fetching internal data or online source.
        Internal data includes financial documents, SEC filings, and other financial data of various companies.
        Use it whenever you need to fetch internal data or online source.
        It can satisfy all your queries related to data retrieval.
        SEARCH SPECIFIC RULES:
            Provide concise queries to this tool, DO NOT give vague queries for search like
            - 'What was the gdp of the US for last 5 years?'
            - 'What is the percentage increase in Indian income in the last few years?'
            Instead, provide specific queries like
            - 'GDP of the US for 2020'
            - 'Income percentage increase in India for 2019'
            ALWAYS mention units for searching specific data wherever applicable and use uniform units for an entity accross queries.
            Eg: Always use 'USD' for currency,'percentage' for percentage, etc.
        INTERNAL DATA SPECIFIC RULES:
            The tool can fetch internal data like financial documents, SEC filings, and other financial data of various companies.
            The retriever is very sensitive to the query, so if you are unable to infer from the data in 1-2 queries, keep on trying again with rephrased queries

        ALWAYS provide specific queries to get accurate results.
        DO NOT try to fetch multiple data points in a single query, instead, make multiple queries.
        """,
        args_schema=DataNode,
    )
    llm_mini = ChatOpenAI(model='gpt-4o-mini')
    config = RunnableConfig(recursion_limit=60)

    joiner_prompt = hub.pull("wfh/llm-compiler-joiner").partial(examples='')
    finance_prompt = hub.pull('yankee/llm-compiler-finance')
    joiner_prompt_finance = hub.pull('yankee/llm-compiler-joiner').partial(examples='')
    supervisor_prompt = hub.pull('llm-compiler/planner')
    maths_prompt = hub.pull('llm-compiler/planner-maths-testing')


    llm = ChatOpenAI(model='gpt-4o')
    finance_tools = [finance_group_tool]
    maths_tools = [code_tool]



    finance_chain = create_agent(llm, finance_tools,finance_prompt,joiner_prompt_finance,'finance')
    maths_chain = create_agent(llm, maths_tools,supervisor_prompt,joiner_prompt,'maths')

    # @socket_emitter("update", emit_data_function=lambda args, kwargs, res: {"response": res})
    def maths_tool_node(query, context):
        response = maths_chain.invoke({"messages": [HumanMessage(content=f"For the following query, {query} and the following {context}, perform the actions")]})
        try:
            get_object().emit("update", {
                "username": "Math",
                "isAgent": True,
                "parentAgent": "Supervisor",
                "content": f"running {query}",
                # "thought": query,
                "isUser": False,
                "verdict": "passing to next agent",
            })
        except Exception as e:
            print("$$$$$$$$\nError while emitting")
        return response

    # @socket_emitter("update", emit_data_function=lambda args, kwargs, res: {"response": res})
    def finance_tool_node(query, context):
        response = finance_chain.invoke({"messages": [HumanMessage(content=f"For the following query, {query} and the following {context}, perform the actions")]})
        return response

    class MathsToolNode(BaseModel):
        query: str = Field(description="The mathematical query/operation to be executed")
        context: str = Field(description="The context to be considered while executing the query")

    class FinanceToolNode(BaseModel):
        query: str = Field(description="The financial query/operation to be executed")
        context: str = Field(description="The context to be considered while executing the query")

    maths_tool_agent = StructuredTool.from_function(
        maths_tool_node,
        name='maths_tool_agent',
        description='''maths_tool_agent(query: str, context[Optional]: str) -> str:
        An LLM agent with access to mathematical tools and a code executor to perform basic arithmetic operations and more.
        Use it whenever you need to perform mathematical operations or need to generate and run some custom code or need to analyze some data. The node can generate its own code, so you need to only provide the query and context.
        Context Specific Rules:
        The context is optional and can be used to provide additional information or constraints for the query.
        If the context is provided, the agent will use it to perform the actions specified in the query.
        If you do not provide a context, the agent will perform the actions based on the query alone.
        Example usage:
        maths_tool_agent("Compare the GDP of India, America and Russia over five years", "GDP of India for 2015-2020 = [21,22,24,25,30] GDP of America for 2015-2020 = [30,32,34,35,40] GDP of Russia for 2015-2020 = [15,16,18,20,22]"),
        returns: "The GDP of India has increased by 9.52 over the last five years.
                The GDP of America has increased by 10.00 over the last five years.
                The GDP of Russia has increased by 46.67 over the last five years."
        
        maths_tool_agent("Calculate the average of the following numbers: [1,2,3,4,5]","")
        returns: "The average of the numbers [1, 2, 3, 4, 5] is 3.0.",
        ''',
        args_schema=MathsToolNode,
    )
    

    tools = [maths_tool_agent,finance_group_tool,data_node_tool,reportgen_tool]


    supervisor = create_agent(llm, tools, supervisor_prompt, joiner_prompt,'supervisor')
    class StateCompression(TypedDict):
        summary: str = Field(description="A summary of the state, including all the function calls and their results, and any conclusions if drawn")

    system_compressor = """You are an expert at compressing the state of the system. 
    You have been given the task to compress the state of the system into a summary. 
    You must include all the function calls and their results, and any conclusions if drawn.
    You must provide this summary in a structured format as per the Act model. """
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_compressor),
            ("human", "{messages}"),
        ]
    )

    def restart(messages,response):
        # query = state['user_question']
        # response = input(f'Enter the response for the query-> {query}:\nAnswer: ')
        messages.append(HumanMessage(content=response))
        structured_llm_compressor = llm_mini.with_structured_output(StateCompression)
        state_compressor = route_prompt | structured_llm_compressor
        summary = state_compressor.invoke({"messages": messages})
        print('Summary:',summary)
        # state["messages"].append(HumanMessage(content=summary["summary"]))
        return summary["summary"]
    try:
        get_object().emit("update", {
            "username": "Supervisor",
            "isAgent": True,
            "parentAgent": "Query",
            "content": "Initialising supervisor...",
            # "thought": "",
            "isUser": False,
            "verdict": "passing to next agent",
        })
    except Exception as e:
        pass

    for step in supervisor.stream({'messages': [HumanMessage(content=query)],'hitl_flag':False},config=config,stream_mode='values'):
        print('============================================STEP START========================================================')
        last_state = step
        print('Last State:',last_state.__dict__)
        print('Last State:',type(last_state))
        print(step)
        print('=============================================STEP END=======================================================')

    hitl_flag = last_state["hitl_flag"]
    print(hitl_flag)
    if hitl_flag:
        messages = last_state['messages']
        user_question = last_state["user_question"]
        print('User Question:',user_question)
        response = input('Enter the response: ')
        # print('To Replay:',to_replay)
        last_message = last_state["messages"][-1]
        print('Last Message:',last_message)
        # last_message['content'] = response
        summary = restart(messages,response)
        new_state = {'messages':[HumanMessage(content=summary)]}
        # branch_config = supervisor.update_state(to_replay.config, {'messages':[HumanMessage(content=summary)],'user_response': response})
        # for step in supervisor.stream(new_state,stream_mode='values'):
        #     print("NEW BRANCH ACTIVATED")
        #     print(step)
        response = supervisor.invoke(new_state,config=config)["messages"][-1].content
    else:
        response = last_state["messages"][-1].content

    print(response)



