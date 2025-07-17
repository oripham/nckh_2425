import axios from "axios";
import React, { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const EmotionDashboard = ({ data, selectedTopic, startDate, endDate }) => {
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSentimentTrend = async () => {
      try {
        setLoading(true);
        // Use the provided date range or default to last year
        const endDateObj = endDate ? new Date(endDate) : new Date();
        const startDateObj = startDate ? new Date(startDate) : new Date();
        if (!startDate) {
          startDateObj.setFullYear(endDateObj.getFullYear() - 1);
        }
        
        // Format dates as YYYY-MM-DD
        const formatDate = (date) => {
          return date.toISOString().split('T')[0];
        };

        const response = await axios.get("http://127.0.0.1:8000/sentiment-trend", {
          params: {
            start_date: formatDate(startDateObj),
            end_date: formatDate(endDateObj),
            topic: selectedTopic
          }
        });
        
        if (response.data && response.data.data) {
          // Transform data to match the chart requirements
          const transformedData = response.data.data.map(item => ({
            day: item.day,
            Positive: item.Positive || 0,
            Negative: item.Negative || 0,
            Neutral: item.Neutral || 0
          }));
          setTimelineData(transformedData);
        }
      } catch (error) {
        console.error("Error fetching sentiment trend data:", error);
        // Set default data if API fails
        const defaultData = [];
        const today = new Date();
        for (let i = 11; i >= 0; i--) {
          const date = new Date(today);
          date.setMonth(today.getMonth() - i);
          defaultData.push({
            day: date.toLocaleDateString('vi-VN', { month: 'short', year: 'numeric' }),
            Positive: 0,
            Negative: 0,
            Neutral: 0
          });
        }
        setTimelineData(defaultData);
      } finally {
        setLoading(false);
      }
    };

    fetchSentimentTrend();
  }, [selectedTopic, startDate, endDate]); // Add dependencies to useEffect

  // Calculate summary data from the provided data prop
  const summaryData = [
    { name: "Tích cực", value: data?.positive?.length || 0 },
    { name: "Tiêu cực", value: data?.negative?.length || 0 },
    { name: "Trung lập", value: data?.neutral?.length || 0 },
  ];

  const COLORS = ["#4CAF50", "#F44336", "#9E9E9E"];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-4">
      {/* Bar Chart */}
      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Phân bố cảm xúc</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={summaryData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" name="Số lượng">
              {summaryData.map((entry, index) => (
                <Cell key={index} fill={COLORS[index]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Pie Chart */}
      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Tỷ lệ cảm xúc</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={summaryData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              fill="#8884d8"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {summaryData.map((entry, index) => (
                <Cell key={index} fill={COLORS[index]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [`${value} bài đăng`, 'Số lượng']} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Line Chart */}
      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">
          Xu hướng cảm xúc theo thời gian
        </h2>
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="ml-3 text-blue-500">Đang tải dữ liệu...</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <XAxis 
                dataKey="day" 
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="Positive" 
                name="Tích cực"
                stroke="#4CAF50" 
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line 
                type="monotone" 
                dataKey="Negative" 
                name="Tiêu cực"
                stroke="#F44336" 
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line 
                type="monotone" 
                dataKey="Neutral" 
                name="Trung lập"
                stroke="#9E9E9E" 
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Area Chart */}
      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Phân bố cảm xúc theo thời gian</h2>
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="ml-3 text-blue-500">Đang tải dữ liệu...</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timelineData}>
              <XAxis 
                dataKey="day" 
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="Positive"
                name="Tích cực"
                stackId="1"
                stroke="#4CAF50"
                fill="#4CAF50"
                fillOpacity={0.3}
              />
              <Area
                type="monotone"
                dataKey="Negative"
                name="Tiêu cực"
                stackId="1"
                stroke="#F44336"
                fill="#F44336"
                fillOpacity={0.3}
              />
              <Area
                type="monotone"
                dataKey="Neutral"
                name="Trung lập"
                stackId="1"
                stroke="#9E9E9E"
                fill="#9E9E9E"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Radar Chart */}
      <div className="bg-white shadow rounded-xl p-4 col-span-1 lg:col-span-2">
        <h2 className="text-lg font-semibold mb-2">Phân tích đa chiều cảm xúc</h2>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart outerRadius="80%" data={summaryData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="name" />
            <PolarRadiusAxis />
            <Radar
              name="Cảm xúc"
              dataKey="value"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.6}
            />
            <Tooltip />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default EmotionDashboard;
