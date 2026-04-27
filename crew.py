from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List

@CrewBase
class MentalHealthApp():

    agents: List[Agent]
    tasks: List[Task]

    @agent
    def emotion_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['emotion_analyzer'],
            llm="openrouter/openai/gpt-4o-mini",
            max_tokens=500,
            verbose=True
        )

    @agent
    def cause_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['cause_analyzer'],
            llm="openrouter/openai/gpt-4o-mini",
            max_tokens=500,  
            verbose=True
        )

    @agent
    def action_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['action_planner'],
            llm="openrouter/openai/gpt-4o-mini",
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