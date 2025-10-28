## YoutubeRAG - TODO & Backlog

### ✅ Recently Completed

- ✅ Multi-agent CLI chat with memory (chat.py)
- ✅ PlannerAgent with catalog-driven retrieval decisions
- ✅ Conversation continuity with code-level enforcement (85% success)
- ✅ Query-aware catalog pruning (36K→80 values)
- ✅ Filter expansion with fuzzy matching
- ✅ Comprehensive development logging
- ✅ Documentation updated (CHAT.md, README.md, EXECUTION.md, env.example)
- ✅ Cleaned obsolete scripts (4 files removed from scripts/)
- ✅ Centralized index configuration in app/services/indexes.py

### 🔄 Active Priorities

- Use chat analysis to create evaluation framework for pipeline configurations
- Consider reorganizing file/folder structure (agents/ vs app/)

- create a flag on the export file after generating a document for question / answer pair to add that to the context
- it is missing some valuation of the content - for example, the source being a bigger yt channel with 2M followers means more then one with just a couple of thousands

- create an agent that takes an document ID and extract information from it that is useful to answer a query
- from a document (video) retrieve in order and combine all of their relations arrays, to have the grouped relations array for a whole video
- create a chunker that only splits the transcript if it is related to a totally different topic (or maybe a subtopic)
- create entry points that only retrieve the context and actually do not send them to the agents

-> Final work: write an article showing the different results depending on the configurations of the pipeline on different datasets.

FRONTEND

- create a visualizer for the graph with filters

1 - animated graph lines, scroll-based transitions
2 - my misson: but I need to give some explaination here to clarify things - this is not exactly a traditional portfolio not CV. It has elements of both, but this is more something to introduce myself and my current stage. I am a generalist and I am addicted in learning and I want to be able to expose myself for maybe find a mentor (once again, I am giving you this as a context, it doesn't mean that I want to say that directly). I am a self-taught software engineer with only 2 year of experience in a startup, so I think that the best way to become more atractive is showing how AI is impacting me, what already happened, what my vision is and where I want to go. All that said, I dont know yet what my mission will be.
3- a more immersive scroll experience where nav appears late

4 - No photo
5 - not sure yet, lets keep this question for later
6 - Should this include personal context

7 - vertical cards
8 - we should have a consistent structure - but not exactly the one you suggested. The main idea is show the impact of AI in each project. First the Sempre Fichas was resettled, second Raine was born using AI since the planning to coding and finally Knowledge Manager is agentic AI project that I am using to learn about the topic (both by the experience of doing and using it as a tool to manage my knowledge on the topic)
9 - show the architectural diagrams directly on each page (decide how to draw them - mermaid? what are the other options?)

10 - visual essay layout but I still want to explore the different options I have to do that
11 - no user's comments, it should stay static and quiet
12 - not blend into the projects, I want to keep it separeted but I am do not clearly see it how it interacts with CV / Professional Journey and About Section

13 - show this as a timeline visualization (scrollable vertical with icons for each era): more then describe the past eras, they should enrich the current era - self taught software enginner powered by AI
14 - I can provide a downloadable CV
15 - no logos

16 - not sure yet, lets keep this question for later
17 - not sure yet, lets keep this question for later
18 - the colors will be only the dark mode as I already decided in the other chat

19 - first-person
20 - you have in context mostly all the content needed to write all the texts, so you are going to write them all and them will work as my start version which I will improve and ask you for a final review
21 - I need clarification, more context and examples here so I can better decide

22 - I think that before deciding on that, I need to start deciding on the whole structure, specially the landing page. If a really have 4 sections, maybe a sidebar layout will make more sense. I am actually considering have the sections CV / Professional Journey, Writings / Reflections and About Section all in the landing page and make the projects the only individual section. I am not sure if this is the best approach, but in my view those 3 sections are only the context, what really matter are the projects. (or maybe it is the other way around, the landing page a 100% focused in the projects while the sessions will have the context information that could be accessed if the user wants).
23 - yes
24 - not sure yet, lets keep this question for later

25 - the most possible analytics, just to have an idea who's acessing, from where and how often. Maybe amplitude only.
26 - No SEO optimization
27 - We can consider, but no for the MVP

28 - no
29 - no
30 - I have no intention on implementing them

What I want:

- the user needs to have context on who I am beforehand, what my experiences and expertises were when AI changed the software landscape. One of the main goes is to show that I have qualities for this new world where AI is not only a new layer in the developer stack but also an extension of our minds. I see AI changing to be a second layer above the code languages where we can almost declaratively describe what we want to build. There is a profile changing for the new software creators, it is like we need more cognitive load on the coding process itself which give more space for holistic view of the projects, a possibility for the developer do parts of the work of PMs and designers and for a single person lead an entire project. I want to attract people who agreed with that totally or partially.
- for that reason I think i need to go with the Context-first approach, but we can adapt it to overcome some of its downsides.
- I also want to tell a story with the projects that kind of complements the context: starting with the modernization/refactor of my first project that made me open to AI coding tools. That experience empowered me to the second step that is Raine - a project where I am translating the vision of the founder into a project, where I could brainstorm, plan and define the user's experience and create a comprehensive documentation to finally build the MVP - where I literally used AI from the first step. These 2 projects will tell the story of using AI to empowered me as a software engineer and will even demonstrate that I am ready to build using the new stack. Finally, we get to the Knowledge Manager that shows modern development paradigms like Agentic Workflows and MCP.

- at 3 you mentioned the narratives, but even that Projects wont be first, it could use all that narratives the same way - there will be folks that will get to the page and will proabbly click on projects so they will fell like project first and I can sometimes share the projects page URL when I want someone to start from there. That said, we will build Context First by default, but the Project session should be in a way that it could also be the first when needed.

I was almost decided but I see that you recommended Projects-first and I really liked the Projects-first (Recommended skeleton) you output at (4)

I really like the following you mentioned in (6), this is actually one of the main ideas: "I want the site to feel like a living essay about becoming an AI-augmented engineer." BUT the projects are really important, they are the proff that I can do and not only talk, so we need to find a way to have the projects acessible.

(7) I like the idea of having "A hybrid compromise that preserves both" but you need to create a different hybrid approach to adapt to what I am poiting

FYI: Sempre Fichas — "From manual ops to a modern stack — how AI sped decision-making and rebuild choices." -> actually this would describe very well why I first built the system 2018 to 2023 (I hired a company, kept close and learn to code to progressively do it myself). AI was a great tool to make myself become independent and do a big refactor, updatading and optimating the whole project.

AI-augmented engineer or multiple-roles-and-engineer
