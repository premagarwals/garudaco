import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Target, BookOpen, Award } from 'lucide-react';
import { Topic, Stats as StatsType } from '../types';
import { apiService } from '../services/api';

const Stats: React.FC = () => {
  const [stats, setStats] = useState<StatsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'success_rate' | 'base_score' | 'attempts' | 'last_seen'>('success_rate');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const statsData = await apiService.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const sortTopics = (topics: Topic[]): Topic[] => {
    return [...topics].sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      switch (sortBy) {
        case 'success_rate':
          aValue = a.success_rate;
          bValue = b.success_rate;
          break;
        case 'base_score':
          aValue = a.base_score;
          bValue = b.base_score;
          break;
        case 'attempts':
          aValue = a.attempts;
          bValue = b.attempts;
          break;
        case 'last_seen':
          aValue = a.last_seen || '1970-01-01';
          bValue = b.last_seen || '1970-01-01';
          break;
        default:
          return 0;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'desc' ? bValue.localeCompare(aValue) : aValue.localeCompare(bValue);
      }

      return sortOrder === 'desc' ? (bValue as number) - (aValue as number) : (aValue as number) - (bValue as number);
    });
  };

  const filterTopics = (topics: Topic[]): Topic[] => {
    if (filterCategory === 'all') return topics;
    return topics.filter(topic => topic.category === filterCategory);
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return 'text-green-400';
    if (rate >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getDifficultyColor = (score: number) => {
    if (score <= 30) return 'text-green-400';
    if (score <= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      arrays: 'bg-blue-500',
      graphs: 'bg-green-500',
      dp: 'bg-purple-500',
      strings: 'bg-pink-500',
      trees: 'bg-yellow-500',
      default: 'bg-gray-500',
    };
    return colors[category as keyof typeof colors] || colors.default;
  };

  const getPerformanceIcon = (successRate: number) => {
    if (successRate >= 90) return '🏆';
    if (successRate >= 80) return '🥇';
    if (successRate >= 70) return '🥈';
    if (successRate >= 60) return '🥉';
    return '📚';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-300">Failed to load statistics</p>
      </div>
    );
  }

  const categories = Object.keys(stats.categories);
  const filteredAndSortedTopics = sortTopics(filterTopics(stats.topics));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold gradient-text mb-2">Statistics & Progress</h1>
        <p className="text-gray-300">Track your learning journey and performance</p>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-6 text-center">
          <BookOpen className="w-8 h-8 text-blue-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.overall.total_topics}</div>
          <div className="text-gray-300">Total Topics</div>
        </div>
        <div className="glass-card p-6 text-center">
          <Target className="w-8 h-8 text-green-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.overall.success_rate}%</div>
          <div className="text-gray-300">Overall Success Rate</div>
        </div>
        <div className="glass-card p-6 text-center">
          <TrendingUp className="w-8 h-8 text-purple-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.overall.total_attempts}</div>
          <div className="text-gray-300">Total Attempts</div>
        </div>
        <div className="glass-card p-6 text-center">
          <Award className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.overall.total_sets}</div>
          <div className="text-gray-300">Assessments Taken</div>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
          <BarChart3 className="w-6 h-6 mr-2" />
          Category Breakdown
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(stats.categories).map(([category, data]) => (
            <div key={category} className="glass-card-dark p-4">
              <div className="flex items-center justify-between mb-3">
                <span className={`px-3 py-1 rounded-full text-sm text-white ${getCategoryColor(category)}`}>
                  {category}
                </span>
                <span className="text-2xl">{getPerformanceIcon(data.success_rate)}</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">Topics:</span>
                  <span className="text-white font-semibold">{data.count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Success Rate:</span>
                  <span className={getSuccessRateColor(data.success_rate)}>
                    {data.success_rate}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Avg Difficulty:</span>
                  <span className={getDifficultyColor(data.avg_difficulty)}>
                    {data.avg_difficulty}/100
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Attempts:</span>
                  <span className="text-white">{data.attempts}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Topics Table */}
      <div className="glass-card p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <h2 className="text-2xl font-bold text-white mb-4 md:mb-0">Topic Details</h2>
          
          <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-4">
            {/* Category Filter */}
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all" className="bg-gray-800">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category} className="bg-gray-800">
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>

            {/* Sort Options */}
            <select
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field as any);
                setSortOrder(order as any);
              }}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="success_rate-desc" className="bg-gray-800">Success Rate (High to Low)</option>
              <option value="success_rate-asc" className="bg-gray-800">Success Rate (Low to High)</option>
              <option value="base_score-desc" className="bg-gray-800">Difficulty (Hard to Easy)</option>
              <option value="base_score-asc" className="bg-gray-800">Difficulty (Easy to Hard)</option>
              <option value="attempts-desc" className="bg-gray-800">Most Attempted</option>
              <option value="attempts-asc" className="bg-gray-800">Least Attempted</option>
              <option value="last_seen-desc" className="bg-gray-800">Recently Seen</option>
              <option value="last_seen-asc" className="bg-gray-800">Oldest Seen</option>
            </select>
          </div>
        </div>

        {filteredAndSortedTopics.length === 0 ? (
          <div className="text-center py-8">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-300">No topics found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-gray-300 font-semibold">Topic</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-semibold">Category</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-semibold">Success Rate</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-semibold">Difficulty</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-semibold">Attempts</th>
                  <th className="text-center py-3 px-4 text-gray-300 font-semibold">Last Seen</th>
                </tr>
              </thead>
              <tbody>
                {filteredAndSortedTopics.map((topic) => (
                  <tr key={topic.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-2xl">{getPerformanceIcon(topic.success_rate)}</span>
                        <span className="text-white font-medium">{topic.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs text-white ${getCategoryColor(topic.category)}`}>
                        {topic.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`font-semibold ${getSuccessRateColor(topic.success_rate)}`}>
                        {topic.success_rate}%
                      </span>
                      <div className="text-xs text-gray-400">
                        {topic.successes}/{topic.attempts}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={`font-semibold ${getDifficultyColor(topic.base_score)}`}>
                        {Math.round(topic.base_score)}/100
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-white font-semibold">{topic.attempts}</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-gray-300 text-sm">
                        {topic.last_seen_formatted === 'Never' ? 'Never' : 
                         new Date(topic.last_seen_formatted).toLocaleDateString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Performance Insights */}
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Performance Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">🎯 Strengths</h3>
            {(() => {
              const strengths = filteredAndSortedTopics
                .filter(topic => topic.success_rate >= 70 && topic.attempts >= 1)
                .slice(0, 5);
              
              if (strengths.length === 0) {
                return (
                  <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg text-center">
                    <p className="text-blue-300">Complete more assessments to see your strengths!</p>
                    <p className="text-sm text-blue-400 mt-2">Topics with 70%+ success rate will appear here</p>
                  </div>
                );
              }
              
              return strengths.map(topic => (
                <div key={topic.id} className="flex items-center justify-between p-4 bg-green-500/15 border border-green-500/30 rounded-lg">
                  <span className="text-green-300 font-medium">{topic.name}</span>
                  <span className="text-green-400 font-bold">{topic.success_rate}%</span>
                </div>
              ));
            })()}
          </div>
          
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">📚 Areas for Improvement</h3>
            {(() => {
              const improvements = filteredAndSortedTopics
                .filter(topic => topic.success_rate < 70 && topic.attempts >= 1)
                .slice(0, 5);
              
              if (improvements.length === 0) {
                return (
                  <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg text-center">
                    <p className="text-blue-300">Great job! No areas needing improvement yet.</p>
                    <p className="text-sm text-blue-400 mt-2">Keep practicing to maintain your performance</p>
                  </div>
                );
              }
              
              return improvements.map(topic => (
                <div key={topic.id} className="flex items-center justify-between p-4 bg-red-500/15 border border-red-500/30 rounded-lg">
                  <span className="text-red-300 font-medium">{topic.name}</span>
                  <span className="text-red-400 font-bold">{topic.success_rate}%</span>
                </div>
              ));
            })()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Stats;