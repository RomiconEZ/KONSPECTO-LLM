import logging
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM
from langchain.tools import Tool
from typing import List
import re

# Import LLMStudioClient model
from app.services.llm.llm_studio_client import LLMStudioClient

# Import tools
from .tools.search import SearchTool  # Tool for RAG search
from .tools.video_processor import youtube_to_docx  # Tool for converting video to DOCX
from app.services.redis_service import RedisService  # For interacting with Redis

# Set up logging
logger = logging.getLogger("agent.react_agent")
logger.setLevel(logging.DEBUG)


class ReactAgent:
    def __init__(self, llm: BaseLLM = None):
        self.llm = llm or LLMStudioClient()
        self.tools = self._initialize_tools()
        self.prompt = self._create_prompt()
        self.agent = self._initialize_agent()

    def _initialize_tools(self) -> List[Tool]:
        """Initialize the tools available to the agent."""
        logger.debug("Initializing tools for the agent.")

        # Define the search tool
        search_tool = Tool(
            name="RAGSearch",
            func=None,
            coroutine=self._search_tool_func,
            description=(
                "Useful for obtaining information from the knowledge base. "
                "Use this tool when the user asks to explain or define something or requests information on a topic. "
                "This tool retrieves relevant information from the knowledge base based on the provided query."
            ),
        )

        # Define the YouTube to DOCX conversion tool
        youtube_tool = Tool(
            name="YouTubeToDocx",
            func=None,
            coroutine=self._youtube_to_docx_tool_func,
            description=(
                "Useful for generating a DOCX document with images extracted every 5 seconds from a YouTube video. "
                "Use this tool when the user requests a document with images from a YouTube video. "
                "If the document is successfully generated, the tool returns a unique key starting with 'docx', which can be used to access the document. "
                "If an error occurs during processing, it returns an error message, and a retry should not be performed."
            ),
        )

        logger.debug(f"Tools initialized: {search_tool.name}, {youtube_tool.name}")
        return [search_tool, youtube_tool]

    def _create_prompt(self) -> PromptTemplate:
        """Create the prompt template for the agent."""
        logger.debug("Creating prompt template for the agent.")

        # Assume we have a method to get model parameters
        model_parameters = self.llm.get_parameters() if hasattr(self.llm, 'get_parameters') else "Model parameters not available."

        template = """
You are an AI assistant that helps users by explaining information or generating documents with images from YouTube videos.

You have access to the following tools:

{tools}

Model Parameters:
{model_parameters}

When searching the knowledge base, extract key terms or concepts from the user's question. If you decide to use the RAGSearch tool, supply only one definition or concept at a time as the input to the tool. For each term, find relevant information in the knowledge base. If the information retrieved does not help answer the user's question, do not use it.

If the user asks you to explain something, provide a clear and understandable explanation.

Use the following format:

Question: the input question you must answer.

Thought: think about what the user is asking and decide which tool to use. Extract key terms if necessary.

Action: the action to take, should be one of [{tool_names}].

Action Input: the input to the action.

Observation: the result of the action.

... (this Thought/Action/Action Input/Observation block can repeat N times)

Thought: I now know the final answer.

Final Answer: the final answer to the original question.

If the user asked for definitions, format each definition as: "{term} - {definition}".

As a reminder, all your reasoning and actions should be in English, but the final answer should be in Russian.

If you cannot further improve the answer, you should provide the answer.

Begin!

Question: {input}
{agent_scratchpad}
"""
        tool_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": tool_descriptions,
                "tool_names": ", ".join([tool.name for tool in self.tools]),
                "model_parameters": model_parameters,
            },
        )
        logger.debug("Prompt template created.")
        return prompt

    def _initialize_agent(self):
        """Initialize the agent executor."""
        logger.debug("Initializing the agent executor.")
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            prompt=self.prompt,
            handle_parsing_errors=True,
            verbose=True,
            max_iterations=5,
        )
        logger.debug("Agent executor initialized.")
        return agent

    async def _search_tool_func(self, query: str) -> str:
        """Asynchronous function to obtain information from RAG."""
        logger.debug(f"Search tool called with query: {query}")
        try:
            results = SearchTool.search(query)
            # Format the results for each term
            if results:
                # Assuming results is a list of definitions
                formatted_results = "\n".join([f"{query} - {result}" for result in results])
                logger.debug(f"Search tool retrieved results: {formatted_results}")
                return formatted_results
            else:
                logger.debug(f"No information found on {query} in the knowledge base.")
                return f"No information found on {query} in the knowledge base."
        except Exception as e:
            logger.exception("Error in RAGSearch tool.")
            return f"Error in RAGSearch: {str(e)}"

    async def _youtube_to_docx_tool_func(self, url: str) -> str:
        """Asynchronous function to generate a DOCX document from a YouTube video."""
        logger.debug(f"YouTubeToDocx tool called with URL: {url}")
        try:
            redis_service = RedisService()
            await redis_service.connect()
            docx_key = await youtube_to_docx(url, redis_service)
            await redis_service.close()
            logger.debug(f"YouTubeToDocx tool generated docx_key: {docx_key}")
            return docx_key
        except Exception as e:
            logger.exception("Error in YouTubeToDocx tool.")
            return f"Error in YouTubeToDocx: {str(e)}"

    async def ainvoke(self, input_question: str) -> str:
        """Asynchronous agent invocation."""
        logger.debug(f"Agent ainvoke called with input: {input_question}")
        try:
            response = await self.agent.ainvoke(input_question)
            logger.debug(f"Agent ainvoke completed with response: {response}")
            # Process agent's response
            if isinstance(response, dict):
                # Assume the final answer is in the 'output' key
                final_answer = response.get('output', 'No final answer provided.')
                logger.debug(f"Extracted Final Answer from dict response: {final_answer}")
                return final_answer
            elif isinstance(response, str):
                # Attempt to extract 'Final Answer' from string
                match = re.search(r'Final Answer:\s*(.*)', response, re.IGNORECASE)
                if match:
                    final_answer = match.group(1).strip()
                    logger.debug(f"Extracted Final Answer from string response: {final_answer}")
                    return final_answer
                else:
                    logger.debug("Final Answer not found in string response. Returning full response.")
                    return response
            else:
                logger.debug(f"Unexpected response type: {type(response)}. Returning string representation.")
                return str(response)
        except Exception as e:
            logger.exception("Agent ainvoke failed.")
            raise e