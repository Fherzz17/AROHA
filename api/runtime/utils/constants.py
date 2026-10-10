"""
SkillPulse Bharat - Domain Constants and Taxonomy
Team: Syntax Society
"""

SKILL_TAXONOMY = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "Go", "Rust", "C#"
    ],
    "Data & AI": [
        "Machine Learning", "Deep Learning", "SQL", "Pandas", "Scikit-learn", 
        "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Data Analysis", 
        "Tableau", "Power BI", "Apache Spark", "Hadoop"
    ],
    "Emerging & Frontier AI": [
        "Generative AI", "RAG", "LLMs", "Prompt Engineering", "LangChain", 
        "Vector Databases", "Agentic AI", "MLOps", "Fine-Tuning"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", 
        "CI/CD", "Linux", "Git", "Ansible", "Microservices"
    ],
    "Web & Backend": [
        "React", "Node.js", "FastAPI", "Django", "Flask", "Next.js", 
        "Express", "GraphQL", "REST APIs", "HTML/CSS"
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Snowflake"
    ],
    "Cybersecurity & Architecture": [
        "Cybersecurity", "Network Security", "Cloud Security", 
        "Penetration Testing", "System Design"
    ]
}

TARGET_ROLES = [
    "Python Developer",
    "Data Analyst",
    "Data Scientist",
    "AI/ML Engineer",
    "Software Developer",
    "Cloud/DevOps Architect",
    "Fullstack Developer",
    "Cybersecurity Analyst"
]

ROLE_SKILL_PROFILES = {
    "Python Developer": {
        "core": ["Python", "Django", "FastAPI", "SQL", "Git", "REST APIs"],
        "complementary": ["Docker", "PostgreSQL", "Redis", "Linux", "AWS"],
        "emerging": ["Generative AI", "LangChain", "Vector Databases"],
        "desc": "Builds scalable backend services, automated workflows, and data-centric applications in Python."
    },
    "Data Analyst": {
        "core": ["SQL", "Python", "Power BI", "Tableau", "Data Analysis", "Pandas"],
        "complementary": ["PostgreSQL", "Statistics", "Machine Learning", "Excel"],
        "emerging": ["Generative AI", "Prompt Engineering", "Snowflake"],
        "desc": "Transforms raw enterprise data into actionable visual insights, KPIs, and statistical dashboards."
    },
    "Data Scientist": {
        "core": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-learn", "Statistics"],
        "complementary": ["Deep Learning", "NLP", "Tableau", "Docker", "Apache Spark"],
        "emerging": ["Generative AI", "LLMs", "RAG", "MLOps"],
        "desc": "Designs predictive algorithms, probabilistic models, and deep analytics pipelines from complex data."
    },
    "AI/ML Engineer": {
        "core": ["Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning", "Scikit-learn"],
        "complementary": ["Docker", "Kubernetes", "Linux", "FastAPI", "Git"],
        "emerging": ["Generative AI", "LLMs", "RAG", "MLOps", "Vector Databases", "Agentic AI"],
        "desc": "Engineers and deploys state-of-the-art neural architectures, fine-tunes LLMs, and builds production AI."
    },
    "Software Developer": {
        "core": ["Java", "Python", "JavaScript", "SQL", "Git", "REST APIs", "Data Structures"],
        "complementary": ["Docker", "PostgreSQL", "Linux", "CI/CD", "Microservices"],
        "emerging": ["Cloud", "Generative AI", "Kubernetes"],
        "desc": "Designs, writes, tests, and maintains robust application logic across the full development lifecycle."
    },
    "Cloud/DevOps Architect": {
        "core": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"],
        "complementary": ["Azure", "GCP", "Python", "Git", "Microservices", "Ansible"],
        "emerging": ["Cloud Security", "MLOps", "Generative AI"],
        "desc": "Architects resilient multi-cloud infrastructure, continuous delivery pipelines, and container orchestrations."
    },
    "Fullstack Developer": {
        "core": ["React", "JavaScript", "TypeScript", "Node.js", "HTML/CSS", "REST APIs"],
        "complementary": ["Next.js", "PostgreSQL", "MongoDB", "Docker", "Git"],
        "emerging": ["Generative AI", "LangChain", "Cloud"],
        "desc": "Crafts responsive end-user experiences and high-throughput server backends with modern web tech."
    },
    "Cybersecurity Analyst": {
        "core": ["Cybersecurity", "Network Security", "Linux", "Python", "Penetration Testing"],
        "complementary": ["Cloud Security", "Docker", "AWS", "Git"],
        "emerging": ["AI Security", "Zero Trust", "Generative AI"],
        "desc": "Protects organizational infrastructure against threat vectors, auditing vulnerabilities and compliance."
    }
}

INDIAN_LOCATIONS = [
    "Bengaluru, Karnataka",
    "Hyderabad, Telangana",
    "Pune, Maharashtra",
    "Gurugram, NCR",
    "Noida, NCR",
    "Mumbai, Maharashtra",
    "Chennai, Tamil Nadu",
    "Remote (India)"
]

INDUSTRIES = [
    "FinTech & Banking",
    "E-Commerce & Retail",
    "SaaS & Enterprise Cloud",
    "IT Services & Consulting",
    "HealthTech",
    "AI & Frontier Startups",
    "EdTech & Upskilling",
    "Automotive & IoT"
]

TOP_COMPANIES = [
    "Tata Consultancy Services", "Infosys", "Wipro", "HCLTech",
    "Flipkart", "Zomato", "Swiggy", "Paytm", "PhonePe", "Razorpay",
    "Reliance Jio", "Amazon India", "Microsoft India", "Google India",
    "Groww", "Zerodha", "CRED", "Freshworks", "Zoho Corporation",
    "Airtel Digital", "Ola Electric", "Darwinbox", "Postman India"
]
