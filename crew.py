import os

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from typing import List

load_dotenv()

@CrewBase
class MentalHealthApp():

    agents: List[Agent]
    tasks: List[Task]

    def _openrouter_llm(self) -> LLM:
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is missing. Add it to .env before running the app."
            )
        base = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1").strip()
        # CrewAI internals/plugins can still look for OpenAI-style env vars.
        # Mirror values so no sub-call accidentally hits OpenAI with OpenRouter key.
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENROUTER_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = base
        os.environ["OPENAI_BASE_URL"] = base
        return LLM(
            model="openai/gpt-4o-mini",
            api_key=api_key,
            base_url=base,
            api_base=base,
            provider="openrouter",
        )

    @agent
    def emotion_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['emotion_analyzer'],
            llm=self._openrouter_llm(),
            max_tokens=500,
            verbose=True
        )

    @agent
    def cause_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['cause_analyzer'],
            llm=self._openrouter_llm(),
            max_tokens=500,  
            verbose=True
        )

    @agent
    def action_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['action_planner'],
            llm=self._openrouter_llm(),
            max_tokens=500,  
            verbose=True
        )

    @task
    def analyze_emotion(self) -> Task:
        return Task(config=self.tasks_config['analyze_emotion'])

    @task
    def find_cause(self) -> Task:
        return Task(config=self.tasks_config['find_cause'])

    @task
    def create_plan(self) -> Task:
        return Task(config=self.tasks_config['create_plan'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=[
                self.analyze_emotion(),
                self.find_cause(),
                self.create_plan()
            ],
            process=Process.sequential,
            verbose=True
        )