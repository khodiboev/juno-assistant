export const profile = {
  nickname: "Juno",
  name: "Jurabek Khodiboev",
  initials: "JK",
  role: "Full-stack developer · AI applications",
  location: "Seoul, South Korea · Open to full-time roles",
  bio:
    "I build web applications end to end — NestJS and GraphQL APIs, Next.js and React frontends, " +
    "Docker deployments — and add AI to them: image classifiers and retrieval-augmented chat. " +
    "M.S. in AI Business, SMIT (2026).",
  links: {
    github: "https://github.com/khodiboev",
    linkedin: "https://www.linkedin.com/in/jurabek-khodiboev-4bab4427b",
    email: "fikrchi@gmail.com",
  },
  downloads: [
    { label: "Download CV", href: "/files/Jurabek_Khodiboev_CV.pdf", available: false },
    { label: "Download portfolio", href: "/files/Jurabek_Khodiboev_Portfolio.pdf", available: false },
  ],
  projects: [
    {
      name: "Santa",
      summary: "Car marketplace · NestJS, GraphQL, Next.js",
      live: "http://santacar.tech",
      code: "https://github.com/khodiboev",
    },
    {
      name: "ColdBrew",
      summary: "Coffee e-commerce · Express, React, MongoDB",
      live: "http://187.127.220.109:3000",
      code: "https://github.com/khodiboev/coldbrew",
    },
    {
      name: "Menu Detector",
      summary: "Food image classifier · PyTorch · 94.8% balanced acc.",
      code: "https://github.com/khodiboev/computer_vision",
    },
    {
      name: "Juno Assistant",
      summary: "This chat · RAG with FastAPI, Qdrant, Qwen2.5",
      code: "https://github.com/khodiboev/juno-assistant",
    },
  ],
  skills: [
    "TypeScript",
    "NestJS",
    "GraphQL",
    "Next.js",
    "React",
    "MongoDB",
    "Python",
    "PyTorch",
    "FastAPI",
    "Docker",
  ],
  languages: "English · Uzbek · Turkish · Korean · Russian",
};

export const starterQuestions = [
  { topic: "Projects", question: "What tech stack does Santa use?" },
  { topic: "AI", question: "How accurate is the Menu Detector?" },
  { topic: "Education", question: "Where did Juno study?" },
  { topic: "Role", question: "What kind of job is Juno looking for?" },
  { topic: "This app", question: "How does this assistant work?" },
  { topic: "Hiring", question: "Does Juno need visa sponsorship?" },
];
