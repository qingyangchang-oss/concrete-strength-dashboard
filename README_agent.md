# Concrete Maturity Research Agent

An AI-powered research agent that gathers intelligence on:
- **Competitors** in the concrete maturity monitoring market
- **Global Studies** on concrete maturity methods
- **TMC Updates** on temperature-matched curing technology

## Setup

### 1. Install Dependencies

```bash
pip install claude-agent-sdk
```

### 2. Set Your API Key

Get your API key from [Anthropic Console](https://console.anthropic.com/)

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

### Interactive Mode (Default)
```bash
python research_agent.py
```

Then use commands:
- `competitors` - Research market competitors
- `studies` - Research academic studies
- `tmc` - Research TMC method updates
- `all` - Run all research topics
- `custom` - Enter a custom query
- `quit` - Exit

### Command Line Mode
```bash
# Research competitors only
python research_agent.py competitors

# Research academic studies
python research_agent.py studies

# Research TMC updates
python research_agent.py tmc

# Run all research topics
python research_agent.py all

# Interactive mode
python research_agent.py interactive
```

## Output

Reports are saved as markdown files:
- `research_competitors_YYYYMMDD.md`
- `research_studies_YYYYMMDD.md`
- `research_tmc_YYYYMMDD.md`
- `research_summary_YYYYMMDD.md` (executive summary)

## Research Topics

### Competitors
- Concrete maturity meter/sensor companies
- TMC system providers
- Smart monitoring solutions
- Maturity prediction software

### Global Studies
- Peer-reviewed papers (2023-2026)
- Maturity method accuracy studies
- Nurse-Saul vs Arrhenius comparisons
- High-performance concrete research

### TMC Updates
- Latest equipment and technology
- Standards (ASTM, EN, BS)
- Case studies
- IoT integration innovations

## Customization

Edit `RESEARCH_TOPICS` in `research_agent.py` to modify research focus areas.

## Cost Considerations

The agent uses Claude API calls with web search. Each research session typically uses:
- ~5-15 API calls per topic
- Estimated cost: $0.10-0.50 per topic

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
- Ensure you've exported the environment variable
- Check for typos in the key

**"claude-agent-sdk not found"**
- Run: `pip install claude-agent-sdk`

**Research times out**
- Some web searches may take longer
- Try running individual topics instead of "all"
