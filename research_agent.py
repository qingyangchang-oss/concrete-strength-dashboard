"""
Concrete Maturity Research Agent
================================
An AI agent that researches competitors, global studies, and updates
on concrete maturity and temperature-matched curing (TMC) methods.

Uses Claude Agent SDK with web search capabilities.
"""

import asyncio
import os
from datetime import datetime

# Check for claude-agent-sdk, provide installation instructions if missing
try:
    from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage
except ImportError:
    print("=" * 60)
    print("Claude Agent SDK not installed. Install it with:")
    print("  pip install claude-agent-sdk")
    print("=" * 60)
    exit(1)


# Research topics configuration
RESEARCH_TOPICS = {
    "competitors": """
        Research competitors in the concrete maturity monitoring market.
        Find companies that offer:
        - Concrete maturity meters/sensors
        - Temperature-matched curing (TMC) systems
        - Smart concrete monitoring solutions
        - Maturity-based strength prediction software

        For each competitor, identify:
        - Company name and location
        - Key products/services
        - Technology approach
        - Target market (construction, infrastructure, precast)
        - Recent news or developments
    """,

    "global_studies": """
        Research recent global studies and academic research on concrete maturity.
        Focus on:
        - Peer-reviewed papers from 2023-2026
        - Studies on maturity method accuracy
        - Comparisons of different maturity functions (Nurse-Saul, Arrhenius)
        - Research on high-performance concrete maturity
        - Studies on sustainable/green concrete maturity behavior

        Include:
        - Study title and authors
        - Key findings
        - Publication source
        - Relevance to industry practice
    """,

    "tmc_updates": """
        Research the latest updates on Temperature-Matched Curing (TMC) methods.
        Find information on:
        - Latest TMC equipment and technology
        - Best practices for TMC implementation
        - Standards and specifications (ASTM, EN, BS)
        - Case studies of TMC in construction projects
        - Innovations in TMC automation and IoT integration
        - Benefits and limitations of TMC vs standard curing

        Focus on practical applications and industry adoption.
    """
}


SYSTEM_PROMPT = """You are an expert researcher specializing in concrete technology,
construction materials, and civil engineering. Your task is to gather comprehensive,
accurate, and up-to-date information on concrete maturity methods and temperature-matched
curing (TMC) technology.

When researching:
1. Use WebSearch to find the latest information
2. Use WebFetch to get detailed content from authoritative sources
3. Prioritize academic papers, industry publications, and company websites
4. Include specific data, statistics, and citations where available
5. Organize findings in a clear, professional format
6. Note the date of information to ensure currency

Always cite your sources with URLs."""


