/**
 * 模拟用户数据
 */
export const users = [
  {
    id: 1,
    name: "测试用户",
    email: "test@example.com",
    learningStyle: "视觉",
    overallProgress: 35,
    completedPaths: 1,
    activePaths: 2,
    completedTests: 3,
    assessment: {
      visual_score: 75,
      auditory_score: 45,
      kinesthetic_score: 60,
      reading_score: 50,
      dominant_style: "visual",
      secondary_style: "kinesthetic"
    }
  },
  {
    id: 2,
    name: "张三",
    email: "zhang@example.com",
    learningStyle: "听觉",
    overallProgress: 42,
    completedPaths: 2,
    activePaths: 1,
    completedTests: 5,
    assessment: {
      visual_score: 50,
      auditory_score: 80,
      kinesthetic_score: 40,
      reading_score: 60,
      dominant_style: "auditory",
      secondary_style: "reading"
    }
  },
  {
    id: 3,
    name: "李四",
    email: "li@example.com",
    learningStyle: "动觉",
    overallProgress: 28,
    completedPaths: 0,
    activePaths: 3,
    completedTests: 2,
    assessment: {
      visual_score: 40,
      auditory_score: 35,
      kinesthetic_score: 85,
      reading_score: 30,
      dominant_style: "kinesthetic",
      secondary_style: "visual"
    }
  }
];

/**
 * 模拟自适应测试数据
 */
export const adaptiveTests = [
  {
    id: 1,
    title: "Python基础知识测试",
    description: "测试您对Python编程基础的理解",
    estimatedTime: "30分钟",
    difficulty: "初级",
    questions: 15,
    tags: ["Python", "编程"],
    instructions: [
      "本测试包含15个多选题",
      "每个问题只有一个正确答案",
      "测试时间为30分钟",
      "您可以随时暂停测试",
      "完成后将显示您的得分和详细分析",
    ]
  },
  {
    id: 2,
    title: "Web开发概念测试",
    description: "测试您对Web开发原理的理解",
    estimatedTime: "45分钟",
    difficulty: "中级",
    questions: 20,
    tags: ["Web", "HTML", "CSS", "JavaScript"],
    instructions: [
      "本测试包含20个多选题",
      "每个问题只有一个正确答案",
      "测试时间为45分钟",
      "您可以随时暂停测试",
      "完成后将显示您的得分和详细分析",
    ]
  },
  {
    id: 3,
    title: "数据科学基础测试",
    description: "评估您的数据科学知识",
    estimatedTime: "60分钟",
    difficulty: "高级",
    questions: 25,
    tags: ["数据科学", "统计", "Python"],
    instructions: [
      "本测试包含25个多选题",
      "每个问题只有一个正确答案",
      "测试时间为60分钟",
      "您可以随时保存进度",
      "完成后将生成详细的能力分析报告",
    ]
  }
];

/**
 * 模拟测试问题数据
 */
export const testQuestions = {
  1: [
    {
      id: 1,
      text: "在Python中，哪个关键字用于定义函数？",
      options: [
        { id: "a", text: "function" },
        { id: "b", text: "def" },
        { id: "c", text: "define" },
        { id: "d", text: "func" },
      ],
      explanation: "在Python中，'def'关键字用于定义函数。",
      correctOption: "b"
    },
    {
      id: 2,
      text: "以下哪个不是Python的内置数据类型？",
      options: [
        { id: "a", text: "list" },
        { id: "b", text: "dictionary" },
        { id: "c", text: "array" },
        { id: "d", text: "tuple" },
      ],
      explanation: "在Python中，'array'不是内置数据类型，而是需要通过导入array模块才能使用。",
      correctOption: "c"
    },
    {
      id: 3,
      text: "在Python中，如何获取字符串的长度？",
      options: [
        { id: "a", text: "str.length()" },
        { id: "b", text: "length(str)" },
        { id: "c", text: "len(str)" },
        { id: "d", text: "str.size()" },
      ],
      explanation: "在Python中，使用len()函数来获取字符串的长度。",
      correctOption: "c"
    }
  ],
  2: [
    {
      id: 1,
      text: "在HTML中，哪个标签用于创建超链接？",
      options: [
        { id: "a", text: "<link>" },
        { id: "b", text: "<a>" },
        { id: "c", text: "<href>" },
        { id: "d", text: "<url>" },
      ],
      explanation: "在HTML中，<a>标签用于创建超链接。",
      correctOption: "b"
    }
  ],
  3: [
    {
      id: 1,
      text: "在数据科学中，哪一项不是描述性统计的度量？",
      options: [
        { id: "a", text: "平均值" },
        { id: "b", text: "中位数" },
        { id: "c", text: "T检验" },
        { id: "d", text: "标准差" },
      ],
      explanation: "T检验是推断统计的一部分，而不是描述性统计。",
      correctOption: "c"
    }
  ]
};

/**
 * 模拟测试结果数据
 */
export const testResults = {
  1: {
    score: 67,
    totalQuestions: 15,
    correctAnswers: 10,
    timeSpent: "18:24",
    strengths: ["变量和数据类型", "基本语法"],
    weaknesses: ["函数", "异常处理"],
    recommendations: [
      "复习Python函数的定义和使用", 
      "学习更多关于异常处理的知识", 
      "尝试完成更多实践项目来巩固基础知识"
    ],
    questionAnalysis: [
      { id: 1, correct: true, topic: "基本语法", difficulty: "简单" },
      { id: 2, correct: false, topic: "数据类型", difficulty: "中等" },
      { id: 3, correct: true, topic: "函数", difficulty: "中等" }
    ]
  }
};
