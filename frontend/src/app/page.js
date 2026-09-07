"use client";

import React, { useEffect, useState, useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Activity, Globe, MessageSquare, AlertCircle, Map as MapIcon, Database, Network, Server, ArrowRight, Download, BarChart2, MinusCircle } from 'lucide-react';
import { ComposableMap, Geographies, Geography, Sphere, Graticule } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';

const COLORS = {
  positive: '#10b981', // emerald-500
  neutral: '#6b7280', // gray-500
  negative: '#ef4444', // red-500
};

// Map TopoJSON URL
const geoUrl = "/features.json";

// Map colors
const colorScale = scaleLinear()
  .domain([-1, 0, 1])
  .range(["#ef4444", "#374151", "#10b981"]);

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [tooltipContent, setTooltipContent] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/sentiment');
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const result = await response.json();
        if (result.success) {
          setData(result.data || []);
        } else {
          throw new Error(result.error || 'Unknown error occurred');
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const sentimentData = useMemo(() => {
    if (!data.length) return [];
    const counts = { positive: 0, neutral: 0, negative: 0 };
    data.forEach(item => {
      if (item.sentiment_label && counts[item.sentiment_label] !== undefined) {
        counts[item.sentiment_label]++;
      }
    });
    return [
      { name: 'Positive', value: counts.positive, fill: COLORS.positive },
      { name: 'Neutral', value: counts.neutral, fill: COLORS.neutral },
      { name: 'Negative', value: counts.negative, fill: COLORS.negative },
    ];
  }, [data]);

  const countryData = useMemo(() => {
    if (!data.length) return [];
    const counts = {};
    data.forEach(item => {
      const country = item.country || 'Unknown';
      counts[country] = (counts[country] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [data]);

  const mapCountryToStandard = (name) => {
    if (!name) return "";
    const lower = name.toLowerCase();
    if (lower === 'usa' || lower === 'us' || lower.includes('united states')) return 'United States of America';
    if (lower === 'uk' || lower.includes('united kingdom')) return 'United Kingdom';
    if (lower === 'eu' || lower === 'europe') return 'France'; // Mocking EU to a central country for demo
    return name;
  };

  const countrySentimentData = useMemo(() => {
    if (!data.length) return {};
    const sums = {};
    const counts = {};
    data.forEach(item => {
      let country = item.country;
      if (country && country !== 'Unknown' && country !== 'Global') {
        country = mapCountryToStandard(country);
        sums[country] = (sums[country] || 0) + item.sentiment_score;
        counts[country] = (counts[country] || 0) + 1;
      }
    });
    const avg = {};
    for (const c in sums) {
      avg[c] = sums[c] / counts[c];
    }
    return avg;
  }, [data]);

  const averageSentiment = useMemo(() => {
    if (!data.length) return 0;
    const total = data.reduce((acc, curr) => acc + (curr.sentiment_score || 0), 0);
    return (total / data.length).toFixed(2);
  }, [data]);

  const handleDownloadCSV = () => {
    if (!data || !data.length) return;
    
    const headers = ['Title', 'Country', 'Sentiment Score', 'Sentiment Label', 'Entities'];
    
    const csvContent = [
      headers.join(','),
      ...data.map(row => {
        return [
          `"${(row.title || '').replace(/"/g, '""')}"`,
          `"${row.country || 'Global'}"`,
          row.sentiment_score || 0,
          `"${row.sentiment_label || 'neutral'}"`,
          `"${(row.entities || []).join('; ')}"`
        ].join(',');
      })
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'global_pulse_data.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
          <p className="text-gray-400 font-medium">Loading Global Pulse Data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-6">
        <div className="bg-red-950/30 border border-red-500/50 rounded-xl p-6 max-w-md w-full flex flex-col items-center text-center gap-4">
          <AlertCircle className="w-12 h-12 text-red-500" />
          <h2 className="text-xl font-bold text-red-400">Connection Error</h2>
          <p className="text-red-300/80">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans selection:bg-emerald-500/30">
      {/* Navigation Bar */}
      <nav className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Globe className="w-8 h-8 text-emerald-500" />
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400">
                Semantic Analysis
              </span>
            </div>
            
            {/* Tabs */}
            <div className="flex items-center gap-2 bg-gray-950 p-1 rounded-lg border border-gray-800">
              {['Dashboard', 'Global Map', 'ELT Pipeline'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
                    activeTab === tab 
                      ? 'bg-gray-800 text-white shadow-sm' 
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900'
                  }`}
                >
                  {tab === 'Dashboard' && <Activity className="w-4 h-4 inline-block mr-2 -mt-0.5" />}
                  {tab === 'Global Map' && <MapIcon className="w-4 h-4 inline-block mr-2 -mt-0.5" />}
                  {tab === 'ELT Pipeline' && <Network className="w-4 h-4 inline-block mr-2 -mt-0.5" />}
                  {tab}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                Live Updates
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {data.length === 0 ? (
          <div className="bg-gray-900/30 border border-gray-800 border-dashed rounded-2xl p-12 text-center flex flex-col items-center justify-center mt-12">
            <Globe className="w-16 h-16 text-gray-700 mb-4" />
            <h3 className="text-xl font-semibold text-gray-300">No Data Available</h3>
            <p className="text-gray-500 mt-2 max-w-md">
              The database is currently empty. Run the sentiment pipeline to populate the dashboard with global intelligence data.
            </p>
          </div>
        ) : (
          <>
            {/* Dashboard Tab Content */}
            {activeTab === 'Dashboard' && (
              <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* Header Stats */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-4 xl:p-6 flex items-center gap-4">
                    <div className="p-3 bg-blue-500/10 rounded-xl shrink-0">
                      <MessageSquare className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs xl:text-sm font-medium">Total Articles</p>
                      <h3 className="text-2xl xl:text-3xl font-bold text-white">{data.length}</h3>
                    </div>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-4 xl:p-6 flex items-center gap-4">
                    <div className="p-3 bg-purple-500/10 rounded-xl shrink-0">
                      <BarChart2 className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs xl:text-sm font-medium">Avg Sentiment</p>
                      <h3 className="text-2xl xl:text-3xl font-bold text-white">{averageSentiment}</h3>
                    </div>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-4 xl:p-6 flex items-center gap-4">
                    <div className="p-3 bg-emerald-500/10 rounded-xl shrink-0">
                      <Activity className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs xl:text-sm font-medium">Positive</p>
                      <h3 className="text-2xl xl:text-3xl font-bold text-white">
                        {sentimentData.find(d => d.name === 'Positive')?.value || 0}
                      </h3>
                    </div>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-4 xl:p-6 flex items-center gap-4">
                    <div className="p-3 bg-gray-500/10 rounded-xl shrink-0">
                      <MinusCircle className="w-6 h-6 text-gray-400" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs xl:text-sm font-medium">Neutral</p>
                      <h3 className="text-2xl xl:text-3xl font-bold text-white">
                        {sentimentData.find(d => d.name === 'Neutral')?.value || 0}
                      </h3>
                    </div>
                  </div>
                  <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-4 xl:p-6 flex items-center gap-4">
                    <div className="p-3 bg-red-500/10 rounded-xl shrink-0">
                      <AlertCircle className="w-6 h-6 text-red-400" />
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs xl:text-sm font-medium">Negative</p>
                      <h3 className="text-2xl xl:text-3xl font-bold text-white">
                        {sentimentData.find(d => d.name === 'Negative')?.value || 0}
                      </h3>
                    </div>
                  </div>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-gray-200 mb-6">Global Sentiment Breakdown</h3>
                    <div className="h-72 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sentimentData}
                            innerRadius={80}
                            outerRadius={110}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {sentimentData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                          </Pie>
                          <RechartsTooltip 
                            contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '0.75rem', color: '#f3f4f6' }}
                            itemStyle={{ color: '#f3f4f6' }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="flex justify-center gap-6 mt-4">
                      {sentimentData.map((entry) => (
                        <div key={entry.name} className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.fill }} />
                          <span className="text-sm text-gray-400">{entry.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-gray-200 mb-6">Top Mentions by Country</h3>
                    <div className="h-72 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={countryData}
                          layout="vertical"
                          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#374151" />
                          <XAxis type="number" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                          <YAxis dataKey="name" type="category" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                          <RechartsTooltip 
                            cursor={{ fill: '#1f2937' }}
                            contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '0.75rem', color: '#f3f4f6' }}
                          />
                          <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                {/* Data Table */}
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl overflow-hidden">
                  <div className="p-6 border-b border-gray-800 flex justify-between items-center flex-wrap gap-4">
                    <h3 className="text-lg font-semibold text-gray-200">Recent Intelligence Feed</h3>
                    <button 
                      onClick={handleDownloadCSV}
                      className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg text-sm font-medium transition-colors border border-gray-700"
                    >
                      <Download className="w-4 h-4" />
                      Export CSV
                    </button>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-gray-800/50 border-b border-gray-800 text-gray-400 text-sm uppercase tracking-wider">
                          <th className="px-6 py-4 font-medium">Article Title</th>
                          <th className="px-6 py-4 font-medium">Country</th>
                          <th className="px-6 py-4 font-medium">Sentiment Score</th>
                          <th className="px-6 py-4 font-medium">Entities Extracted</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-800/50">
                        {data.slice(0, 50).map((row, index) => (
                          <tr key={index} className="hover:bg-gray-800/30 transition-colors">
                            <td className="px-6 py-4">
                              <p className="text-gray-200 font-medium line-clamp-2">{row.title}</p>
                            </td>
                            <td className="px-6 py-4">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-800 text-gray-300 border border-gray-700">
                                {row.country || 'Global'}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-2">
                                <div 
                                  className={`w-2 h-2 rounded-full ${
                                    row.sentiment_label === 'positive' ? 'bg-emerald-500' :
                                    row.sentiment_label === 'negative' ? 'bg-red-500' : 'bg-gray-500'
                                  }`} 
                                />
                                <span className="text-gray-300 tabular-nums">
                                  {typeof row.sentiment_score === 'number' ? row.sentiment_score.toFixed(2) : 'N/A'}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex flex-wrap gap-2">
                                {(row.entities || []).slice(0, 3).map((entity, i) => (
                                  <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                    {entity}
                                  </span>
                                ))}
                                {(row.entities || []).length > 3 && (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-800 text-gray-400 border border-gray-700">
                                    +{(row.entities || []).length - 3}
                                  </span>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* Global Map Tab Content */}
            {activeTab === 'Global Map' && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-gray-200">Global Sentiment Heatmap</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-red-500"></div> Negative
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-gray-500"></div> Neutral
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-emerald-500"></div> Positive
                      </div>
                    </div>
                  </div>
                  
                  <div className="w-full bg-[#111827] rounded-xl overflow-hidden relative" style={{ height: '600px' }}>
                    {tooltipContent && (
                      <div className="absolute top-4 left-4 z-10 bg-gray-900 border border-gray-700 p-3 rounded-lg shadow-xl text-white">
                        {tooltipContent}
                      </div>
                    )}
                    <ComposableMap 
                      projectionConfig={{ scale: 155 }}
                      style={{ width: "100%", height: "100%" }}
                    >
                      <Sphere stroke="#1f2937" strokeWidth={0.5} />
                      <Graticule stroke="#1f2937" strokeWidth={0.5} />
                      <Geographies geography={geoUrl}>
                        {({ geographies }) =>
                          geographies.map((geo) => {
                            const countryName = geo.properties.name;
                            // Check exact matches or simple heuristics
                            const matchedKey = Object.keys(countrySentimentData).find(
                              key => countryName.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(countryName.toLowerCase())
                            );
                            const avgSentiment = matchedKey !== undefined ? countrySentimentData[matchedKey] : null;
                            
                            return (
                              <Geography
                                key={geo.rsmKey}
                                geography={geo}
                                onMouseEnter={() => {
                                  if (avgSentiment !== null) {
                                    setTooltipContent(`${countryName}: ${avgSentiment > 0 ? '+' : ''}${avgSentiment.toFixed(2)}`);
                                  } else {
                                    setTooltipContent(`${countryName}: No data`);
                                  }
                                }}
                                onMouseLeave={() => {
                                  setTooltipContent("");
                                }}
                                style={{
                                  default: {
                                    fill: avgSentiment !== null ? colorScale(avgSentiment) : "#1f2937",
                                    outline: "none",
                                    stroke: "#374151",
                                    strokeWidth: 0.5,
                                    transition: "all 250ms"
                                  },
                                  hover: {
                                    fill: avgSentiment !== null ? "#3b82f6" : "#4b5563",
                                    outline: "none",
                                    cursor: "pointer",
                                    stroke: "#9ca3af",
                                    strokeWidth: 1
                                  },
                                  pressed: {
                                    fill: "#2563eb",
                                    outline: "none"
                                  }
                                }}
                              />
                            );
                          })
                        }
                      </Geographies>
                    </ComposableMap>
                  </div>
                </div>
              </div>
            )}

            {/* ELT Pipeline Tab Content */}
            {activeTab === 'ELT Pipeline' && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8">
                  <h2 className="text-2xl font-bold text-white mb-2">Under the Hood: ELT Architecture</h2>
                  <p className="text-gray-400 mb-10 max-w-2xl">
                    Global Pulse leverages a modern Extract, Load, Transform (ELT) architecture running in isolated Docker containers to guarantee robust data ingestion and presentation.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
                    {/* Connecting line for desktop */}
                    <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gray-800 -z-10 transform -translate-y-1/2"></div>

                    {/* Step 1: Extract */}
                    <div className="bg-gray-950 border border-gray-800 rounded-xl p-6 shadow-xl relative group hover:border-emerald-500/50 transition-colors">
                      <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6 mx-auto">
                        <Globe className="w-6 h-6 text-emerald-400" />
                      </div>
                      <h3 className="text-xl font-bold text-white text-center mb-3">1. Extract</h3>
                      <p className="text-sm text-gray-400 text-center leading-relaxed">
                        The <code>pulse_pipeline_worker</code> continuously queries the NewsAPI for the latest global headlines. It features automatic defensive fallbacks to synthetic data if keys are missing or invalid.
                      </p>
                      <div className="mt-4 flex justify-center">
                        <span className="text-xs font-mono px-2 py-1 bg-gray-900 rounded text-gray-500">Python 3.12 / requests</span>
                      </div>
                    </div>

                    {/* Step 2: Transform */}
                    <div className="bg-gray-950 border border-gray-800 rounded-xl p-6 shadow-xl relative group hover:border-blue-500/50 transition-colors">
                      <div className="w-12 h-12 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-6 mx-auto">
                        <Server className="w-6 h-6 text-blue-400" />
                      </div>
                      <h3 className="text-xl font-bold text-white text-center mb-3">2. Transform</h3>
                      <p className="text-sm text-gray-400 text-center leading-relaxed">
                        Unstructured text is processed by an Agentic LLM (Gemini via OpenAI compat layer). A strict JSON schema is enforced to extract sentiment, numeric scores, and geopolitical entities.
                      </p>
                      <div className="mt-4 flex justify-center">
                        <span className="text-xs font-mono px-2 py-1 bg-gray-900 rounded text-gray-500">LLM JSON Mode</span>
                      </div>
                    </div>

                    {/* Step 3: Load */}
                    <div className="bg-gray-950 border border-gray-800 rounded-xl p-6 shadow-xl relative group hover:border-purple-500/50 transition-colors">
                      <div className="w-12 h-12 rounded-full bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-6 mx-auto">
                        <Database className="w-6 h-6 text-purple-400" />
                      </div>
                      <h3 className="text-xl font-bold text-white text-center mb-3">3. Load</h3>
                      <p className="text-sm text-gray-400 text-center leading-relaxed">
                        Structured insights are loaded into a persistent <code>pulse_mongodb</code> volume. The Next.js dashboard securely queries this data over the isolated internal Docker network to serve the UI.
                      </p>
                      <div className="mt-4 flex justify-center">
                        <span className="text-xs font-mono px-2 py-1 bg-gray-900 rounded text-gray-500">MongoDB / Next.js API</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-12 p-4 bg-blue-900/10 border border-blue-500/20 rounded-lg flex items-start gap-4">
                    <div className="mt-0.5">
                      <MapIcon className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-blue-100">Robust Orchestration</h4>
                      <p className="text-sm text-blue-200/70 mt-1">
                        If a single service fails, Docker Compose ensures it restarts automatically (`unless-stopped`). The database volume securely isolates state from compute, meaning UI components never directly execute heavy processing tasks.
                      </p>
                    </div>
                  </div>

                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
