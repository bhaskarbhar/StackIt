import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { 
  MessageSquare, 
  Eye, 
  ThumbsUp, 
  Tag, 
  CheckCircle,
  Edit,
  Trash2,
  ArrowLeft
} from 'lucide-react';
import api from '../lib/api';
import { formatDate } from '../lib/utils';
import toast from 'react-hot-toast';

export default function QuestionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [question, setQuestion] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newAnswer, setNewAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState({ id: null, type: null });

  useEffect(() => {
    fetchQuestionAndAnswers();
  }, [id]);

  const fetchQuestionAndAnswers = async () => {
    try {
      setLoading(true);
      const [questionRes, answersRes] = await Promise.all([
        api.get(`/questions/${id}`),
        api.get(`/answers/question/${id}`)
      ]);
      setQuestion(questionRes.data);
      setAnswers(answersRes.data);
    } catch (error) {
      toast.error('Failed to load question');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (itemId, itemType, voteType) => {
    try {
      const endpoint = itemType === 'question' 
        ? `/questions/${itemId}/vote?vote_type=${voteType}`
        : `/answers/${itemId}/vote?vote_type=${voteType}`;
      
      await api.post(endpoint);
      fetchQuestionAndAnswers(); // Refresh data
    } catch (error) {
      toast.error('Failed to vote');
    }
  };

  const handleSubmitAnswer = async () => {
    if (!newAnswer.trim()) {
      toast.error('Please enter an answer');
      return;
    }

    setSubmitting(true);
    try {
      const response = await api.post('/answers/', {
        content: newAnswer
      }, {
        params: { question_id: id }
      });
      setNewAnswer('');
      fetchQuestionAndAnswers();
      toast.success('Answer posted successfully!');
    } catch (error) {
      console.error('Post answer error:', error);
      toast.error('Failed to post answer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = (itemId, itemType) => {
    setDeleteTarget({ id: itemId, type: itemType });
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    const { id: itemId, type: itemType } = deleteTarget;
    setShowDeleteModal(false);
    try {
      const endpoint = itemType === 'question'
        ? `/questions/${itemId}`
        : `/answers/${itemId}`;
      await api.delete(endpoint);
      toast.success(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully!`);
      if (itemType === 'question') {
        navigate('/');
      } else {
        fetchQuestionAndAnswers();
      }
    } catch (error) {
      toast.error(`Failed to delete ${itemType}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Question not found.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
          <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-sm">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Confirm Deletion</h2>
            <p className="mb-6 text-gray-700">Are you sure you want to delete this {deleteTarget.type}? This action cannot be undone.</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="btn btn-outline"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="btn btn-danger"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Questions</span>
      </button>

      {/* Question */}
      <div className="card p-6">
        <div className="flex space-x-4">
          {/* Vote Stats */}
          <div className="flex flex-col items-center space-y-2">
            <button
              onClick={() => handleVote(question.id, 'question', 'upvote')}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
            >
              <ThumbsUp className="w-5 h-5 text-gray-400" />
            </button>
            <span className="text-lg font-semibold text-gray-900">
              {question.votes}
            </span>
            <button
              onClick={() => handleVote(question.id, 'question', 'downvote')}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
            >
              <ThumbsUp className="w-5 h-5 text-gray-400 rotate-180" />
            </button>
          </div>

          {/* Question Content */}
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">
                {question.title}
              </h1>
              
              {user && user.id === question.author_id && (
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigate(`/question/${question.id}/edit`)}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                </div>
              )}
              {user && (user.role === 'admin' || user.id === question.author_id) && (
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleDelete(question.id, 'question')}
                    className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>

            <div 
              className="prose max-w-none mb-4"
              dangerouslySetInnerHTML={{ __html: question.description }}
            />

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
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
            <div className="flex items-center space-x-4 text-sm text-gray-500">
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
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Answered
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Answers */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">
          {answers.length} Answer{answers.length !== 1 ? 's' : ''}
        </h2>

        {answers.map((answer) => (
          <div key={answer.id} className="card p-6">
            <div className="flex space-x-4">
              {/* Vote Stats */}
              <div className="flex flex-col items-center space-y-2">
                <button
                  onClick={() => handleVote(answer.id, 'answer', 'upvote')}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <ThumbsUp className="w-5 h-5 text-gray-400" />
                </button>
                <span className="text-lg font-semibold text-gray-900">
                  {answer.votes}
                </span>
                <button
                  onClick={() => handleVote(answer.id, 'answer', 'downvote')}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <ThumbsUp className="w-5 h-5 text-gray-400 rotate-180" />
                </button>
              </div>

              {/* Answer Content */}
              <div className="flex-1">
                <div className="flex items-start justify-between mb-4">
                  <div 
                    className="prose max-w-none"
                    dangerouslySetInnerHTML={{ __html: answer.content }}
                  />
                  
                  {user && answer.author_id === user.id && (
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => navigate(`/answer/${answer.id}/edit`)}
                        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                  {user && (user.role === 'admin' || answer.author_id === user.id) && (
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleDelete(answer.id, 'answer')}
                        className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>

                {/* Answer Meta */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Answered by {answer.author_username}</span>
                    <span>{formatDate(answer.created_at)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Post Answer */}
      {user ? (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Your Answer
          </h3>
          <div className="space-y-4">
            <div className="border border-gray-300 rounded-lg">
              <ReactQuill
                value={newAnswer}
                onChange={setNewAnswer}
                placeholder="Write your answer..."
                modules={{
                  toolbar: [
                    [{ 'header': [1, 2, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    ['link', 'image'],
                    ['clean']
                  ],
                }}
                className="min-h-[200px]"
              />
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleSubmitAnswer}
                disabled={submitting || !newAnswer.trim()}
                className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Posting...' : 'Post Answer'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="card p-6 text-center">
          <p className="text-gray-600 mb-4">
            Please sign in to post an answer.
          </p>
          <button
            onClick={() => navigate('/login')}
            className="btn btn-primary"
          >
            Sign In
          </button>
        </div>
      )}
    </div>
  );
} 