"""
Skill Normalization Engine for SkillPulse Bharat
Standardizes industry jargon, abbreviations, and syntactic variations into canonical skill tags.
Team: Syntax Society
"""

import re
from typing import Dict, Optional, Set

ALIAS_MAPPINGS: Dict[str, str] = {
    # Programming Languages
    "python": "Python",
    "python programming": "Python",
    "python3": "Python",
    "python 3": "Python",
    "java": "Java",
    "core java": "Java",
    "java 8": "Java",
    "java 17": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "ecmascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "c++": "C++",
    "cpp": "C++",
    "golang": "Go",
    "go lang": "Go",
    "go": "Go",
    "rust": "Rust",
    "rust lang": "Rust",
    "c#": "C#",
    "csharp": "C#",
    "dotnet": ".NET",
    ".net": ".NET",

    # AI, ML & Frontier
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "generative ai": "Generative AI",
    "gen ai": "Generative AI",
    "genai": "Generative AI",
    "generative artificial intelligence": "Generative AI",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language model": "LLMs",
    "large language models": "LLMs",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "retrieval-augmented generation": "RAG",
    "langchain": "LangChain",
    "lang chain": "LangChain",
    "llamaindex": "LlamaIndex",
    "llama index": "LlamaIndex",
    "vector database": "Vector Databases",
    "vector databases": "Vector Databases",
    "vector db": "Vector Databases",
    "pinecone": "Vector Databases",
    "weaviate": "Vector Databases",
    "chromadb": "Vector Databases",
    "chroma": "Vector Databases",
    "qdrant": "Vector Databases",
    "agentic ai": "Agentic AI",
    "ai agents": "Agentic AI",
    "autonomous agents": "Agentic AI",
    "prompt engineering": "Prompt Engineering",
    "fine-tuning": "Fine-Tuning",
    "finetuning": "Fine-Tuning",
    "model fine tuning": "Fine-Tuning",
    "mlops": "MLOps",
    "machine learning operations": "MLOps",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",

    # Data Analytics & BI
    "sql": "SQL",
    "structured query language": "SQL",
    "advanced sql": "SQL",
    "sas": "SAS",
    "sas programming": "SAS",
    "sas analytics": "SAS",
    "big data": "Big Data",
    "big data skills": "Big Data",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "ms power bi": "Power BI",
    "tableau": "Tableau",
    "tableau desktop": "Tableau",
    "data analysis": "Data Analysis",
    "data analytics": "Data Analysis",
    "statistics": "Statistics",
    "statistical analysis": "Statistics",
    "maths": "Statistics",
    "mathematics": "Statistics",
    "excel": "Excel",
    "advanced excel": "Excel",
    "ms excel": "Excel",
    "apache spark": "Big Data",
    "spark": "Big Data",
    "pyspark": "Big Data",
    "hadoop": "Big Data",
    "snowflake": "Snowflake",
    "snow": "ServiceNow",
    "servicenow": "ServiceNow",
    "servicenow developer": "ServiceNow",

    # Cloud & DevOps
    "amazon web services": "AWS",
    "aws": "AWS",
    "aws cloud": "AWS",
    "microsoft azure": "Azure",
    "azure": "Azure",
    "azure cloud": "Azure",
    "google cloud platform": "GCP",
    "google cloud": "GCP",
    "gcp": "GCP",
    "docker": "Docker",
    "docker containers": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "linux": "Linux",
    "git": "Git",
    "github": "Git",
    "gitlab": "Git",
    "microservices": "Microservices",
    "system design": "System Design",

    # Web & Frameworks
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node": "Node.js",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "express": "Express",
    "express.js": "Express",
    "graphql": "GraphQL",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "html": "HTML/CSS",
    "css": "HTML/CSS",
    "html/css": "HTML/CSS",
    "html5": "HTML/CSS",

    # Databases
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",

    # Security
    "cybersecurity": "Cybersecurity",
    "cyber security": "Cybersecurity",
    "infosec": "Cybersecurity",
    "information security": "Cybersecurity",
    "network security": "Network Security",
    "cloud security": "Cloud Security",
    "penetration testing": "Penetration Testing",
    "pen testing": "Penetration Testing",
    "ethical hacking": "Penetration Testing"
}

# Pre-compile canonical skill list for fast exact matching
CANONICAL_SKILLS: Set[str] = set(ALIAS_MAPPINGS.values())


def normalize_skill(raw_name: str) -> Optional[str]:
    """
    Normalizes a single skill string or abbreviation to its canonical form.
    Returns canonical name, or formatted title if not in dictionary.
    """
    if not raw_name:
        return None
    cleaned = raw_name.strip().lower()
    # Direct dictionary lookup
    if cleaned in ALIAS_MAPPINGS:
        return ALIAS_MAPPINGS[cleaned]
    # Check punctuation variations (e.g. hyphens or dots)
    cleaned_no_punct = re.sub(r'[\.\-_/]', ' ', cleaned).strip()
    if cleaned_no_punct in ALIAS_MAPPINGS:
        return ALIAS_MAPPINGS[cleaned_no_punct]
    
    # Capitalize title if reasonably short identifier
    if len(raw_name) <= 30:
        return raw_name.strip().title()
    return None
