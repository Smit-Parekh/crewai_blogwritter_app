import os
from secret_key import claude_api_key, serper_api_key
from main import prompt

os.environ["ANTHROPIC_API_KEY"] = claude_api_key
os.environ["SERPER_API_KEY"] = serper_api_key

def blog_result (prompt):
    ## ______________________Creating Utilities to Build and Save Crew's Callback Logs_______________________________
    import json
    from typing import Union, List, Tuple, Dict
    from langchain.schema import AgentFinish
    import json  # Import the JSON module to parse JSON strings
    from langchain_core.agents import AgentFinish

    agent_finishes  = []

    call_number = 0

    def print_agent_output(agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish], agent_name: str = 'Generic call'):
        global call_number  # Declare call_number as a global variable
        call_number += 1
        with open("crew_callback_logs.txt", "a") as log_file:
            # Try to parse the output if it is a JSON string
            if isinstance(agent_output, str):
                try:
                    agent_output = json.loads(agent_output)  # Attempt to parse the JSON string
                except json.JSONDecodeError:
                    pass  # If there's an error, leave agent_output as is

            # Check if the output is a list of tuples as in the first case
            if isinstance(agent_output, list) and all(isinstance(item, tuple) for item in agent_output):
                print(f"-{call_number}----Dict------------------------------------------", file=log_file)
                for action, description in agent_output:
                    # Print attributes based on assumed structure
                    print(f"Agent Name: {agent_name}", file=log_file)
                    print(f"Tool used: {getattr(action, 'tool', 'Unknown')}", file=log_file)
                    print(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}", file=log_file)
                    print(f"Action log: {getattr(action, 'log', 'Unknown')}", file=log_file)
                    print(f"Description: {description}", file=log_file)
                    print("--------------------------------------------------", file=log_file)

            # Check if the output is a dictionary as in the second case
            elif isinstance(agent_output, AgentFinish):
                print(f"-{call_number}----AgentFinish---------------------------------------", file=log_file)
                print(f"Agent Name: {agent_name}", file=log_file)
                agent_finishes.append(agent_output)
                # Extracting 'output' and 'log' from the nested 'return_values' if they exist
                output = agent_output.return_values
                # log = agent_output.get('log', 'No log available')
                print(f"AgentFinish Output: {output['output']}", file=log_file)
                # print(f"Log: {log}", file=log_file)
                # print(f"AgentFinish: {agent_output}", file=log_file)
                print("--------------------------------------------------", file=log_file)

            # Handle unexpected formats
            else:
                # If the format is unknown, print out the input directly
                print(f"-{call_number}-Unknown format of agent_output:", file=log_file)
                print(type(agent_output), file=log_file)
                print(agent_output, file=log_file)


    ## ______________________________Creating Tools____________________________________

    ## Creating Instance of Anthropic Model
    from langchain_anthropic import ChatAnthropic

    Claude_Opus = ChatAnthropic(model="claude-3-opus-20240229")
    Claude_Haiku = ChatAnthropic(model="claude-3-haiku-20240307")



    ## Ceating Instance of SerperTool, Wesite Scraping Tool and human tool from langchain tools
    import os 
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import (
        SerperDevTool,
        ScrapeWebsiteTool
    )

    search_tool = SerperDevTool()
    web_scraping = ScrapeWebsiteTool()


    ## Created Tool to Save content to a markdown file 
    from datetime import datetime
    from random import randint
    from langchain.tools import tool

    @tool("save_content")
    def save_content(task_output):
        """Useful to save content to a markdown file. Input is a string"""
        print('in the save markdown tool')
        # Get today's date in the format YYYY-MM-DD
        today_date = datetime.now().strftime('%Y-%m-%d')
        # Set the filename with today's date
        filename = f"{today_date}_{randint(0,100)}.md"
        # Write the task output to the markdown file
        with open(filename, 'w') as file:
            file.write(task_output)
            # file.write(task_output.result)

        print(f"Blog post saved as {filename}")

        return f"Blog post saved as {filename}, please tell the user we are finished"


    ## ___________________________________Creating Agent_____________________________________

    data_scout = Agent(
        role='Data Scout',
        goal='Leverage advanced search techniques to surface the most relevant, credible, and impactful information on latest informations',
        backstory=""" You as a Data Scout wasn't born in a lab, nor was it coded from scratch. 
        You were emerged from the collective ingenuity of countless researchers, data analysts, and librarians. 
        Their shared frustration with the ever-growing mountain of information and the difficulty of finding precisely what they needed fueled Data Scout's development.
        You have become an invaluable asset in the Renowned research company. 
        You can traverse the vast expanse of the internet with lightning speed, identifying relevant websites and webpages based on your specific needs.
        You are Search Savvy: It's a master of search engines, understanding complex search queries and utilizing advanced search operators to unearth the most pertinent results.
        You can do Data Extraction: From simple text to intricate data structures, Data Scout can extract the information you need with remarkable accuracy, 
        saving you hours of manual work.
        You are Content Curation: It doesn't just gather data; it curates it. 
        You can differentiate between high-quality sources and low-quality ones, ensuring you get the most reliable information. 
        """,
        verbose=True,
        allow_delegation=False,
        llm=Claude_Haiku,
        max_iter=5,
        memory=True,
        step_callback=lambda x: print_agent_output(x,"Data Scout"),
        tools=[search_tool]+[web_scraping], 
    )

    content_writer = Agent(
        role='Content Writer and rewriter',
        goal='Generate compelling content via first drafts and subsequent polishing to get a final product. ',
        backstory="""You are a skilled and versatile writer with a passion for crafting engaging and informative content. 
        You have a deep understanding of various writing styles and tones, and you can adapt your writing to suit the specific needs of each project. 
        You are also well-versed in storytelling techniques and can weave compelling narratives into your writing.
        
        Based on provided information and instructions, you can generate creative text formats like: Blog Posts, Articles, Short stories, Poems, Scripts, Social media posts, 
        Marketing copy, Website content. 
        You can incorporate storytelling elements into your writing to make it more engaging and impactful.   

        You can adjust your writing style and tone to match the target audience and the desired effect. Options include: Informative, Persuasive, Humorous,
        Serious, Formal, Informal. 
        
        Your writing prowess extends beyond simply conveying information; you have a knack for restructuring
        and formatting content to enhance readability and engagement. Whether it's breaking down intricate
        ideas into clear, concise paragraphs or organizing key points into visually appealing lists,
        your articles are a masterclass in effective communication.

        Some of your signature writing techniques include:

        Utilizing subheadings and bullet points to break up long passages and improve scannability

        Employing analogies and real-world examples to simplify complex technical concepts

        Incorporating visuals, such as diagrams and infographics, to supplement the written content

        Varying sentence structure and length to maintain a dynamic flow throughout the article

        Crafting compelling introductions and conclusions that leave a lasting impact on readers

        Your ability to rewrite and polish rough drafts into publishable masterpieces is unparalleled.
        You have a meticulous eye for detail and a commitment to delivering content that not only informs
        but also engages and inspires. With your expertise, even the most technical and dry subject matter
        can be transformed into a riveting read.""",
        llm=Claude_Haiku,
        verbose=True,
        max_iter=5,
        memory=True,
        step_callback=lambda x: print_agent_output(x,"Content Writer"),
        allow_delegation=True,
        # tools=[search_tool],
    )

    file_saver = Agent(
        role='File Saver',
        goal='Take in information and write it to a Markdown file',
        backstory="""You are a efficient and simple agent that gets data and saves it to a markdown file. in a quick and efficient manner""",
        llm=Claude_Haiku,
        verbose=True,
        step_callback=lambda x: print_agent_output(x,"File Saving Agent"),
        tools=[save_content],
    )


    ## _________________________________Creating Tasks_______________________________________
    # Create tasks for your agents
    sourcing_website = Task(
    description=f"""Conduct a comprehensive analysis of the latest news advancements in an area
    given by the human. THE HUMAN has given his area of interest, i.e, onn{prompt}.\n
    The current time is {datetime.now()}. Focus on recent events related to the {prompt} topic.
    Identify key facts and useful information related to the Human's topic

    Compile you results into a useful and helpful report for the content writer to use to write an blog""",
    expected_output='A full report on the latest advancements in the specified human topic, leave nothing out',
    agent=data_scout,
    )

    write_content = Task(
    description="""Using the source material from the research specialist's report,
    write a compelling and informative blog post of 500 to 1000 words based on provided information, highlights the
    most significant information and advancements.
    Your blog is for all type of audience, i.e., for beginners, experts and general audience.
    Also make sure you optimizes the content for search engines. Provides factual information supported by reliable sources, 
    by giving links to relevant articles, research papers, or other resources to support the content.
    Your article should be engaging content i.e., Captures the audience's attention and keeps them interested.
    Follows a logical flow with a clear introduction, body paragraphs, and conclusion.
    Targeted Keywords, Naturally integrates relevant keywords throughout the text.
    DON'T overly 'Hype' the topic. Be factual and clear.
    Your final answer MUST be a full bog post of at least 500-1000 words and should contain
    a set of bullet points with the key facts at the end for a summary""",
    expected_output="""A compelling 500-1000 words blog with a set of bullet points with
    the key facts at the end for a summay. This should all be formated as markdown in an easy readable manner""",
    agent=content_writer,
    context=[sourcing_website]
    )


    save_output = Task(
    description="""Taking the post created by the writer, take this and save it to a markdown file.
    Your final answer MUST be a response must be showing that the file was saved .""",
    expected_output='A saved file name',
    agent=file_saver,
    context=[sourcing_website]
    )


    ## ________________________________ Initializing Crew_______________________________________
    # Instantiate your crew with a hierarchical process
    crew = Crew(
        agents=[data_scout, 
                content_writer, 
                file_saver],
        tasks=[sourcing_website,
            write_content,
            save_output],
        manager_llm=Claude_Opus,
        verbose=2,
        process=Process.hierarchical,
        full_output=True,
        share_crew=False,
        max_iter = 15,
        step_callback=lambda x: print_agent_output(x,"MasterCrew Agent")
    )


    ## _______________________________Kicking Off Crew__________________________________________
    # Kick off the crew's work
    results = crew.kickoff()
    return results
