"""
Optimized prompts for OpenAI web search functionality
These prompts are designed to trigger effective web search and return structured results
"""

def get_web_search_system_prompt() -> str:
    """Optimized system prompt for web search agent"""
    return """You are an expert research assistant with real-time web search capabilities.

Your primary function is to search the web for current, accurate information and provide comprehensive, well-structured responses with proper citations.

IMPORTANT INSTRUCTIONS:
1. Always search the web for current information about the user's query
2. Focus on recent developments, current facts, and up-to-date data
3. Provide specific details including dates, numbers, and sources
4. Structure your response with clear sections and bullet points
5. Always include source URLs when available
6. Be specific about when information was published or last updated

For each search, you should:
- Find multiple relevant sources
- Verify information across sources when possible
- Prioritize authoritative and credible sources
- Include both primary and secondary sources where applicable"""

def get_general_search_prompt(query: str) -> str:
    """Optimized prompt for general web search"""
    return f"""Please search the web RIGHT NOW for current information about: "{query}"

I need you to find and provide:

1. **Current Status/Latest Developments** (within the last 6 months)
   - What's happening now with {query}?
   - Any recent news, updates, or changes?

2. **Key Facts and Data**
   - Specific numbers, statistics, or measurements
   - Important dates and timelines
   - Current market conditions, prices, or rankings (if applicable)

3. **Authoritative Sources**
   - Official websites, press releases, or statements
   - News reports from credible outlets
   - Expert opinions or analysis

4. **Multiple Perspectives**
   - Different viewpoints or interpretations
   - Contrasting opinions if they exist

FORMAT YOUR RESPONSE AS:
## Current Information About {query}

### Latest Developments
[Recent news and updates with dates]

### Key Facts
• [Specific fact with source]
• [Another fact with source]

### Sources and References
1. [Source name] - [URL] (Date: [when published/accessed])
2. [Source name] - [URL] (Date: [when published/accessed])

SEARCH THE WEB NOW and provide detailed, current information."""

def get_academic_search_prompt(query: str) -> str:
    """Optimized prompt for academic/research web search"""
    return f"""Please search the web RIGHT NOW for academic and research information about: "{query}"

I need you to find current scholarly content including:

1. **Recent Academic Papers** (priority: last 2 years)
   - Paper titles and authors
   - Publication dates and journals
   - Key findings and methodologies
   - DOI numbers or direct links

2. **Research Institutions and Experts**
   - Leading researchers in this field
   - Universities or labs working on this topic
   - Recent publications or press releases

3. **Conference Papers and Presentations**
   - Recent conference proceedings
   - Workshop papers or poster sessions
   - Presentation slides or videos

4. **Preprint Servers and Archives**
   - arXiv papers
   - bioRxiv or other discipline-specific archives
   - Working papers from institutions

FORMAT YOUR RESPONSE AS:
## Academic Research on {query}

### Recent Papers and Publications
**Title**: [Paper title]
**Authors**: [Author names]
**Journal/Venue**: [Publication venue]
**Date**: [Publication date]
**Key Findings**: [Summary of main results]
**Source**: [URL or DOI]

### Leading Researchers and Institutions
• [Researcher name] at [Institution] - [Recent work summary]
• [Another researcher] at [Institution] - [Recent work summary]

### Conference Papers and Presentations
• [Conference name] ([Year]) - [Paper title by authors]

### Sources and Citations
1. [Full citation] - [URL]
2. [Full citation] - [URL]

SEARCH THE WEB NOW for current academic and research content."""

