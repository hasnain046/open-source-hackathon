// Realistic Mock Data for InflationIQ Platform

export const currentInflation = {
  rate: 4.82,
  changePrevMonth: -0.15,
  targetRate: 4.00,
  confidenceInterval: [4.65, 4.99],
  lastUpdated: "June 2026",
  quickStats: {
    foodRate: 5.42,
    energyRate: 3.10,
    coreRate: 4.25,
    wholesaleRate: 2.15
  }
};

export const forecastSummary = {
  lstmForecastNextMonth: 4.75,
  prophetForecastNextMonth: 4.78,
  confidenceScore: 94.5,
  direction: "downward", // upward, stable, downward
  dominantDriver: "Monetary Policy tightening & falling energy costs"
};

export const inflationForecast = [
  { month: "Jan 2026", historical: 5.10, lstm: 5.10, prophet: 5.10, lower: 5.10, upper: 5.10 },
  { month: "Feb 2026", historical: 5.02, lstm: 5.02, prophet: 5.02, lower: 5.02, upper: 5.02 },
  { month: "Mar 2026", historical: 4.95, lstm: 4.95, prophet: 4.95, lower: 4.95, upper: 4.95 },
  { month: "Apr 2026", historical: 4.88, lstm: 4.88, prophet: 4.88, lower: 4.88, upper: 4.88 },
  { month: "May 2026", historical: 4.82, lstm: 4.82, prophet: 4.82, lower: 4.82, upper: 4.82 },
  { month: "Jun 2026", historical: null, lstm: 4.75, prophet: 4.78, lower: 4.60, upper: 4.90 },
  { month: "Jul 2026", historical: null, lstm: 4.68, prophet: 4.72, lower: 4.48, upper: 4.88 },
  { month: "Aug 2026", historical: null, lstm: 4.60, prophet: 4.65, lower: 4.35, upper: 4.85 },
  { month: "Sep 2026", historical: null, lstm: 4.54, prophet: 4.58, lower: 4.25, upper: 4.82 },
  { month: "Oct 2026", historical: null, lstm: 4.48, prophet: 4.50, lower: 4.15, upper: 4.80 },
  { month: "Nov 2026", historical: null, lstm: 4.41, prophet: 4.44, lower: 4.02, upper: 4.78 },
  { month: "Dec 2026", historical: null, lstm: 4.35, prophet: 4.38, lower: 3.90, upper: 4.75 }
];

export const cpiCategories = [
  { name: "Food & Beverages", weight: 45.86, rate: 5.42, color: "#06b6d4", itemBreakdown: [
    { name: "Cereals", rate: 6.20, weight: 9.67 },
    { name: "Vegetables", rate: 8.50, weight: 6.04 },
    { name: "Pulses", rate: 7.10, weight: 2.38 },
    { name: "Milk & Products", rate: 4.80, weight: 6.25 }
  ]},
  { name: "Housing", weight: 10.07, rate: 4.10, color: "#6366f1", itemBreakdown: [
    { name: "Urban Rent", rate: 4.25, weight: 8.50 },
    { name: "Maintenance", rate: 3.80, weight: 1.57 }
  ]},
  { name: "Fuel & Light", weight: 6.84, rate: 3.10, color: "#f59e0b", itemBreakdown: [
    { name: "LPG Gas", rate: 2.50, weight: 3.20 },
    { name: "Electricity", rate: 3.90, weight: 2.80 },
    { name: "Kerosene", rate: 2.10, weight: 0.84 }
  ]},
  { name: "Clothing & Footwear", weight: 6.53, rate: 5.12, color: "#ec4899", itemBreakdown: [
    { name: "Clothing", rate: 5.25, weight: 5.40 },
    { name: "Footwear", rate: 4.50, weight: 1.13 }
  ]},
  { name: "Miscellaneous / Services", weight: 28.32, rate: 4.25, color: "#10b981", itemBreakdown: [
    { name: "Transport & Comm.", rate: 3.90, weight: 8.59 },
    { name: "Education", rate: 5.10, weight: 4.46 },
    { name: "Health & Care", rate: 6.15, weight: 5.89 },
    { name: "Personal Care", rate: 4.05, weight: 9.38 }
  ]}
];

