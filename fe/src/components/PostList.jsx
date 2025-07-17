import axios from "axios";
import { useMemo, useState } from "react";

export default function PostList({ posts, isLoading }) {
  const [expandedPost, setExpandedPost] = useState(null);
  const [wordAnalysis, setWordAnalysis] = useState({});
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  const API_URL = "http://127.0.0.1:8000";

  // Sort posts by total interactions (likes + comments + shares)
  const sortedPosts = useMemo(() => {
    if (!posts) return [];
    return [...posts].sort((a, b) => {
      const totalInteractionsA = (a.likes || 0) + (a.comments || 0) + (a.shares || 0);
      const totalInteractionsB = (b.likes || 0) + (b.comments || 0) + (b.shares || 0);
      return totalInteractionsB - totalInteractionsA;
    });
  }, [posts]);

  const fetchWordAnalysis = async (postId, post) => {
    if (wordAnalysis[postId]) return; // Return if already analyzed
    
    setLoadingAnalysis(true);
    setAnalysisError(null);
    try {
      // Get word analysis
      const wordAnalysisResponse = await axios.post(`${API_URL}/word-analysis`, {
        text: post.text,
        time: post.time,
        likes: post.likes,
        comments: post.comments,
        shares: post.shares,
        url: post.url
      });

      // Get overall sentiment
      const sentimentResponse = await axios.post(`${API_URL}/sentiment`, [{
        text: post.text,
        time: post.time,
        likes: post.likes,
        comments: post.comments,
        shares: post.shares,
        url: post.url
      }]);

      setWordAnalysis(prev => ({
        ...prev,
        [postId]: {
          ...wordAnalysisResponse.data,
          overallSentiment: sentimentResponse.data
        }
      }));
    } catch (err) {
      console.error('Error analyzing text:', err);
      setAnalysisError(err.response?.data?.detail || err.message);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // Handle loading state
  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-10">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-blue-500">Đang tải dữ liệu...</span>
      </div>
    );
  }

  // Handle empty state
  if (!posts || posts.length === 0) {
    return (
      <div className="p-6 bg-yellow-50 rounded-lg text-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-yellow-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p className="text-yellow-700 font-medium">Không tìm thấy bài đăng nào phù hợp với điều kiện tìm kiếm.</p>
        <p className="text-yellow-600 mt-2">Vui lòng thử lại với các bộ lọc khác.</p>
      </div>
    );
  }

  // Format date to Vietnamese format
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  // Function to determine sentiment color
  const getSentimentColor = (text) => {
    const lowerText = text.toLowerCase();
    
    // Simple sentiment detection based on common Vietnamese words
    if (lowerText.includes("tốt") || lowerText.includes("hay") || lowerText.includes("tuyệt vời") || lowerText.includes("cảm ơn")) {
      return "bg-green-50 border-green-200";
    } else if (lowerText.includes("tệ") || lowerText.includes("kém") || lowerText.includes("chán") || lowerText.includes("buồn")) {
      return "bg-red-50 border-red-200";
    }
    
    return "bg-gray-50 border-gray-200";
  };

  // Function to determine topic based on content
  const getTopic = (text) => {
    // Map topic labels to display names
    const topicDisplayNames = {
      "LABEL_0": "Cơ sở vật chất",
      "LABEL_1": "Giảng viên",
      "LABEL_2": "Sinh viên",
      "LABEL_3": "Chương trình đào tạo"
    };

    // Get topic from post data if available
    if (text.topic) {
      return topicDisplayNames[text.topic] || "Khác";
    }
    
    return "Khác";
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-xl font-bold text-gray-800">Danh sách bài đăng</h2>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
          {sortedPosts.length} bài đăng
        </span>
      </div>
      
      <div className="divide-y divide-gray-200">
        {sortedPosts.map((post, index) => {
          const sentimentClass = getSentimentColor(post.text);
          const topic = getTopic(post);
          
          return (
            <div key={index} className={`p-5 hover:bg-blue-50 transition-colors ${sentimentClass}`}>
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center">
                  <span className="text-xs font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-800 mr-2">
                    {topic}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDate(post.time)}
                  </span>
                </div>
              </div>
              
              <p className="text-gray-800 text-base mb-3">
                {post.text}
              </p>
              
              <div className="flex items-center space-x-4">
                
                <a 
                  href={post.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-red-600 hover:text-red-800 flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Xem bài gốc
                </a>
              </div>

              <div className="flex justify-between items-center text-sm">
                <div className="flex space-x-6">
                  <span className="flex items-center text-blue-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                    </svg>
                    {post.likes}
                  </span>
                  <span className="flex items-center text-green-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    {post.comments}
                  </span>
                  <span className="flex items-center text-purple-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                    {post.shares}
                  </span>
                </div>
                
                <button 
                  onClick={() => {
                    if (expandedPost === index) {
                      setExpandedPost(null);
                    } else {
                      setExpandedPost(index);
                      fetchWordAnalysis(index, post);
                    }
                  }}
                  className="text-blue-600 hover:text-blue-800 hover:underline flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  {expandedPost === index ? 'Ẩn phân tích' : 'Phân tích từ ngữ'}
                </button>
              </div>

              {expandedPost === index && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  {loadingAnalysis ? (
                    <div className="flex justify-center items-center py-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                      <span className="ml-3 text-blue-500">Đang phân tích...</span>
                    </div>
                  ) : analysisError ? (
                    <div className="text-red-500 text-center py-4">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Lỗi khi phân tích: {analysisError}
                    </div>
                  ) : wordAnalysis[index] ? (
                    <div className="space-y-4">
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-700 mb-2">Kết quả phân tích cảm xúc:</h4>
                        <div className="flex gap-4">
                          <div className={`flex-1 p-3 rounded-lg border ${
                            wordAnalysis[index].overallSentiment?.positive?.includes(post.text) 
                              ? 'bg-green-50 border-green-200' 
                              : 'bg-gray-50 border-gray-200'
                          }`}>
                            <div className="text-sm text-green-600 mb-1">Tích cực</div>
                            <div className="text-2xl font-bold text-green-700">
                              {wordAnalysis[index].overallSentiment?.positive?.includes(post.text) ? '✓' : '-'}
                            </div>
                          </div>
                          <div className={`flex-1 p-3 rounded-lg border ${
                            wordAnalysis[index].overallSentiment?.negative?.includes(post.text) 
                              ? 'bg-red-50 border-red-200' 
                              : 'bg-gray-50 border-gray-200'
                          }`}>
                            <div className="text-sm text-red-600 mb-1">Tiêu cực</div>
                            <div className="text-2xl font-bold text-red-700">
                              {wordAnalysis[index].overallSentiment?.negative?.includes(post.text) ? '✓' : '-'}
                            </div>
                          </div>
                          <div className={`flex-1 p-3 rounded-lg border ${
                            wordAnalysis[index].overallSentiment?.neutral?.includes(post.text) 
                              ? 'bg-gray-50 border-gray-200' 
                              : 'bg-gray-50 border-gray-200'
                          }`}>
                            <div className="text-sm text-gray-600 mb-1">Trung lập</div>
                            <div className="text-2xl font-bold text-gray-700">
                              {wordAnalysis[index].overallSentiment?.neutral?.includes(post.text) ? '✓' : '-'}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium text-green-700 mb-2">Từ tích cực:</h4>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(wordAnalysis[index].positive).map(([word, data]) => (
                            <span key={word} className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                              {word} ({Math.round(data.confidence * 100)}%)
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-red-700 mb-2">Từ tiêu cực:</h4>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(wordAnalysis[index].negative).map(([word, data]) => (
                            <span key={word} className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-sm">
                              {word} ({Math.round(data.confidence * 100)}%)
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Từ trung lập:</h4>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(wordAnalysis[index].neutral).map(([word, data]) => (
                            <span key={word} className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                              {word} ({Math.round(data.confidence * 100)}%)
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {sortedPosts.length > 10 && (
        <div className="p-4 flex justify-center border-t">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Xem thêm bài đăng
          </button>
        </div>
      )}
    </div>
  );
}