async def run_research(topic_key: str, output_file: str):
    """Run research on a specific topic and save results"""

    topic_prompt = RESEARCH_TOPICS.get(topic_key)
    if not topic_prompt:
        print(f"Unknown topic: {topic_key}")
        return

    full_prompt = f"""
{topic_prompt}

After completing your research:
1. Compile all findings into a well-structured markdown report
2. Include an executive summary at the top
3. Organize by categories/themes
4. Include all source URLs as references
5. Save the report to: {output_file}

Current date: {datetime.now().strftime('%Y-%m-%d')}
"""

    print(f"\n{'='*60}")
    print(f"Starting research: {topic_key}")
    print(f"Output file: {output_file}")
    print(f"{'='*60}\n")

    try:
        async for message in query(
            prompt=full_prompt,
            options=ClaudeAgentOptions(
                allowed_tools=["WebSearch", "WebFetch", "Write", "Read", "Glob"],
                permission_mode="acceptEdits",
                system_prompt=SYSTEM_PROMPT,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(block.text)
                    elif hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]\n")
            elif isinstance(message, ResultMessage):
                print(f"\n{'='*60}")
                print(f"Research completed: {message.subtype}")
                print(f"{'='*60}\n")

    except Exception as e:
        print(f"Error during research: {e}")


async def run_full_research():
    """Run research on all topics"""

    timestamp = datetime.now().strftime('%Y%m%d')
    output_dir = os.path.dirname(os.path.abspath(__file__))

    tasks = [
        ("competitors", f"{output_dir}/research_competitors_{timestamp}.md"),
        ("global_studies", f"{output_dir}/research_studies_{timestamp}.md"),
        ("tmc_updates", f"{output_dir}/research_tmc_{timestamp}.md"),
    ]

    for topic_key, output_file in tasks:
        await run_research(topic_key, output_file)

    # Generate summary report
    summary_prompt = f"""
Create an executive summary report that combines the key findings from:
1. research_competitors_{timestamp}.md
2. research_studies_{timestamp}.md
3. research_tmc_{timestamp}.md

The summary should:
- Highlight the most important findings from each area
- Identify trends and opportunities
- Provide actionable insights for a concrete technology company
- Be concise (2-3 pages max)

Save to: {output_dir}/research_summary_{timestamp}.md
"""

    print("\n" + "="*60)
    print("Generating Executive Summary")
    print("="*60 + "\n")

    async for message in query(
        prompt=summary_prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)


async def interactive_research():
    """Interactive mode for custom research queries"""

    print("\n" + "="*60)
    print("Concrete Maturity Research Agent - Interactive Mode")
    print("="*60)
    print("\nCommands:")
    print("  competitors  - Research market competitors")
    print("  studies      - Research global academic studies")
    print("  tmc          - Research TMC method updates")
    print("  all          - Run all research topics")
    print("  custom       - Enter a custom research query")
    print("  quit         - Exit the agent")
    print()

    while True:
        try:
            command = input("\nEnter command: ").strip().lower()

            if command == "quit":
                print("Goodbye!")
                break
            elif command == "competitors":
                await run_research("competitors", "research_competitors.md")
            elif command == "studies":
                await run_research("global_studies", "research_studies.md")
            elif command == "tmc":
                await run_research("tmc_updates", "research_tmc.md")
            elif command == "all":
                await run_full_research()
            elif command == "custom":
                custom_query = input("Enter your research query: ").strip()
                if custom_query:
                    await run_research_custom(custom_query)
            else:
                print("Unknown command. Try: competitors, studies, tmc, all, custom, quit")

        except KeyboardInterrupt:
            print("\nInterrupted. Goodbye!")
            break


async def run_research_custom(query_text: str):
    """Run a custom research query"""

    output_file = f"research_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    full_prompt = f"""
Research the following topic related to concrete maturity and temperature-matched curing:

{query_text}

Provide comprehensive findings with:
1. Executive summary
2. Detailed findings organized by theme
3. Source citations with URLs
4. Recommendations or key takeaways

Save the report to: {output_file}
"""

    print(f"\nResearching: {query_text[:50]}...")
    print(f"Output: {output_file}\n")

    async for message in query(
        prompt=full_prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["WebSearch", "WebFetch", "Write", "Read"],
            permission_mode="acceptEdits",
            system_prompt=SYSTEM_PROMPT,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"\n[Tool: {block.name}]\n")


def main():
    """Main entry point"""
    import sys

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("="*60)
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print()
        print("Set it with:")
        print("  Windows: set ANTHROPIC_API_KEY=your-key-here")
        print("  Linux/Mac: export ANTHROPIC_API_KEY=your-key-here")
        print()
        print("Get your API key from: https://console.anthropic.com/")
        print("="*60)
        return

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "competitors":
            asyncio.run(run_research("competitors", "research_competitors.md"))
        elif command == "studies":
            asyncio.run(run_research("global_studies", "research_studies.md"))
        elif command == "tmc":
            asyncio.run(run_research("tmc_updates", "research_tmc.md"))
        elif command == "all":
            asyncio.run(run_full_research())
        elif command == "interactive":
            asyncio.run(interactive_research())
        else:
            print(f"Unknown command: {command}")
            print("Usage: python research_agent.py [competitors|studies|tmc|all|interactive]")
    else:
        # Default to interactive mode
        asyncio.run(interactive_research())


if __name__ == "__main__":
    main()
