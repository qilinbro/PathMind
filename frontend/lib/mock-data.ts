// Mock user data
export const users = [
  {
    id: 1,
    name: "Test User",
    email: "user@example.com",
    learning_style: "visual",
    overall_progress: 65,
    completed_paths: 2,
    active_paths: 3,
    completed_tests: 8,
    recent_activities: [
      {
        id: 1,
        type: "test",
        title: "JavaScript Basics Test",
        date: "2023-04-10",
        score: 85,
      },
      {
        id: 2,
        type: "path",
        title: "Web Development Fundamentals",
        date: "2023-04-08",
        progress: 75,
      },
      {
        id: 3,
        type: "assessment",
        title: "Learning Style Assessment",
        date: "2023-04-05",
        result: "Visual Learner",
      },
    ],
  },
]

// Mock learning paths
export const learningPaths = [
  {
    id: 1,
    title: "Python编程基础",
    description: "学习Python编程的基本概念和语法",
    enrolled: true,
    progress: 45,
    total_steps: 20,
    completed_steps: 9,
    estimated_time: "20小时",
    tags: ["编程", "Python", "初学者"],
  },
  {
    id: 2,
    title: "Web开发入门",
    description: "学习HTML、CSS和JavaScript的基础知识",
    enrolled: true,
    progress: 30,
    total_steps: 25,
    completed_steps: 7,
    estimated_time: "30小时",
    tags: ["Web开发", "HTML", "CSS", "JavaScript"],
  },
  {
    id: 3,
    title: "数据科学导论",
    description: "了解数据科学的基本概念和工具",
    enrolled: false,
    estimated_time: "25小时",
    tags: ["数据科学", "统计", "分析"],
  },
  {
    id: 4,
    title: "移动应用开发",
    description: "学习使用React Native开发移动应用",
    enrolled: false,
    estimated_time: "35小时",
    tags: ["移动开发", "React Native", "JavaScript"],
  },
]

// Mock assessment questions
export const assessmentQuestions = [
  {
    id: 1,
    text: "我喜欢通过图表和图像学习",
    info: "这有助于我们了解您是否是视觉学习者",
  },
  {
    id: 2,
    text: "我通过听讲解和讨论学习效果最好",
    info: "这有助于我们了解您是否是听觉学习者",
  },
  {
    id: 3,
    text: "我喜欢动手活动和实践练习",
    info: "这有助于我们了解您是否是动手学习者",
  },
  {
    id: 4,
    text: "我喜欢在学习新材料时做详细笔记",
    info: "这有助于我们了解您的笔记偏好",
  },
  {
    id: 5,
    text: "我更喜欢独自学习而不是小组学习",
    info: "这有助于我们了解您的社交学习偏好",
  },
]

// Mock content items
export const contentItems = [
  {
    id: 1,
    title: "Python变量和数据类型",
    description: "了解Python中的变量声明和基本数据类型",
    type: "文章",
    read_time: "10分钟",
    tags: ["Python", "编程基础"],
    content: "Python是一种高级编程语言，以其简洁的语法和易读性而闻名...",
  },
  {
    id: 2,
    title: "HTML结构和语义标签",
    description: "学习HTML文档的基本结构和语义标签的使用",
    type: "教程",
    read_time: "15分钟",
    tags: ["HTML", "Web开发"],
    content: "HTML（超文本标记语言）是构建网页的基础...",
  },
  {
    id: 3,
    title: "数据可视化基础",
    description: "了解数据可视化的基本原则和常用工具",
    type: "视频",
    read_time: "20分钟",
    tags: ["数据科学", "可视化"],
    content: "数据可视化是将数据转换为视觉表示的过程...",
  },
]

// Mock analytics data
export const analyticsData = {
  total_study_time: 465,
  average_score: 76,
  completed_tests: 8,
  study_sessions: 12,
  activity_data: [
    { date: "周一", minutes: 45 },
    { date: "周二", minutes: 60 },
    { date: "周三", minutes: 30 },
    { date: "周四", minutes: 90 },
    { date: "周五", minutes: 75 },
    { date: "周六", minutes: 120 },
    { date: "周日", minutes: 45 },
  ],
  performance_data: [
    { subject: "Python", score: 85 },
    { subject: "Web开发", score: 70 },
    { subject: "数据科学", score: 60 },
    { subject: "算法", score: 75 },
    { subject: "数据库", score: 90 },
  ],
  learning_style_data: [
    { name: "视觉", value: 60 },
    { name: "听觉", value: 20 },
    { name: "动手", value: 20 },
  ],
  strengths: [
    {
      title: "数据库",
      description: "您在数据库概念和SQL查询方面的得分始终很高。",
    },
    {
      title: "Python编程",
      description: "您的Python技能很强，特别是在数据结构方面。",
    },
  ],
  improvements: [
    {
      title: "数据科学",
      description: "专注于统计概念和数据可视化技术。",
    },
    {
      title: "Web开发",
      description: "加强JavaScript框架和响应式设计原则。",
    },
  ],
  behavior_analysis: {
    consistency: {
      description: "您倾向于在工作日更加一致地学习，周二和周四达到高峰。周末学习不太一致。",
      recommendation: "尝试建立更一致的周末学习习惯，以保持动力。",
    },
    duration: {
      description: "您的平均学习时间为45分钟，略低于最佳学习保留的推荐时间。",
      recommendation: "争取60-90分钟的专注学习时间，中间短暂休息。",
    },
    engagement: {
      description: "您最喜欢互动内容和视频教程，但花在基于文本的材料上的时间较少。",
      recommendation: "平衡您的学习，增加更多基于文本的资源，以提高阅读理解能力。",
    },
  },
}