export const historicalTrends = [
  { year: "2017", rate: 3.33, growth: 6.8 },
  { year: "2018", rate: 3.94, growth: 6.5 },
  { year: "2019", rate: 3.73, growth: 6.1 },
  { year: "2020", rate: 6.62, growth: -5.8 },
  { year: "2021", rate: 5.13, growth: 8.7 },
  { year: "2022", rate: 6.70, growth: 7.2 },
  { year: "2023", rate: 5.65, growth: 6.3 },
  { year: "2024", rate: 5.40, growth: 6.8 },
  { year: "2025", rate: 4.98, growth: 7.1 },
  { year: "2026 (YTD)", rate: 4.82, growth: 7.3 }
];

export const detailedHistoricalTrends = [
  { date: "2021-06", inflation: 5.30, food: 5.15, fuel: 12.60, core: 5.40 },
  { date: "2021-12", inflation: 5.66, food: 5.40, fuel: 11.20, core: 5.85 },
  { date: "2022-06", inflation: 7.01, food: 7.50, fuel: 10.10, core: 6.40 },
  { date: "2022-12", inflation: 5.72, food: 5.20, fuel: 8.40, core: 6.10 },
  { date: "2023-06", inflation: 4.87, food: 4.60, fuel: 3.90, core: 5.10 },
  { date: "2023-12", inflation: 5.69, food: 9.50, fuel: -0.70, core: 3.80 },
  { date: "2024-06", inflation: 5.08, food: 8.10, fuel: -3.20, core: 3.15 },
  { date: "2024-12", inflation: 5.12, food: 7.90, fuel: -2.80, core: 3.50 },
  { date: "2025-06", inflation: 4.95, food: 6.20, fuel: 1.10, core: 4.10 },
  { date: "2025-12", inflation: 5.01, food: 6.80, fuel: 2.90, core: 4.30 },
  { date: "2026-06", inflation: 4.82, food: 5.42, fuel: 3.10, core: 4.25 }
];

export const newsSentiment = [
  {
    id: 1,
    headline: "Central Bank retains policy repo rate at 6.50% to align inflation back to 4.0% target",
    source: "Financial Bulletin",
    time: "2 hours ago",
    sentiment: "Bullish", // Bullish = positive for curbing inflation (interest rate hike/retained)
    impactScore: 78,
    category: "Monetary Policy"
  },
  {
    id: 2,
    headline: "Crude oil prices decline below $78 per barrel amid supply increase reports",
    source: "Global Market Monitor",
    time: "4 hours ago",
    sentiment: "Bullish", // Lower crude is good for lowering inflation
    impactScore: 85,
    category: "Commodities"
  },
  {
    id: 3,
    headline: "El Niño weather pattern threatens local crop yields; Pulse and Veg pricing expected to rise",
    source: "Agricultural Times",
    time: "1 day ago",
    sentiment: "Bearish", // High food prices
    impactScore: 92,
    category: "Agriculture"
  },
  {
    id: 4,
    headline: "Local currency gains strength against USD, easing pressure on import costs of key electronics",
    source: "FX Journal",
    time: "1 day ago",
    sentiment: "Bullish", // Currency strength lowers inflation
    impactScore: 68,
    category: "Currency"
  },
  {
    id: 5,
    headline: "Supply chain disruptions reported at key shipping terminals due to port maintenance scheduling",
    source: "Logistics Weekly",
    time: "2 days ago",
    sentiment: "Neutral",
    impactScore: 45,
    category: "Supply Chain"
  }
];

export const currencyAndCommodities = [
  { month: "Jan 2026", usdInr: 83.15, eurUsd: 1.09, crude: 79.40, gold: 62500 },
  { month: "Feb 2026", usdInr: 83.22, eurUsd: 1.08, crude: 81.10, gold: 63100 },
  { month: "Mar 2026", usdInr: 82.95, eurUsd: 1.10, crude: 84.50, gold: 64200 },
  { month: "Apr 2026", usdInr: 82.80, eurUsd: 1.11, crude: 83.20, gold: 65000 },
  { month: "May 2026", usdInr: 82.65, eurUsd: 1.12, crude: 80.50, gold: 66800 },
  { month: "Jun 2026", usdInr: 82.52, eurUsd: 1.13, crude: 77.80, gold: 67200 }
];

