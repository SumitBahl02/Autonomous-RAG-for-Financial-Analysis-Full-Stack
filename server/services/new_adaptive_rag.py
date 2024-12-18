from langchain.text_splitter import RecursiveCharacterTextSplitter #type: ignore
from langchain_community.document_loaders import WebBaseLoader#type: ignore
from langchain_community.vectorstores import Chroma#type: ignore
from langchain_openai import OpenAIEmbeddings#type: ignore
from langchain_core.prompts import ChatPromptTemplate#type: ignore
from langchain_openai import ChatOpenAI#type: ignore
from pydantic import BaseModel, Field#type: ignore
from typing import Literal, List
from typing_extensions import TypedDict
from langchain.schema import Document#type: ignore
from langchain import hub#type: ignore
from langchain_core.output_parsers import StrOutputParser#type: ignore
from langchain_community.tools.tavily_search import TavilySearchResults#type: ignore
from langgraph.graph import END, StateGraph, START#type: ignore
from pprint import pprint
import os
from dotenv import load_dotenv#type: ignore
from langchain.tools import StructuredTool
from llama_index.retrievers.pathway import PathwayRetriever
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import PathwayVectorClient
load_dotenv()

os.environ['OPENAI_API_KEY'] = "OPENAI_API_KEY"

client = PathwayVectorClient(
    url="http://172.30.2.194:8788",
)
# query =  """3M_2022.pdf business segment with least growth contribution"""

# client = OpenAIEmbeddings

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
# # Set embeddings
embd = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# # retriever = vectorstore.as_retriever()
retriever = PathwayRetriever(url="http://172.30.2.194:8788", similarity_top_k=10)

# print(client.similarity_search_with_score(query,metadata_filter =r"contains(path,`3M_2022`)"))


# 2021 2022 performance by business segment 3M Company"""
# print(client.similarity_search(query))
# Data model



#============================= QUESTION ROUTER =================================
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

structured_llm_router = llm.with_structured_output(RouteQuery)

# Prompt
system_router = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to SEC fillings or financial data of multiple companies.
Use the vectorstore for questions on these topics. Otherwise, use web-search."""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_router),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router

#================================================================================


#============================= GRADE DOCUMENTS =================================
# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

# LLM with function call


structured_llm_doc_grader = llm.with_structured_output(GradeDocuments)

# Prompt
system_grader = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    1)If the facts contain ANY keywords or semantic meaning related to the question, consider them relevant\n
    2)It is OK if the facts have SOME information that is unrelated to the question (1) is met \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_grader),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_doc_grader


#================================================================================


#==============================RAG CHAIN=========================================
# Prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Chain
rag_chain = prompt | llm | StrOutputParser()

#============================= GRADE HALLUCINATIONS =================================
# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

# LLM with function call
structured_llm_grader = llm.with_structured_output(GradeHallucinations)

# Prompt
system_hallucination_grader = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_hallucination_grader),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

hallucination_grader = hallucination_prompt | structured_llm_grader
#==================================================================================


#============================= GRADE ANSWER =======================================
# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

# LLM with function call


structured_llm_answer_grader = llm.with_structured_output(GradeAnswer)

# Prompt
system_answer_grader = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_answer_grader),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

answer_grader = answer_prompt | structured_llm_answer_grader
#==================================================================================

#============================= QUERY REWRITER ====================================



# Prompt
system_rewriter = """
You are a question re-writer that converts an input question to a better version that is optimized \n 
for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning.
And reformulate the query to better suite the content of the documents in the vectorstore, which are mainly SEC filings and financial documents."""
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_rewriter),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)

question_rewriter = re_write_prompt | llm | StrOutputParser()

#==================================================================================



#============================= WEB SEARCH ========================================
web_search_tool = TavilySearchResults(k=3,tavily_api_key=os.getenv("TAVILY_API_KEY"))

#==================================================================================



#============================= WORKFLOW ===========================================
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
        count: Number of times retriever is called
        queries: list of possible queries
    """

    question: str
    generation: str
    documents: List[str]
    count: int
    queries: List[str]
    company_name: str
    year: str
    table: str
    mode: str
