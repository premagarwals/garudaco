import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, BookOpen } from 'lucide-react';
import { apiService } from '../services/api';

const AddTopic: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    difficulty: 50,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const categories = [
    'arrays',
    'graphs',
    'trees',
    'dp',
    'strings',
    'math',
    'greedy',
    'backtracking',
    'sorting',
    'searching',
    'linkedlist',
    'stack',
    'queue',
    'heap',
    'trie',
    'segment-tree',
    'binary-search',
    'two-pointers',
    'sliding-window',
    'hashing',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsSubmitting(true);

    try {
      if (!formData.name.trim() || !formData.category) {
        setError('Please fill in all required fields');
        return;
      }

      const message = await apiService.addTopic(
        formData.name.trim(),
        formData.category,
        formData.difficulty
      );

      setSuccess(message);
      setFormData({ name: '', category: '', difficulty: 50 });
      
      // Navigate back to dashboard after successful submission
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to add topic');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDifficultyColor = (difficulty: number) => {
    if (difficulty <= 30) return 'text-green-400';
    if (difficulty <= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getDifficultyLabel = (difficulty: number) => {
    if (difficulty <= 30) return 'Easy';
    if (difficulty <= 70) return 'Medium';
    return 'Hard';
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <Plus className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold gradient-text mb-2">Add New Topic</h1>
        <p className="text-gray-300">
          Add a topic you've learned to start tracking your progress
        </p>
      </div>

      {/* Form */}
      <div className="glass-card p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Topic Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
              Topic Name *
            </label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Binary Search, DFS, Dynamic Programming..."
              required
            />
          </div>

          {/* Category */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-300 mb-2">
              Category *
            </label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="" className="bg-gray-800">Select a category...</option>
              {categories.map((category) => (
                <option key={category} value={category} className="bg-gray-800">
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty */}
          <div>
            <label htmlFor="difficulty" className="block text-sm font-medium text-gray-300 mb-2">
              Initial Difficulty Assessment: {' '}
              <span className={getDifficultyColor(formData.difficulty)}>
                {formData.difficulty}/100 ({getDifficultyLabel(formData.difficulty)})
              </span>
            </label>
            <input
              type="range"
              id="difficulty"
              min="1"
              max="100"
              value={formData.difficulty}
              onChange={(e) => setFormData({ ...formData, difficulty: parseInt(e.target.value) })}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>Very Easy (1)</span>
              <span>Medium (50)</span>
              <span>Very Hard (100)</span>
            </div>
            <p className="text-sm text-gray-400 mt-2">
              Rate how difficult you think this topic is for you right now
            </p>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg text-red-300">
              {error}
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-lg text-green-300">
              {success}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Adding Topic...</span>
              </>
            ) : (
              <>
                <BookOpen className="w-5 h-5" />
                <span>Add Topic</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Tips */}
      <div className="mt-8 glass-card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">💡 Tips for Adding Topics</h3>
        <ul className="space-y-2 text-gray-300 text-sm">
          <li>• Be specific with topic names (e.g., "Binary Search on Rotated Array" vs "Binary Search")</li>
          <li>• Choose the most appropriate category to help with organization</li>
          <li>• Rate difficulty based on your current understanding, not absolute difficulty</li>
          <li>• You can always add the same algorithm/concept with different variations</li>
          <li>• The system will adjust difficulty based on your performance over time</li>
        </ul>
      </div>
    </div>
  );
};

export default AddTopic;