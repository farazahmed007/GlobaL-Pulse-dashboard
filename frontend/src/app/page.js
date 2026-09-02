"use client";

import React, { useEffect, useState, useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Activity, Globe, MessageSquare, AlertCircle } from 'lucide-react';

const COLORS = {
  positive: '#10b981', // emerald-500
  neutral: '#6b7280', // gray-500
  negative: '#ef4444', // red-500
};

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
    // Optional: Refresh every 30 seconds for live feel
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
    // Sort by count descending and take top 10
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [data]);

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
                Global Pulse
              </span>
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
        
        {/* Header Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-xl">
              <MessageSquare className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-gray-400 text-sm font-medium">Total Articles Processed</p>
              <h3 className="text-3xl font-bold text-white">{data.length}</h3>
            </div>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-xl">
              <Activity className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <p className="text-gray-400 text-sm font-medium">Positive Sentiments</p>
              <h3 className="text-3xl font-bold text-white">
                {sentimentData.find(d => d.name === 'Positive')?.value || 0}
              </h3>
            </div>
          </div>
          <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 flex items-center gap-4">
            <div className="p-3 bg-red-500/10 rounded-xl">
              <AlertCircle className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <p className="text-gray-400 text-sm font-medium">Negative Sentiments</p>
              <h3 className="text-3xl font-bold text-white">
                {sentimentData.find(d => d.name === 'Negative')?.value || 0}
              </h3>
            </div>
          </div>
        </div>

        {data.length === 0 ? (
          <div className="bg-gray-900/30 border border-gray-800 border-dashed rounded-2xl p-12 text-center flex flex-col items-center justify-center">
            <Globe className="w-16 h-16 text-gray-700 mb-4" />
            <h3 className="text-xl font-semibold text-gray-300">No Data Available</h3>
            <p className="text-gray-500 mt-2 max-w-md">
              The database is currently empty. Run the sentiment pipeline to populate the dashboard with global intelligence data.
            </p>
          </div>
        ) : (
          <>
            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Sentiment Donut Chart */}
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
                      <Tooltip 
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

              {/* Country Distribution Bar Chart */}
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
                      <Tooltip 
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
              <div className="p-6 border-b border-gray-800">
                <h3 className="text-lg font-semibold text-gray-200">Recent Intelligence Feed</h3>
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
          </>
        )}
      </main>
    </div>
  );
}