from .constants import get_object
def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]
    queries = state["queries"]
    count = state["count"]+1
    print('======STATE BEFORE RETRIEVAL==========')
    try:
        get_object().emit("update", {
            "username": "Retriever",
            "isAgent": False,
            "parentAgent": "Research",
            "content": "Retrieving documents...",
            # "thought": "",
            "isUser": False,
            "verdict": "passing to next agent",
        })
    except Exception as e:
        pass
    print(state)
    # Retrieval
    documents = []
    table_results = []
    text_results = []
    if queries[0] != "" and count == 1:
        for query in queries:
            table_query = f"Markdown Table {query}"
            res = client.similarity_search_with_score(table_query,k = 10, metadata_filter =f"contains(path,`{state['company_name']}_{state['year']}`)")
            for doc in res:
                if doc[0].metadata["category"] == "Table":
                    table_results.append(doc)
            normal_query = query
            res = client.similarity_search_with_score(normal_query,k = 10, metadata_filter =f"contains(path,`{state['company_name']}_{state['year']}`)")
            text_results.extend(res)
    else:
        table_query = f"Markdown Table {question}"
        table_results = client.similarity_search_with_score(table_query,metadata_filter =f"contains(path,`{state['company_name']}_{state['year']}`)")
        normal_query = question
        text_results = client.similarity_search_with_score(normal_query,metadata_filter =f"contains(path,`{state['company_name']}_{state['year']}`)")    

    unique_table_results = []
    for doc in table_results:
        if doc[0].page_content not in [d[0].page_content for d in unique_table_results]:
            unique_table_results.append(doc)
    table_results = unique_table_results
    unique_text_results = []
    for doc in text_results:
        if doc[0].page_content not in [d[0].page_content for d in unique_text_results]:
            unique_text_results.append(doc)
    text_results = unique_text_results
    table_results.sort(key=lambda x: x[1], reverse=False)
    text_results.sort(key=lambda x: x[1], reverse=False)
    documents = table_results[:3] + text_results[:2]
    documents = [doc[0].page_content for doc in documents]
    return {"documents": documents, "question": question, "count":count}

def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    print('======STATE BEFORE GENERATION==========')
    try:
        get_object().emit("update", {
            "username": "Generator",
            "isAgent": False,
            "parentAgent": "Research",
            "content": "Generating answer based on the retrieved documents...",
            # "thought": "",
            "isUser": False,
            "verdict": "passing to next agent",
        })
    except Exception as e:
        pass
    print(state)
    print(state['mode'])
    if state['mode'] == "web_search":
        # RAG generation
        generation = rag_chain.invoke({"context": documents, "question": question})
    else:
        generation = '\n\n'.join(doc for doc in documents)
    return {"documents": documents, "question": question, "generation": generation}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    print('======STATE BEFORE GRADE DOCUMENTS==========')
    for d in documents:

        score = retrieval_grader.invoke(
            {"question": question, "document": d}
        )
        grade = score.binary_score
        print("grade: ", grade)
        print("document: ", d)
        print("''''''''''''''''''''''''''''''''''''''")
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}

def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    print("better_question: ", better_question)
    print("#####################################")
    return {"documents": documents, "question": better_question}

