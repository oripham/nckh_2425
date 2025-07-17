import axios from "axios";
import { useEffect, useState } from "react";
import EmotionStats from "./components/EmotionStats";
import Loading from "./components/Loading";
import PostList from "./components/PostList"; // Import the new PostList component

const pages = [
  "UTC2 Confessions",
  "UCT2 Nơi chia sẻ cảm xúc",
  "UTC2 Zone",
  "Diễn đàn nghe sinh viên nói",
];

// Changed from hashtags to topics based on the backend model
const topics = [
  { label: "Cơ sở vật chất", value: "LABEL_0" },
  { label: "Giảng viên", value: "LABEL_1" },
  { label: "Sinh viên", value: "LABEL_2" },
  { label: "Chương trình đào tạo", value: "LABEL_3" },
];

const API_URL = "http://127.0.0.1:8000";

export default function FilterConfession() {
  const [isLoadingOverView, setIsLoadingOverView] = useState(false);
  const [overViewContent, setOverViewContent] = useState("");

  const [isLoadingSentiment, setIsLoadingSentiment] = useState(false);
  const [sentimentContent, setSentimentContent] = useState({
    positive: [],
    negative: [],
    neutral: []
  });

  const [data, setData] = useState([]);
  const [isLoadingData, setIsLoadingData] = useState(false);

  const [selectedPage, setSelectedPage] = useState(0);
  const [selectedTopic, setSelectedTopic] = useState(""); // Changed from selectedTag to selectedTopic
  const [startDate, setStartDate] = useState(undefined);
  const [endDate, setEndDate] = useState(undefined);
  const [error, setError] = useState("");
  
  // New state to control which view is active
  const [activeView, setActiveView] = useState("sentiment"); // "sentiment" or "posts"

  // Function to truncate text to 50 characters
  const truncateText = (text, maxLength = 50) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // Fetch data function
  const fetchData = async () => {
    setIsLoadingData(true);
    setError("");
    try {
      await new Promise((resolve) => setTimeout(resolve, 3000));
      const response = await axios.get(`${API_URL}/posts`, {
        params: {
          page: 1,
          limit: 10,
          selected_page: selectedPage,
          topic: selectedTopic, // Changed from tag to topic
          start_date: startDate,
          end_date: endDate,
        },
      });
      setData(response.data.posts);
    } catch (err) {
      setError("Lỗi kết nối: " + err.message);
    } finally {
      setIsLoadingData(false);
    }
  };

  const shoolOverview = async () => {
    setIsLoadingOverView(true);
    setError("");
    try {
      await new Promise((resolve) => setTimeout(resolve, 3000));
      const response = await axios.post(`${API_URL}/school-summary`, data);
      setOverViewContent(response.data);
    } catch (err) {
      setError("Lỗi kết nối: " + err.message);
    } finally {
      setIsLoadingOverView(false);
    }
  };

  const shoolSentiment = async () => {
    setIsLoadingSentiment(true);
    setError("");
    try {
      const response = await axios.post(`${API_URL}/sentiment`, data);
      if (response.data && typeof response.data === 'object') {
        setSentimentContent(response.data);
      } else {
        console.error('Invalid response format:', response.data);
        setError("Định dạng dữ liệu không hợp lệ");
      }
    } catch (err) {
      console.error('Error fetching sentiment:', err);
      setError("Lỗi kết nối: " + err.message);
    } finally {
      setIsLoadingSentiment(false);
    }
  };

  // UseEffect to fetch data on dependency change
  const handleSearch = () => {
    fetchData();
  };

  // Trigger shoolOverview whenever `data` is updated
  useEffect(() => {
    if (data.length > 0) {
      shoolOverview();
      shoolSentiment();
    }
  }, [data]);

  // Fetch initial data on component mount
  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="max-w-6xl mx-auto bg-white shadow-lg rounded-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 py-6 px-8">
        <h1 className="text-3xl font-bold text-white">NCKH Sinh Viên 2025</h1>
        <p className="text-blue-100 mt-2">
          Phân tích cảm xúc của sinh viên UTC2 trên mạng xã hội
        </p>
      </div>

      {isLoadingData && (
        <div className="flex items-center p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-200">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 mr-2"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M18 10A8 8 0 11 2 10a8 8 0 0116 0zM9 9a1 1 0 012 0v5a1 1 0 11-2 0V9zm1-4a1 1 0 100 2 1 1 0 000-2z"
              clipRule="evenodd"
            />
          </svg>
          Đang tải dữ liệu...
        </div>
      )}

      {/* Summarize school situation */}
      <div className="p-4 space-y-3 max-h-96 overflow-y-auto rounded-b-lg bg-white shadow-inner">
        {!isLoadingData && (
          <div className="p-4">
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-dark">
                Tình hình trường UTC2
              </h2>
            </div>
          </div>
        )}

        {isLoadingOverView && <Loading />}

        {overViewContent && !isLoadingOverView && (
          <div className="bg-blue-50 p-6 rounded-lg border border-blue-100 shadow-sm hover:shadow-md transition-shadow duration-200">
            <div className="flex items-start space-x-4">
              <p className="text-gray-800 leading-relaxed">{overViewContent}</p>
            </div>
            <div className="mt-4 flex items-center text-sm text-gray-500">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Cập nhật lần cuối: {new Date().toLocaleString("vi-VN")}
            </div>
          </div>
        )}
      </div>

      {/* Filter Section - All in one row */}
      <div className="p-6 bg-gray-50 border-b">
        <div className="flex flex-wrap items-end space-x-4">
          <div className="flex-1 min-w-0">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Page
            </label>
            <select
              className="w-full cursor-pointer px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedPage}
              onChange={(e) => setSelectedPage(e.target.value)}
            >
              {pages.map((page, index) => (
                <option key={page} value={index}>
                  {page}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1 min-w-0">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Từ ngày
            </label>
            <input
              type="date"
              className="w-full cursor-pointer px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="flex-1 min-w-0">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Đến ngày
            </label>
            <input
              type="date"
              className="w-full cursor-pointer px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

          <div className="flex-1 min-w-0">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Chủ đề
            </label>
            <select
              className="w-full cursor-pointer px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
            >
              <option value="">Tất cả chủ đề</option>
              {topics.map((topic) => (
                <option key={topic.value} value={topic.value}>
                  {topic.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <button
              className="px-6 cursor-pointer py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
              onClick={handleSearch}
              disabled={isLoadingData}
            >
              {isLoadingData ? "Đang tải..." : "  Tìm kiếm"}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}
      </div>

      {/* View Toggle Buttons */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveView("sentiment")}
          className={`flex-1 py-3 text-center font-medium text-sm ${
            activeView === "sentiment"
              ? "text-blue-600 border-b-2 border-blue-600"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Phân tích cảm xúc
        </button>
        <button
          onClick={() => setActiveView("posts")}
          className={`flex-1 py-3 text-center font-medium text-sm ${
            activeView === "posts"
              ? "text-blue-600 border-b-2 border-blue-600"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Danh sách bài viết
        </button>
      </div>

      {/* Conditional View Content */}
      {activeView === "sentiment" ? (
        <>
          {/* Results Section - 3 columns with divider lines */}
          <div className="p-6">
            <div className="grid grid-cols-3 divide-x divide-gray-200">
              <div className="px-4">
                <div className="bg-green-500 text-white p-3 rounded-t-lg">
                  <h2 className="text-lg font-bold">Tích cực</h2>
                </div>

                {isLoadingSentiment && <Loading />}

                {sentimentContent && !isLoadingSentiment && Array.isArray(sentimentContent.positive) && (
                  <div className="p-4 space-y-3 max-h-96 overflow-y-auto rounded-b-lg">
                    {sentimentContent.positive.map((text, index) => (
                      <div
                        key={index}
                        className="bg-green-50 p-3 rounded-lg border border-green-100"
                      >
                        {truncateText(text)}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="px-4">
                <div className="bg-red-500 text-white p-3 rounded-t-lg">
                  <h2 className="text-lg font-bold">Tiêu cực</h2>
                </div>

                {isLoadingSentiment && <Loading />}

                {sentimentContent && !isLoadingSentiment && Array.isArray(sentimentContent.negative) && (
                  <div className="p-4 space-y-3 max-h-96 overflow-y-auto rounded-b-lg">
                    {sentimentContent.negative.map((text, index) => (
                      <div
                        key={index}
                        className="bg-red-50 p-3 rounded-lg border border-red-100"
                      >
                        {truncateText(text)}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="px-4">
                <div className="bg-gray-500 text-white p-3 rounded-t-lg">
                  <h2 className="text-lg font-bold">Trung lập</h2>
                </div>

                {isLoadingSentiment && <Loading />}

                {sentimentContent && !isLoadingSentiment && Array.isArray(sentimentContent.neutral) && (
                  <div className="p-4 space-y-3 max-h-96 overflow-y-auto rounded-b-lg">
                    {sentimentContent.neutral.map((text, index) => (
                      <div
                        key={index}
                        className="bg-gray-50 p-3 rounded-lg border border-gray-100"
                      >
                        {truncateText(text)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Create a section for the visualization and statistical */}
          <div className="min-h-screen bg-gray-50 p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">
              Thống kê cảm xúc
            </h1>

            {sentimentContent && !isLoadingSentiment && (
              <EmotionStats data={sentimentContent} />
            )}
          </div>
        </>
      ) : (
        // The PostList view
        <div className="p-6">
          {isLoadingData ? (
            <Loading />
          ) : (
            <PostList posts={data} />
          )}
        </div>
      )}
    </div>
  );
}