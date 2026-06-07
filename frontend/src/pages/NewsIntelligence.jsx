import React, { useState } from 'react';
import { Newspaper, MessageSquare, Flame, CheckCircle, SlidersHorizontal, Search } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { newsSentiment } from '../mockData/inflationData';

export const NewsIntelligence = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Filter headlines
  const filteredHeadlines = newsSentiment.filter(item => {
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    const matchesSearch = item.headline.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          item.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const categories = ['All', 'Monetary Policy', 'Commodities', 'Agriculture', 'Currency', 'Supply Chain'];

  // Count sentiments
  const bullishCount = newsSentiment.filter(n => n.sentiment === 'Bullish').length;
  const bearishCount = newsSentiment.filter(n => n.sentiment === 'Bearish').length;

  return (
    <div className="space-y-8">
      {/* Top action header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-900/40 p-6 rounded-2xl border border-slate-800/40">
        <div>
          <h2 className="text-xl font-bold font-display text-white">News Sentiment Intelligence</h2>
          <p className="text-xs text-slate-400 mt-1">Parse news headlines to classify macro sentiment and calculate market inflation pressure scores.</p>
        </div>
        
        {/* Search Feed */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-950 border border-slate-900 focus-within:border-cyan-500/50 transition-colors w-64">
          <Search size={16} className="text-slate-500" />
          <input 
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search economic articles..."
            className="bg-transparent text-xs text-slate-300 focus:outline-none w-full"
          />
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Overall News Sentiment"
          value="Bullish"
          change={12.4}
          trend="up"
          subtitle="Net Deflationary Sentiment"
          icon={Newspaper}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Bullish Signals Ingested"
          value={bullishCount}
          change={1}
          trend="up"
          subtitle="Support price stabilization"
          icon={CheckCircle}
          isPercentage={false}
          status="positive"
        />
        <MetricCard
          title="Bearish Signals Ingested"
          value={bearishCount}
          change={0}
          trend="stable"
          subtitle="Exerting upward CPI pressure"
          icon={Flame}
          isPercentage={false}
          status="negative"
        />
        <MetricCard
          title="Mean Ingest Impact Score"
          value="73.6%"
          change={-2.1}
          trend="down"
          subtitle="Average signal significance"
          icon={MessageSquare}
          isPercentage={false}
          status="neutral"
        />
      </div>

      {/* Category selector pill list */}
      <div className="flex flex-wrap gap-2 pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4.5 py-2 rounded-xl text-xs font-semibold transition-all border ${
              selectedCategory === cat 
                ? 'bg-cyan-500 text-slate-950 border-cyan-500 shadow-md shadow-cyan-500/10' 
                : 'bg-slate-900/40 border-slate-800/40 text-slate-400 hover:text-white hover:bg-slate-900/80'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Headline listing grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main News feed list */}
        <Card className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center pb-4 border-b border-slate-900">
            <h3 className="text-base font-bold font-display text-white">Parsed Economics News Stream</h3>
            <span className="text-[10px] text-slate-500 font-semibold">{filteredHeadlines.length} articles filtered</span>
          </div>

          <div className="space-y-4">
            {filteredHeadlines.length > 0 ? (
              filteredHeadlines.map((item) => (
                <div 
                  key={item.id} 
                  className="p-5 rounded-2xl bg-slate-950/45 border border-slate-900 hover:border-slate-800 transition-all hover:bg-slate-900/10 flex justify-between gap-6 items-start"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        item.sentiment === 'Bullish' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                        item.sentiment === 'Bearish' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                        'bg-slate-500/10 text-slate-400 border border-slate-800'
                      }`}>
                        {item.sentiment}
                      </span>
                      <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">{item.category}</span>
                    </div>

                    <h4 className="text-sm font-bold text-white leading-relaxed">{item.headline}</h4>
                    
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span>Source: <strong className="text-slate-400">{item.source}</strong></span>
                      <span>&bull;</span>
                      <span>{item.time}</span>
                    </div>
                  </div>

                  <div className="text-right flex flex-col justify-center items-end min-w-[70px]">
                    <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block">Impact</span>
                    <span className="text-base font-black text-cyan-400 mt-0.5 block">{item.impactScore}%</span>
                    <span className="text-[9px] text-slate-500 mt-1 block">Weight: High</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-10 text-slate-500 text-xs">
                No economic reports match your filters.
              </div>
            )}
          </div>
        </Card>

        {/* NLP Parsing configuration summary */}
        <Card className="lg:col-span-1 h-fit">
          <h3 className="text-base font-bold font-display text-white mb-4">NLP Sentiment Parser Specs</h3>
          <p className="text-xs text-slate-500 mb-6">Configuration variables driving news impact mapping.</p>
          
          <div className="space-y-5">
            <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-900">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active ML Classifier</span>
              <p className="text-xs font-bold text-white mt-1">RoBERTa Economic-Sentiment-v2</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-900">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Aggregate Ingestion Rate</span>
              <p className="text-xs font-bold text-white mt-1">45 articles / hour (Reuters + Bloomberg Ingests)</p>
            </div>

            <div>
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate-400">Neutral Threshold Weight</span>
                <span className="text-cyan-400">0.35</span>
              </div>
              <input type="range" min="10" max="90" defaultValue="35" className="w-full h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
            </div>

            <div>
              <div className="flex justify-between items-center text-xs font-semibold mb-2">
                <span className="text-slate-400">Alert Notification Severity</span>
                <span className="text-cyan-400">&gt; 80% Impact</span>
              </div>
              <input type="range" min="50" max="95" defaultValue="80" className="w-full h-1 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