def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """
    try:
        get_object().emit("update", {
            "username": "Web Search",
            "isAgent": False,
            "parentAgent": "Research",
            "content": "Performing web search",
            # "thought": "",
            "isUser": False,
            "verdict": "passing to next agent",
        })
    except Exception as e:
        pass
    print("---WEB SEARCH---")
    question = state["question"]
    state["mode"] = "web_search"
    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)

    return {"documents": web_results, "question": question, "mode": "web_search"}


#===================================QUERY REWRITER===============================================

class RewrittenQueries(BaseModel):
    """Possible queries for a given user question."""

    query1: str = Field(
        description="Rewritten query number 1"
    )
    query2: str = Field(
        description="Rewritten query number 2"
    )
    query3: str = Field(
        description="Rewritten query number 3"
    )
    query4: str = Field(
        description="Rewritten query number 4"
    )
    query5: str = Field(
        description="Rewritten query number 5"
    )
    company_name: str = Field(
        description="Name of the company"
    )
    year: str = Field(
        description="Year of the financial document"
    )
    table: str = Field(
        description="Wether the answer might be in a table"
    )

structured_llm_rewriter = llm.with_structured_output(RewrittenQueries)


# Prompt
system_multiple_queries = """
You are an expert at rewriting a user question for querying a vectorstore or web search.
The database contains documents related to SEC fillings of multiple companies and other financial documents.
Your task is to generate multiple rephrased queries for the user question to improve search results.
While rewriting queries remember that the query text need to closely match the content of the documents in the database for vector store search.
Output exacty 5 rephrased queries for the user question along with the company name and financial year of the document as inferred from question the and nothing else.
If you think a query might belong to a certain section of the financial document, you can include that in the query.
If you think the answer might be in a table, you can include YES in the table parameter else NO.
"""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_multiple_queries),
        ("human", "{question}"),
    ]
)

query_rewriter = route_prompt | structured_llm_rewriter



def possible_queries(state):
    """
    Transform the question to produce multiple rephrased queries.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates queries key with multiple rephrased queries
    """

    print("---REPHRASED QUERIES---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    result = query_rewriter.invoke({"question": question})
    queries = [result.query1, result.query2, result.query3, result.query4, result.query5]
    company_name = result.company_name
    year = result.year
    # print("rephrased queries: ", queries)
    print(result)
    print("#####################################")
    return {"documents": documents, "queries": [question,result.query1, result.query2, result.query3, result.query4, result.query5], "question": question, "company_name": company_name, "year": year, "table": result.table, "mode": "vectorstore"}
    
#==================================================================================
def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    state["count"] = 0
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        state['mode'] = "web_search"
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        state['mode'] = "vectorstore"
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
    # return "vectorstore"

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:  #--------------------------------------------------------------------------------------
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"

# added (new)
def decide_after_transform(state):
    print("---ASSESS TRANSFORMED QUERY DOCUMENTS---")
    filtered_documents = state["documents"]

    if not filtered_documents and state["count"] >= 2 :
        # All documents have been filtered, try web search
        print("---DECISION: ALL DOCUMENTS ARE STILL NOT RELEVANT TO QUESTION, PERFORM WEB SEARCH---")
        return "web_search"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: RETRIEVE---")
        return "retrieve"





def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


# ======================================================================================================
workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("web_search", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generatae
workflow.add_node("transform_query", transform_query)  # transform_query
workflow.add_node("possible_queries", possible_queries)  # possible_queries

# Build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "web_search": "web_search",
        "vectorstore": "possible_queries",
    },
)

workflow.add_edge("possible_queries", "retrieve")

workflow.add_edge("web_search", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
# new =================================================
workflow.add_conditional_edges(
    "transform_query",
    decide_after_transform,
    {
        "web_search": "web_search",
        "retrieve": "retrieve",
    },
)

workflow.add_edge("generate",END)

# Compile
app = workflow.compile()

class DataNode(BaseModel):
    query: str = Field(description="The Query to be processed for fetching data")


def data_node_function(query: str) -> str:
    """
    An LLM agent with access to a structured tool for fetching internal data or online source.
    """
    try:
        get_object().emit("update", {
            "username": "Research",
            "isAgent": True,
            "parentAgent": "Supervisor",
            "content": "Building the research agent...",
            # "thought": "",
            "isUser": False,
            "verdict": "passing to next agent",
        })
    except Exception as e:
        pass
    inputs = {
        "question": query,
        "count": 0,  # Add this line to initialize count
        "documents": [],  # Add this line to initialize documents
        "generation": "",  # Add this line to initialize generation
        "mode" : ""  # Add this line to initialize mode
    }
    results =  app.invoke(inputs)
    return results['generation']


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


# Run
# print('___________________________________________')
# query = "Which business segment negatively impacted 3M's overall growth in 2022, excluding MD&A effects?"
# # query = "What is Adobe's year-over-year change in unadjusted operating income from FY2015 to FY2016 (in units of percents and round to one decimal place)? Give a solution to the question by using the income statement."
# # query = "What is the gdp of usa in 2020"
# result = data_node_tool.invoke({"query": query})
# print(result)
# query = """
# ### Comprehensive Description of the Table\n\nThe table provides a detailed summary of 3M's financial performance over three years (2022, 2021, and 2020). The data is presented in millions of dollars, except for shares and earnings per share, which are stated in straightforward dollar amounts.\n\nThe primary components of the table include:\n\n1. **Operating Expenses**:\n   - **Cost of Sales**: This reflects the direct costs attributable to the production of goods sold by the company.\n   - **Selling, General and Administrative Expenses**: These are the overhead costs tied to selling products and managing the business operations.\n   - **Research, Development and Related Expenses**: This figure outlines expenditures related to innovation and the development of new products.\n   - **Gain on Business Divestitures**: Any profits derived from selling parts of the business are shown here.\n   - **Goodwill Impairment Expense**: This figure indicates any reduction in the value of acquired goodwill that is no longer deemed valid.\n   - **Total Operating Expenses**: The total of all operating expenses listed above.\n\n2. **Operating Income**: This metric shows the profit made from regular business operations, calculated by subtracting total operating expenses from the total sales revenue (though total net sales figures are not explicitly mentioned in the table, it’s implied before calculating operating income).\n\n3. **Other Income (Expense), Net**: This reflects non-operating income or expenses that affect the overall profitability.\n\n4. **Income before Income Taxes**: This is derived by adjusting operating income for other income or expenses prior to accounting for taxes.\n\n5. **Provision for Income Taxes**: This depicts the estimated tax liabilities for the period.\n\n6. **Consolidated Group Income**: This shows the total income of the combined group after tax provisions.\n\n7. **Income (Loss) from Unconsolidated Subsidiaries, Net of Taxes**: This represents profits or losses from affiliates that are not included in the consolidated results.\n\n8. **Net Income**: The final figure representing profit after all expenses, taxes, and consideration of both consolidated income and unconsolidated subsidiaries.\n\n9. **Noncontrolling Interest**: This captures the portion of income that is attributed to shareholders who do not hold a controlling interest in a subsidiary company.\n\n10. **Net Income Attributable to 3M**: The profit attributable specifically to the shareholders of 3M.\n\n11. **Weighted Average Shares Outstanding**: Both basic and diluted share counts are provided, reflecting the shares available for earnings distribution to shareholders.\n\n12. **Earnings Per Share (EPS)**: This is presented for both basic and diluted forms, indicating how much profit is earned per share of common stock.\n\n### Table in Markdown Format\n\n```markdown\n| Category                                                               | 2022     | 2021     | 2020     |\n|-----------------------------------------------------------------------|----------|----------|----------|\n| Operating Expenses                                                     |          |          |          |\n| - Cost of Sales
#                                      | 34,229   | 35,355   | 32,184   |\n| - Selling, General and Administrative Expenses                        | 19,232   | 18,795   | 16,605   |\n| - Research, Development and Related Expenses                          | 9,049    | 7,197    | 6,929    |\n| - Gain on Business Divestitures                                        | (2,724)  | —        | (389)    |\n| - Goodwill Impairment Expense                                         | 271      | —        | —        |\n| - Total Operating Expenses                                             | 27,690   | 27,986   | 25,023   |\n| Operating Income                                                      | 6,539    | 7,369    | 7,161    |\n| Other Expense (Income), Net                                           | 147      | 165      | 366      |\n| Income Before Income Taxes                                            | 6,392    | 7,204    | 6,795    |\n| Provision for Income Taxes                                             | 612      | 1,285    | 1,337    |\n| Income of Consolidated Group                                          | 5,780    | 5,919    | 5,458    |\n| Income (Loss) from Unconsolidated Subsidiaries, Net of Taxes         | 11       | 10       | (5)      |\n| Net Income Including Noncontrolling Interest                           | 5,791    | 5,929    | 5,453    |\n| Less: Net Income (Loss) Attributable to Noncontrolling Interest       | 14       | 8        | 4        |\n| Net Income Attributable to 3M                                         | 5,777    | 5,921    | 5,449    |\n| Weighted Average 3M Common Shares Outstanding — Basic                | 566.0    | 579.0    | 577.6    |\n| Earnings Per Share Attributable to 3M Common Shareholders — Basic    | 10.21    | 10.23    | 9.43     |\n| Weighted Average 3M Common Shares Outstanding — Diluted              | 567.6    | 585.3    | 582.2    |\n```\n\nThe table effectively encapsulates 3M’s financial performance trends over the specified years, offering insight into operating efficiency, income sources, and shareholder returns.

# """

# print(client.similarity_search_with_score(query,metadata_filter =r"contains(path,`3M_2022`)"))