import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Play, BarChart3, BookOpen } from 'lucide-react';
import { Topic } from '../types';
import { apiService } from '../services/api';

const Dashboard: React.FC = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalTopics: 0,
    avgSuccessRate: 0,
    topicsNeverSeen: 0,
    recentlyAdded: 0,
  });

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const topicsData = await apiService.getTopics();
      setTopics(topicsData);
      
      // Calculate dashboard stats
      const totalTopics = topicsData.length;
      const avgSuccessRate = totalTopics > 0 
        ? Math.round(topicsData.reduce((sum, topic) => {
            const attempts = topic.attempts || 0;
            const successes = topic.successes || 0;
            const rate = attempts > 0 ? (successes / attempts * 100) : 0;
            return sum + rate;
          }, 0) / totalTopics)
        : 0;
      const topicsNeverSeen = topicsData.filter(topic => !topic.last_seen).length;
      const recentlyAdded = topicsData.filter(topic => {
        const addedDate = new Date(topic.date_added);
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return addedDate > weekAgo;
      }).length;
      
      setStats({
        totalTopics,
        avgSuccessRate: Math.round(avgSuccessRate),
        topicsNeverSeen,
        recentlyAdded,
      });
    } catch (error) {
      console.error('Error fetching topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return 'text-green-400';
    if (rate >= 60) return 'text-yellow-400';
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold gradient-text mb-4">
          Welcome to garudaco.
        </h1>
        <p className="text-gray-300 text-lg">
          Your intelligent learning assessment companion
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-6 text-center">
          <BookOpen className="w-8 h-8 text-blue-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.totalTopics}</div>
          <div className="text-gray-300">Total Topics</div>
        </div>
        <div className="glass-card p-6 text-center">
          <BarChart3 className="w-8 h-8 text-green-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.avgSuccessRate}%</div>
          <div className="text-gray-300">Avg Success Rate</div>
        </div>
        <div className="glass-card p-6 text-center">
          <Play className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.topicsNeverSeen}</div>
          <div className="text-gray-300">Never Assessed</div>
        </div>
        <div className="glass-card p-6 text-center">
          <Plus className="w-8 h-8 text-purple-400 mx-auto mb-2" />
          <div className="text-2xl font-bold text-white">{stats.recentlyAdded}</div>
          <div className="text-gray-300">Added This Week</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/add-topic" className="glass-card p-6 hover:bg-white/10 transition-all duration-200 group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <Plus className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Add New Topic</h3>
              <p className="text-gray-300">Add a topic you've learned</p>
            </div>
          </div>
        </Link>

        <Link to="/assessment" className="glass-card p-6 hover:bg-white/10 transition-all duration-200 group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <Play className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Start Assessment</h3>
              <p className="text-gray-300">Test your knowledge</p>
            </div>
          </div>
        </Link>

        <Link to="/stats" className="glass-card p-6 hover:bg-white/10 transition-all duration-200 group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">View Statistics</h3>
              <p className="text-gray-300">Track your progress</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Topics */}
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Your Topics</h2>
        {topics.length === 0 ? (
          <div className="text-center py-8">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-300">No topics added yet</p>
            <Link to="/add-topic" className="btn-primary mt-4 inline-block">
              Add Your First Topic
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topics.slice(0, 6).map((topic) => (
              <div key={topic.id} className="glass-card-dark p-4 hover:bg-white/5 transition-all duration-200">
                <div className="flex items-start justify-between mb-6 h-12">
                  <h3 className="font-semibold text-white m-auto">{topic.name}</h3>
                  <span className={`px-2 w-16 ml-2 flex justify-center items-center rounded-lg text-xs font-medium leading-tight text-white ${getCategoryColor(topic.category)}`}>
                    {topic.category}
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Success Rate:</span>
                    <span className={getSuccessRateColor(topic.success_rate)}>
                      {topic.success_rate}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Attempts:</span>
                    <span className="text-white">{topic.attempts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Difficulty:</span>
                    <span className="text-white">{Math.round(topic.base_score)}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Last Seen:</span>
                    <span className="text-white">
                      {topic.last_seen_formatted === 'Never' ? 'Never' : 
                       topic.last_seen_formatted}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        {topics.length > 6 && (
          <div className="text-center mt-6">
            <Link to="/stats" className="btn-secondary">
              View All Topics
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;