export const regionalInflation = [
  { state: "Maharashtra", region: "West", currentRate: 4.88, yearAgoRate: 5.20, status: "Medium" },
  { state: "Tamil Nadu", region: "South", currentRate: 5.25, yearAgoRate: 5.80, status: "High" },
  { state: "Uttar Pradesh", region: "North", currentRate: 4.60, yearAgoRate: 5.01, status: "Medium" },
  { state: "Karnataka", region: "South", currentRate: 4.90, yearAgoRate: 5.30, status: "Medium" },
  { state: "Gujarat", region: "West", currentRate: 4.10, yearAgoRate: 4.70, status: "Low" },
  { state: "West Bengal", region: "East", currentRate: 5.42, yearAgoRate: 6.10, status: "High" },
  { state: "Rajasthan", region: "North", currentRate: 5.10, yearAgoRate: 5.50, status: "High" },
  { state: "Madhya Pradesh", region: "Central", currentRate: 4.52, yearAgoRate: 4.80, status: "Low" },
  { state: "Kerala", region: "South", currentRate: 4.05, yearAgoRate: 4.60, status: "Low" },
  { state: "Bihar", region: "East", currentRate: 5.30, yearAgoRate: 6.02, status: "High" },
  { state: "Punjab", region: "North", currentRate: 4.75, yearAgoRate: 5.15, status: "Medium" }
];

export const alertsHistory = [
  { id: 1, title: "CPI Headline Update", message: "India CPI for May 2026 drops to 4.82%, lower than Wall Street estimates of 4.90%.", severity: "Low", date: "June 6, 2026", read: false, channel: "System" },
  { id: 2, title: "Vegetable Spike Warning", message: "Agriculture price sub-indices indicate a 12% rise in wholesale potato & onion prices over 7 days.", severity: "High", date: "June 4, 2026", read: false, channel: "Email & Telegram" },
  { id: 3, title: "Oil Threshold Triggered", message: "Brent Crude falls below your preset trigger of $80.00/bbl (currently trading at $77.80).", severity: "Medium", date: "June 2, 2026", read: true, channel: "System" },
  { id: 4, title: "Exchange Rate Alert", message: "USD/INR dips below 82.60, strengthening the Rupee and lowering commodity landing costs.", severity: "Medium", date: "May 28, 2026", read: true, channel: "Telegram" }
];

export const adminLogs = {
  activeUsers: 1420,
  requestsHandled: 23568,
  dbSize: "42.8 MB",
  cronStatus: "Active",
  modelTraining: {
    lastTrained: "June 1, 2026",
    accuracyR2: 0.962,
    errorsLogged: 0
  },
  pipelineStats: {
    fredConnection: "Connected",
    blsConnection: "Connected",
    scrapingStatus: "Operational"
  }
};

export const economistSuggestions = [
  { q: "What is the forecast for food inflation next quarter?", label: "Food Forecast" },
  { q: "Explain the contribution of crude oil drop on CPI predictions.", label: "Oil Impact" },
  { q: "What policy adjustments should the Central Bank perform?", label: "Policy Suggestion" },
  { q: "Which states have the highest inflation rates and why?", label: "State Analysis" }
];

export const mockChatAnswers = {
  "What is the forecast for food inflation next quarter?": 
    "According to the InflationIQ LSTM forecasting engine, **food inflation is projected to decline from 5.42% to approximately 5.10% over the next quarter**. This is driven by strong projections for monsoons easing agricultural output limitations, offsetting local El Niño risks. However, vegetables remain highly sensitive to local transport rate fluctuations.",
  "Explain the contribution of crude oil drop on CPI predictions.": 
    "Brent Crude Oil drop from $83.20 to $77.80 per barrel has a direct pass-through deflationary effect. Our model estimates that **every $10 drop in crude prices yields a -22 bps reduction in the aggregate CPI headline rate**, primarily by decreasing freight, cargo shipping expenses, and chemical production inputs.",
  "What policy adjustments should the Central Bank perform?": 
    "With CPI currently standing at 4.82% (approaching the target of 4.00%), our policy models recommend that the **Central Bank maintain interest rates at 6.50% for one more cycle before introducing a mild 25 bps rate cut in Q4**. Tightening prematurely might stunt GDP growth, whereas easing too fast could trigger minor food pricing shocks.",
  "Which states have the highest inflation rates and why?": 
    "Currently, **West Bengal (5.42%), Bihar (5.30%), and Tamil Nadu (5.25%)** show the highest consumer prices. In West Bengal and Bihar, local supply chain inefficiencies and high agricultural distribution margins are the primary drivers. In Tamil Nadu, urban housing rent demands and high services inflation are keeping headline metrics elevated compared to Karnataka or Kerala (4.05%)."
};
