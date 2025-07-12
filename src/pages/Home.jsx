import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MessageSquare, Eye, ThumbsUp, Tag, Plus, Search } from 'lucide-react';
import api from '../lib/api';
import { formatDate, truncateText } from '../lib/utils';
import { useAuth } from '../contexts/AuthContext';
import { fetchAdminStats } from '../lib/api';

export default function Home() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('newest');
  const [searchTerm, setSearchTerm] = useState('');
  // Admin stats state
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState(null);

  useEffect(() => {
    fetchQuestions();
  }, [filter]);

  useEffect(() => {
    if (user && user.role === 'admin') {
      fetchStats();
    }
  }, [user]);

  const fetchStats = async () => {
    setStatsLoading(true);
    setStatsError(null);
    try {
      const res = await fetchAdminStats();
      setStats(res.data);
    } catch (err) {
      setStatsError('Failed to load statistics');
    } finally {
      setStatsLoading(false);
    }
  };

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: 20,
      });

      // Set sort parameters based on filter
      switch (filter) {
        case 'newest':
          params.append('sort_by', 'created_at');
          params.append('sort_order', 'desc');
          break;
        case 'popular':
          params.append('sort_by', 'votes');
          params.append('sort_order', 'desc');
          break;
        case 'best':
          params.append('sort_by', 'answers_count');
          params.append('sort_order', 'desc');
          break;
        default:
          params.append('sort_by', 'created_at');
          params.append('sort_order', 'desc');
      }



      const response = await api.get(`/questions/?${params}`);
      setQuestions(response.data);
    } catch (error) {
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (questionId, voteType) => {
    try {
      await api.post(`/questions/${questionId}/vote?vote_type=${voteType}`);
      fetchQuestions(); // Refresh the list
    } catch (error) {
      console.error('Error voting:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Admin Platform Statistics */}
      {user && user.role === 'admin' && (
        <div className="card p-6 bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 mb-4">
          <h2 className="text-2xl font-bold text-blue-900 mb-4 flex items-center">
            Platform Statistics
          </h2>
          {statsLoading ? (
            <div className="text-blue-700">Loading statistics...</div>
          ) : statsError ? (
            <div className="text-red-500">{statsError}</div>
          ) : stats ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              <div className="flex flex-col items-center">
                <span className="text-3xl font-bold text-blue-800">{stats.total_users}</span>
                <span className="text-sm text-blue-700">Total Users</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-3xl font-bold text-blue-800">{stats.total_questions}</span>
                <span className="text-sm text-blue-700">Questions</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-3xl font-bold text-blue-800">{stats.total_answers}</span>
                <span className="text-sm text-blue-700">Answers</span>
              </div>
            </div>
          ) : null}
        </div>
      )}
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Recent Questions</h1>
          <p className="mt-2 text-gray-600">Find answers to your questions or help others</p>
        </div>
        {(!user || user.role !== 'admin') && (
          <Link
            to="/ask"
            className="mt-4 sm:mt-0 btn btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Ask Question</span>
          </Link>
        )}
      </div>

      {/* Search and Filter Bar */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search Bar */}
          <div className="flex-1">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search questions..."
                className="input pr-10"
              />
              <button
                type="submit"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <Search className="w-5 h-5" />
              </button>
            </form>
          </div>

          {/* Filter Options */}
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('newest')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'newest'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Newest
            </button>
            <button
              onClick={() => setFilter('popular')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'popular'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Most Popular
            </button>
            <button
              onClick={() => setFilter('best')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'best'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Best
            </button>
          </div>
        </div>
      </div>

      {/* Questions List */}
      <div className="space-y-4">
        {questions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No questions found.</p>
          </div>
        ) : (
          questions.map((question) => (
            <div key={question.id} className="card p-6">
              <div className="flex space-x-4">
                {/* Vote Stats */}
                <div className="flex flex-col items-center space-y-2">
                  <button
                    onClick={() => handleVote(question.id, 'upvote')}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                  >
                    <ThumbsUp className="w-5 h-5 text-gray-400" />
                  </button>
                  <span className="text-lg font-semibold text-gray-900">
                    {question.votes}
                  </span>
                  <button
                    onClick={() => handleVote(question.id, 'downvote')}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                  >
                    <ThumbsUp className="w-5 h-5 text-gray-400 rotate-180" />
                  </button>
                </div>

                {/* Question Content */}
                <div className="flex-1">
                  <Link
                    to={`/question/${question.id}`}
                    className="block group"
                  >
                    <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {question.title}
                    </h3>
                  </Link>
                  
                  <div
                    className="mt-2 text-gray-600 prose max-w-none"
                    dangerouslySetInnerHTML={{ __html: question.description }}
                  />

                  {/* Tags */}
                  <div className="mt-3 flex flex-wrap gap-2">
                    {question.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                      >
                        <Tag className="w-3 h-3 mr-1" />
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Meta Info */}
                  <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
                    <span>Asked by {question.author_username}</span>
                    <span>{formatDate(question.created_at)}</span>
                    <div className="flex items-center space-x-1">
                      <MessageSquare className="w-4 h-4" />
                      <span>{question.answers_count} answers</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Eye className="w-4 h-4" />
                      <span>{question.views} views</span>
                    </div>
                    {question.is_answered && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Answered
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
} 
