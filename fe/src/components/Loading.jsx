import React from "react";

const Loading = () => {
  return (
    <div className="flex items-center p-4 border border-gray-200 rounded-lg">
      <div className="ml-3 text-gray-600 flex items-center">
        <span>Đang phân tích</span>
        <span className="inline-flex ml-1">
          <span className="animate-bounce mx-px delay-75">.</span>
          <span
            className="animate-bounce mx-px delay-150"
            style={{ animationDelay: "0.2s" }}
          >
            .
          </span>
          <span
            className="animate-bounce mx-px delay-300"
            style={{ animationDelay: "0.4s" }}
          >
            .
          </span>
        </span>
      </div>
    </div>
  );
};

export default Loading;
