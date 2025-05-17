import axios from 'axios';

const throttledApiCalls = {};

function throttle(func, wait) {
  let lastCall = 0;
  let timeout = null;
  let result;
  
  return function(...args) {
    const now = Date.now();
    const remaining = wait - (now - lastCall);
    
    if (throttledApiCalls[func.name] && remaining > 0) {
      console.log('Throttled API call:', func.name);
      return throttledApiCalls[func.name];
    }
    
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
    }
    
    lastCall = now;

    result = func(...args);
    throttledApiCalls[func.name] = result;
    
    timeout = setTimeout(() => {
      delete throttledApiCalls[func.name];
    }, wait);
    
    return result;
  };
}

// Định nghĩa Axios instance với các cấu hình cơ bản
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 30000 // Tăng timeout lên 30 giây cho các yêu cầu phức tạp
});

// Thêm interceptor để xử lý lỗi
API.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    
    // Ghi log lỗi
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error setting up request:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Text processing services - Sử dụng cho HomePage
export const textProcessingService = {
  // Lấy văn bản mẫu
  getSampleText: (category) => API.get(`/api/sample_text?category=${category}`),
  
  // Xử lý văn bản với các tùy chọn
  processWithOptions: (options) => {
    console.log('Sending API request with options:', options);
    // Thêm timeout cho requests lớn
    return API.post('/api/process_with_options', options, {
      timeout: 60000, // 60 seconds for complex processing
      headers: {
        'Content-Type': 'application/json'
      }
    });
  },
  
  // Làm sạch văn bản
  cleanText: (text) => API.post('/api/clean_text', { text }),
  
  // Tokenize câu
  tokenizeSentences: (text) => API.post('/api/tokenize_sentences', { text }),
  
  // Vector hóa văn bản
  vectorizeText: (text, vector_type, ngram_min, ngram_max) => 
    API.post('/api/vectorize', { text, vector_type, ngram_min, ngram_max }),
  
  // Phân loại văn bản
  classifyText: (text, model_type, use_clean_text) => 
    API.post('/api/classify_text', { text, model_type, use_clean_text }),
    
  // API tải lên file
  uploadFile: (formData) => {
    return API.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // API tải xuống file kết quả
  downloadResult: (filename) => API.get(`/outputs/${filename}`, {
    responseType: 'blob'
  }),

  // API phát hiện tin tức thật/giả
  detectFakeNews: (data) => {
    console.log('Sending API request to detect fake news:', data);
    return API.post('/api/detect_fake_news', data, {
      timeout: 60000, // 60 seconds for processing
      headers: {
        'Content-Type': 'application/json'
      }
    });
  },
};

// File processing services - Hỗ trợ xử lý file
export const fileService = {
  // API tải lên file
  uploadFile: (formData) => {
    return API.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // API xử lý file
  processFile: (filename, options) => API.post('/process_file', { filename, ...options }),
  
  // API tải xuống file kết quả
  downloadFile: (filename) => API.get(`/outputs/${filename}`, {
    responseType: 'blob'
  }),
};

export default {
  textProcessingService,
  fileService,
}; 