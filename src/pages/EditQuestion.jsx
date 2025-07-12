import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { Tag, AlertCircle } from 'lucide-react';
import api from '../lib/api';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

export default function EditQuestion() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [description, setDescription] = useState('');
  const [question, setQuestion] = useState(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm();

  useEffect(() => {
    fetchQuestion();
    // eslint-disable-next-line
  }, [id]);

  const fetchQuestion = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/questions/${id}`);
      setQuestion(res.data);
      setValue('title', res.data.title);
      setDescription(res.data.description);
      setTags(res.data.tags);
      setLoading(false);
      // Only author or admin can edit
      if (!user || (user.id !== res.data.author_id && user.role !== 'admin')) {
        toast.error('Not authorized to edit this question');
        navigate(`/question/${id}`);
      }
    } catch (error) {
      toast.error('Failed to load question');
      navigate('/');
    }
  };

  const handleTagInput = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const tag = tagInput.trim().toLowerCase();
      if (tag && !tags.includes(tag) && tags.length < 5) {
        setTags([...tags, tag]);
        setTagInput('');
      }
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const onSubmit = async (data) => {
    if (tags.length === 0) {
      toast.error('Please add at least one tag');
      return;
    }
    if (description.trim().length < 20) {
      toast.error('Description must be at least 20 characters long');
      return;
    }
    try {
      setLoading(true);
      const updateData = {
        title: data.title,
        description: description,
        tags: tags,
      };
      await api.put(`/questions/${id}`, updateData);
      toast.success('Question updated successfully!');
      navigate(`/question/${id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update question');
    } finally {
      setLoading(false);
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
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Edit Question</h1>
        <p className="mt-2 text-gray-600">
          Update your question details below
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title *
          </label>
          <input
            type="text"
            {...register('title', {
              required: 'Title is required',
              minLength: {
                value: 10,
                message: 'Title must be at least 10 characters long',
              },
              maxLength: {
                value: 300,
                message: 'Title must be less than 300 characters',
              },
            })}
            placeholder="What's your question? Be specific."
            className="input"
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.title.message}
            </p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <div className="border border-gray-300 rounded-lg">
            <ReactQuill
              value={description}
              onChange={setDescription}
              placeholder="Provide details about your question..."
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
          {description.trim().length > 0 && description.trim().length < 20 && (
            <p className="mt-1 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              Description must be at least 20 characters long
            </p>
          )}
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags * (1-5 tags)
          </label>
          <div className="space-y-3">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagInput}
              placeholder="Type tags and press Enter or comma (e.g., react, javascript)"
              className="input"
            />
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                  >
                    <Tag className="w-3 h-4 mr-1" />
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-2 text-primary-600 hover:text-primary-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
            {tags.length === 0 && (
              <p className="text-sm text-gray-500">
                Add at least one tag to help others find your question
              </p>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate(`/question/${id}`)}
            className="btn btn-outline"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || tags.length === 0 || description.trim().length < 20}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
} 