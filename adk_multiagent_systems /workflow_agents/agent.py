import os
import logging
import google.cloud.logging

from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools import exit_loop
from google.adk.models import Gemini

from google.genai import types

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


# =====================================
# LOGGING
# =====================================

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

logging.basicConfig(level=logging.INFO)


# =====================================
# LOAD ENV
# =====================================

load_dotenv()

model_name = os.getenv("MODEL")

RETRY_OPTIONS = types.HttpRetryOptions(
    initial_delay=1,
    attempts=6
)


# =====================================
# TOOLS
# =====================================

def append_to_state(
    tool_context: ToolContext,
    field: str,
    response: str
) -> dict:

    current = tool_context.state.get(field, [])

    tool_context.state[field] = current + [response]

    logging.info(f"เพิ่มข้อมูลใน state: {field}")

    return {"status": "success"}


def write_file(
    tool_context: ToolContext,
    directory: str,
    filename: str,
    content: str
) -> dict:

    os.makedirs(directory, exist_ok=True)

    path = os.path.join(directory, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    logging.info(f"เขียนไฟล์สำเร็จ: {path}")

    return {"status": "success"}


# =====================================
# WIKIPEDIA TOOL
# =====================================

wiki_tool = LangchainTool(
    tool=WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper()
    )
)


# =====================================
# INVESTIGATION TEAM (INITIAL)
# =====================================

admirer_agent_initial = Agent(

    name="admirer_agent_initial",

    model=Gemini(
        model=model_name,
        retry_options=RETRY_OPTIONS
    ),

    description="ค้นหาด้านบวก",

    instruction="""
ตอบเป็นภาษาไทยเท่านั้น

PROMPT:
{ PROMPT? }

คุณคือฝ่ายสนับสนุน

ใช้ Wikipedia tool เพื่อค้นหา:

- achievements
- accomplishments
- success
- positive impact
- legacy

สรุปข้อมูลเป็นภาษาไทย

ใช้ append_to_state

field = pos_data
""",

    tools=[wiki_tool, append_to_state]
)


critic_agent_initial = Agent(

    name="critic_agent_initial",

    model=Gemini(
        model=model_name,
        retry_options=RETRY_OPTIONS
    ),

    description="ค้นหาด้านลบ",

    instruction="""
ตอบเป็นภาษาไทยเท่านั้น

PROMPT:
{ PROMPT? }

คุณคือฝ่ายกล่าวหา

ใช้ Wikipedia tool เพื่อค้นหา:

- controversy
- criticism
- failures
- negative impact
- war crimes

สรุปข้อมูลเป็นภาษาไทย

ใช้ append_to_state

field = neg_data
""",

    tools=[wiki_tool, append_to_state]
)


investigation_team = ParallelAgent(

    name="investigation_team",

    sub_agents=[

        admirer_agent_initial,
        critic_agent_initial
    ]
)


# =====================================
# LOOP TEAM
# =====================================

admirer_agent_loop = Agent(

    name="admirer_agent_loop",

    model=Gemini(
        model=model_name,
        retry_options=RETRY_OPTIONS
    ),

    instruction="""
ตอบเป็นภาษาไทยเท่านั้น

PROMPT:
{ PROMPT? }

JUDGE FEEDBACK:
{ judge_feedback? }

ค้นหาข้อมูลด้านบวกเพิ่มเติมตาม feedback

ใช้ Wikipedia tool

บันทึกลง pos_data
""",

    tools=[wiki_tool, append_to_state]
)


critic_agent_loop = Agent(

    name="critic_agent_loop",

    model=Gemini(
        model=model_name,
        retry_options=RETRY_OPTIONS
    ),

    instruction="""
ตอบเป็นภาษาไทยเท่านั้น

PROMPT:
{ PROMPT? }

JUDGE FEEDBACK:
{ judge_feedback? }

ค้นหาข้อมูลด้านลบเพิ่มเติมตาม feedback

ใช้ Wikipedia tool

บันทึกลง neg_data
""",

    tools=[wiki_tool, append_to_state]
)


judge_agent = Agent(

    name="judge_agent",

    model=Gemini(
        model=model_name,
        retry_options=RETRY_OPTIONS
    ),

    instruction="""
ตอบเป็นภาษาไทยเท่านั้น

PROMPT:
{ PROMPT? }

POSITIVE DATA:
{ pos_data? }

NEGATIVE DATA:
{ neg_data? }

คุณคือผู้พิพากษา

ประเมินว่าข้อมูลทั้งสองฝั่งสมดุลหรือไม่

ถ้ายังไม่สมดุล:

ใช้ append_to_state

field = judge_feedback


ถ้าสมดุลแล้ว:

ใช้ exit_loop tool
""",

    tools=[
        append_to_state,
        exit_loop
    ]
)


trial_loop = LoopAgent(

    name="trial_loop",

    sub_agents=[

        admirer_agent_loop,
        critic_agent_loop,
        judge_agent

    ],

    max_iterations=5
)


# =====================================
# VERDICT AGENT
# =====================================

verdict_agent = Agent(

    name="verdict_agent",

    model=Gemini(
        model=model_name,
        retry_options=RETRY_OPTIONS
    ),

    instruction="""
ตอบเป็นภาษาไทยเท่านั้น

PROMPT:
{ PROMPT? }

POSITIVE DATA:
{ pos_data? }

NEGATIVE DATA:
{ neg_data? }

เขียนรายงานที่เป็นกลาง ประกอบด้วย:

1 บทนำ

2 ด้านบวก

3 ด้านลบ

4 วิเคราะห์อย่างเป็นกลาง

5 บทสรุป

ใช้ write_file tool

directory = historical_court

filename = {PROMPT}.txt

content = รายงานทั้งหมด
""",

    tools=[write_file]
)


# =====================================
# MAIN COURT SYSTEM
# =====================================

historical_court = SequentialAgent(

    name="historical_court",

    sub_agents=[

        investigation_team,

        trial_loop,

        verdict_agent

    ]
)


# =====================================
# ROOT AGENT
# =====================================

root_agent = Agent(

    name="root_agent",

    model=Gemini(
        model=model_name,
        retry_options=RETRY_OPTIONS
    ),

    instruction="""
ตอบเป็นภาษาไทยเท่านั้น

ถามผู้ใช้ว่าต้องการวิเคราะห์บุคคลหรือเหตุการณ์ใด

เมื่อผู้ใช้ตอบ:

ใช้ append_to_state

field = PROMPT

จากนั้นส่งต่อไป historical_court
""",

    tools=[append_to_state],

    sub_agents=[historical_court]
)