def get_news_search_prompt(query: str) -> str:
    """Optimized prompt for news and current events search"""
    return f"""Please search the web RIGHT NOW for the latest news about: "{query}"

I need you to find current news coverage including:

1. **Breaking News** (last 24-48 hours)
   - Latest headlines and developments
   - Real-time updates or live coverage

2. **Recent Coverage** (last 1-2 weeks)
   - Major news stories and articles
   - Analysis and opinion pieces
   - Follow-up reports

3. **Trending Topics**
   - What aspects are currently trending
   - Social media discussions or viral content
   - Public reactions or responses

4. **Official Statements**
   - Press releases from relevant organizations
   - Official government or company statements
   - Expert quotes and interviews

FORMAT YOUR RESPONSE AS:
## Latest News About {query}

### Breaking News (Last 24-48 Hours)
• [Headline] - [News outlet] ([Time/Date])
• [Another headline] - [News outlet] ([Time/Date])

### Recent Coverage (Last 1-2 Weeks)
• [Story title] - [Outlet] ([Date])
  Summary: [Brief description]

### Key Quotes and Statements
• "[Quote]" - [Attribution] ([Source, Date])

### Trending Aspects
• [What's trending and why]

### News Sources
1. [News outlet] - [Article title] - [URL] ([Date])
2. [News outlet] - [Article title] - [URL] ([Date])

SEARCH THE WEB NOW for the most current news and information."""

def get_technical_search_prompt(query: str) -> str:
    """Optimized prompt for technical/documentation search"""
    return f"""Please search the web RIGHT NOW for technical information about: "{query}"

I need you to find current technical documentation and resources:

1. **Official Documentation**
   - Official docs, API references, user guides
   - Getting started tutorials or quickstarts
   - Version history and changelogs

2. **Technical Specifications**
   - System requirements or compatibility
   - Performance benchmarks or comparisons
   - Technical limitations or constraints

3. **Code Examples and Repositories**
   - GitHub repositories or code samples
   - Stack Overflow discussions or solutions
   - Technical blog posts with implementations

4. **Community Resources**
   - Forums, Discord servers, or communities
   - User-generated tutorials or guides
   - Tips, tricks, and best practices

FORMAT YOUR RESPONSE AS:
## Technical Information for {query}

### Official Documentation
• [Doc title] - [URL] (Last updated: [Date])
• [Another doc] - [URL] (Last updated: [Date])

### Technical Specifications
• **Requirements**: [System/software requirements]
• **Performance**: [Benchmarks or performance data]
• **Compatibility**: [Version compatibility info]

### Code Examples and Repositories
• [Repository name] - [GitHub URL] ([Language])
  Description: [What it does]

### Community Resources
• [Forum/Community name] - [URL]
• [Tutorial title] - [URL] ([Author])

### Technical Sources
1. [Source] - [URL] ([Date])
2. [Source] - [URL] ([Date])

SEARCH THE WEB NOW for current technical information and documentation."""

def get_optimized_prompt(query: str, search_type: str = "general") -> str:
    """
    Get the optimized prompt based on search type

    Args:
        query: The search query
        search_type: Type of search (general, academic, news, technical)

    Returns:
        Optimized prompt string
    """
    prompt_map = {
        "general": get_general_search_prompt,
        "academic": get_academic_search_prompt,
        "news": get_news_search_prompt,
        "technical": get_technical_search_prompt
    }

    prompt_func = prompt_map.get(search_type, get_general_search_prompt)
    return prompt_func(query)

# Additional helper functions for prompt optimization

def add_urgency_indicators(prompt: str) -> str:
    """Add urgency indicators to trigger immediate web search"""
    urgency_phrases = [
        "SEARCH THE WEB RIGHT NOW",
        "Please find CURRENT information",
        "I need RECENT data",
        "Look up the LATEST information"
    ]

    # Add random urgency indicator if not already present
    if not any(phrase in prompt for phrase in urgency_phrases):
        prompt = "SEARCH THE WEB RIGHT NOW and " + prompt.lower()

    return prompt

def add_date_context(prompt: str) -> str:
    """Add current date context to encourage recent information"""
    current_date = datetime.now().strftime("%B %Y")
    date_context = f"\n\nNote: Today is {current_date}. Please prioritize information from {current_date} and recent months."

    return prompt + date_context

def add_source_requirements(prompt: str) -> str:
    """Add explicit source requirements"""
    source_requirements = """

IMPORTANT: You must include:
- Exact URLs for all sources
- Publication dates or last updated dates
- Author names when available
- Clear attribution for all facts and quotes"""

    return prompt + source_requirements