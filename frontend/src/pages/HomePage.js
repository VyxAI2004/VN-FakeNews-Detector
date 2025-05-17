import React, { useState, useEffect } from 'react';
import { textProcessingService } from '../services/api';
import ApiErrorAlert from '../components/common/ApiErrorAlert';
import './HomePage.css';


const HomePage = () => {
  const [inputText, setInputText] = useState('');
  const [inputUrl, setInputUrl] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [shouldSummarize, setShouldSummarize] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [detailedAnalysis, setDetailedAnalysis] = useState(false);
  const [factChecking, setFactChecking] = useState(false);
  const [sourceAnalysis, setSourceAnalysis] = useState(false);

  // Reset error khi input thay đổi
  useEffect(() => {
    if (error) {
      setError(null);
    }
  }, [inputText, inputUrl, error]);

  // Load history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('analysisHistory');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Error loading history:', e);
      }
    }
  }, []);

  const handleClear = () => {
    setInputText('');
    setInputUrl('');
    setError(null);
  };

  const handleSampleNews = () => {
    setInputText('Nhiệt độ tại Bắc Cực tăng cao kỷ lục, các nhà khoa học cảnh báo về tình trạng băng tan nhanh chóng. Theo số liệu vệ tinh, nhiệt độ trung bình tại Bắc Cực đã tăng 3 độ C trong thập kỷ qua, cao hơn gấp đôi so với mức tăng trung bình toàn cầu. Các nhà khoa học cho biết nếu tình trạng này tiếp tục, mực nước biển có thể dâng cao tới 7 mét vào năm 2100.');
    setInputUrl('');
  };

  const handleFakeNewsSample = () => {
    setInputText('NÓNG: Các nhà khoa học tuyên bố tất cả các nghiên cứu về biến đổi khí hậu đều là hoang đường. Một nghiên cứu bí mật gây chấn động giới khoa học chỉ ra rằng nhiệt độ toàn cầu đang thực tế đang giảm. Các nguồn tin nội bộ từ NASA cho biết cơ quan này đã che giấu sự thật này suốt nhiều năm qua để nhận nguồn tài trợ khổng lồ từ chính phủ. Dữ liệu nhiệt độ từ 10.000 trạm thời tiết trên khắp thế giới đã bị sửa đổi để làm cho trái đất có vẻ nóng lên.');
    setInputUrl('');
  };

  const handleSaveToHistory = (result) => {
    const historyItem = {
      id: Date.now(),
      date: new Date().toLocaleString(),
      text: inputText.substring(0, 100) + (inputText.length > 100 ? '...' : ''),
      url: inputUrl,
      result: {
        is_fake: result.is_fake,
        confidence: result.confidence
      }
    };

    const updatedHistory = [historyItem, ...history].slice(0, 50); // Keep only the most recent 50 items
    setHistory(updatedHistory);
    localStorage.setItem('analysisHistory', JSON.stringify(updatedHistory));
  };

  const handleClearHistory = () => {
    if (window.confirm('Bạn có chắc chắn muốn xóa tất cả lịch sử phân tích?')) {
      setHistory([]);
      localStorage.removeItem('analysisHistory');
    }
  };

  const handleLoadFromHistory = (historyItem) => {
    setInputUrl(historyItem.url || '');
    if (historyItem.text) {
      // Remove '...' if it exists at the end
      const fullText = historyItem.text.endsWith('...') 
        ? historyItem.text.slice(0, -3) 
        : historyItem.text;
      setInputText(fullText);
    } else {
      setInputText('');
    }
  };

  const handleProcess = async () => {
    // Kiểm tra nếu không có input nào
    if (!inputText.trim() && !inputUrl.trim()) {
      setError('Vui lòng nhập văn bản hoặc URL của bài báo');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      // Tạo object chứa các dữ liệu gửi lên server
      const requestData = {
        text: inputText.trim(),
        url: inputUrl.trim(),
        options: {
          summarize: shouldSummarize,
          detailed_analysis: detailedAnalysis,
          fact_checking: factChecking,
          source_analysis: sourceAnalysis
        }
      };

      const response = await textProcessingService.detectFakeNews(requestData);

      if (response.data) {
        setResults(response.data);
        handleSaveToHistory(response.data);
          } else {
        throw new Error('Không nhận được kết quả từ server');
          }
        } catch (error) {
      console.error('Lỗi khi phân tích:', error);
      setError('Không thể phân tích bài viết: ' + (error.response?.data?.message || error.message || 'Lỗi kết nối đến máy chủ'));
    } finally {
        setIsLoading(false);
    }
  };

  const renderGuide = () => (
    <div className="guide-container">
      <div className="card">
        <div className="card-header">
          <div className="d-flex align-items-center justify-content-between">
            <h5 className="mb-0"><i className="fas fa-book me-2"></i> Hướng dẫn sử dụng</h5>
            <button 
              className="btn btn-sm btn-outline-secondary" 
              onClick={() => setShowGuide(false)}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>
        <div className="card-body guide-content">
          <h6>Cách kiểm tra tin tức</h6>
          <ol>
            <li>
              <strong>Nhập thông tin bài viết</strong>
              <p>Có hai cách để kiểm tra bài viết:</p>
              <ul>
                <li>Nhập URL của bài báo (được khuyến nghị)</li>
                <li>Sao chép và dán nội dung bài báo vào ô nội dung</li>
              </ul>
            </li>
            <li>
              <strong>Tùy chọn kiểm tra</strong>
              <p>Bạn có thể tùy chỉnh các tùy chọn kiểm tra theo nhu cầu:</p>
              <ul>
                <li><strong>Tóm tắt bài viết:</strong> Tạo một bản tóm tắt ngắn gọn về nội dung bài viết</li>
                <li><strong>Phân tích chi tiết:</strong> Cung cấp phân tích sâu hơn về nội dung bài viết</li>
                <li><strong>Kiểm tra thông tin:</strong> So sánh thông tin trong bài viết với các nguồn tin cậy</li>
                <li><strong>Phân tích nguồn:</strong> Đánh giá độ tin cậy của nguồn bài viết</li>
              </ul>
            </li>
            <li>
              <strong>Phân tích kết quả</strong>
              <p>Sau khi nhận được kết quả, hãy xem xét:</p>
              <ul>
                <li><strong>Độ tin cậy:</strong> Càng cao càng đáng tin cậy</li>
                <li><strong>Lý do:</strong> Giải thích tại sao hệ thống đưa ra kết luận</li>
                <li><strong>Thông tin nguồn:</strong> Độ uy tín của tên miền và trang web</li>
              </ul>
            </li>
          </ol>

          <h6 className="mt-4">Lưu ý quan trọng</h6>
          <div className="alert alert-info">
            <p className="mb-0">Công cụ này sử dụng trí tuệ nhân tạo để phân tích tin tức, nhưng kết quả không phải lúc nào cũng hoàn toàn chính xác. Vui lòng sử dụng kết quả như một tham khảo, và luôn kiểm tra thông tin từ nhiều nguồn tin cậy khác.</p>
          </div>
          
          <h6 className="mt-4">Các tính năng khác</h6>
          <ul>
            <li><strong>Lịch sử kiểm tra:</strong> Xem lại các bài viết đã kiểm tra trước đó</li>
            <li><strong>Mẫu thử:</strong> Dùng các ví dụ về tin thật/giả để thử nghiệm hệ thống</li>
          </ul>
            </div>
            </div>
          </div>
        );

  const renderHistory = () => (
    <div className="history-container">
      <div className="card">
        <div className="card-header">
          <div className="d-flex align-items-center justify-content-between">
            <h5 className="mb-0"><i className="fas fa-history me-2"></i> Lịch sử phân tích</h5>
            <button 
              className="btn btn-sm btn-outline-secondary" 
              onClick={() => setShowHistory(false)}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
            </div>
        <div className="card-body p-0">
          {history.length === 0 ? (
            <div className="text-center p-4 text-muted">
              <i className="fas fa-inbox fa-2x mb-3"></i>
              <p>Chưa có lịch sử phân tích</p>
                        </div>
          ) : (
            <>
              <div className="list-group list-group-flush history-list">
                {history.map(item => (
                  <button 
                    key={item.id} 
                    className="list-group-item list-group-item-action" 
                    onClick={() => handleLoadFromHistory(item)}
                  >
                    <div className="d-flex w-100 justify-content-between">
                      <h6 className="mb-1 text-truncate" style={{maxWidth: "70%"}}>
                        {item.url ? (new URL(item.url)).hostname : 'Văn bản nhập trực tiếp'}
                      </h6>
                      <small className="text-muted">{item.date}</small>
                        </div>
                    <p className="mb-1 text-truncate">{item.text}</p>
                    <div>
                      <span className={`badge ${item.result.is_fake ? 'bg-danger' : 'bg-success'} me-2`}>
                        {item.result.is_fake ? 'Tin giả' : 'Tin thật'}
                      </span>
                      <small>Độ tin cậy: {(item.result.confidence * 100).toFixed(2)}%</small>
                      </div>
                  </button>
            ))}
          </div>
              <div className="p-3 border-top">
                <button 
                  className="btn btn-outline-danger btn-sm" 
                  onClick={handleClearHistory}
                >
                  <i className="fas fa-trash-alt me-1"></i> Xóa lịch sử
                </button>
              </div>
            </>
              )}
            </div>
            </div>
              </div>
  );

  const renderAdvancedOptions = () => (
    <div className="advanced-options-container">
            <div className="card">
        <div className="card-header">
          <div className="d-flex align-items-center justify-content-between">
            <h5 className="mb-0"><i className="fas fa-sliders-h me-2"></i> Tùy chọn nâng cao</h5>
                <button 
                  className="btn btn-sm btn-outline-secondary" 
              onClick={() => setShowAdvancedOptions(false)}
                >
                  <i className="fas fa-times"></i>
                </button>
          </div>
              </div>
              <div className="card-body">
          <div className="mb-3">
            <div className="form-check form-switch">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="detailed-analysis-option"
                checked={detailedAnalysis}
                onChange={(e) => setDetailedAnalysis(e.target.checked)}
                disabled={isLoading}
              />
              <label className="form-check-label" htmlFor="detailed-analysis-option">
                Phân tích chi tiết
              </label>
                </div>
            <small className="text-muted d-block mt-1">
              Phân tích sâu hơn về cấu trúc ngôn ngữ, ngữ cảnh và các yếu tố nghiêm túc của bài viết
            </small>
                </div>
          
          <div className="mb-3">
            <div className="form-check form-switch">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="fact-checking-option"
                checked={factChecking}
                onChange={(e) => setFactChecking(e.target.checked)}
                disabled={isLoading}
              />
              <label className="form-check-label" htmlFor="fact-checking-option">
                Kiểm tra thông tin
              </label>
                </div>
            <small className="text-muted d-block mt-1">
              So sánh thông tin trong bài viết với các nguồn tin cậy
            </small>
              </div>
          
          <div className="mb-3">
            <div className="form-check form-switch">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="source-analysis-option"
                checked={sourceAnalysis}
                onChange={(e) => setSourceAnalysis(e.target.checked)}
                disabled={isLoading}
              />
              <label className="form-check-label" htmlFor="source-analysis-option">
                Phân tích nguồn
              </label>
            </div>
            <small className="text-muted d-block mt-1">
              Đánh giá độ tin cậy của nguồn dựa trên lịch sử và uy tín
            </small>
          </div>
          
          <hr />
          
          <div className="mb-3">
            <div className="form-check form-switch">
              <input 
                className="form-check-input" 
                type="checkbox" 
                id="summarize-option"
                checked={shouldSummarize}
                onChange={(e) => setShouldSummarize(e.target.checked)}
                disabled={isLoading}
              />
              <label className="form-check-label" htmlFor="summarize-option">
                Tóm tắt bài viết
              </label>
        </div>
            <small className="text-muted d-block mt-1">
              Tạo bản tóm tắt ngắn gọn về nội dung bài viết
            </small>
      </div>
        </div>
      </div>
    </div>
  );

  const renderInputPanel = () => (
    <div className="input-panel">
      <div className="card input-card">
              <div className="card-header sticky-top">
                <div className="d-flex align-items-center">
                  <i className="fas fa-edit me-2 text-primary-1 animated-icon"></i>
            <h5 className="mb-0">Nhập thông tin bài viết</h5>
                </div>
              </div>
              <div className="card-body">
          <div className="form-group mb-3">
            <label htmlFor="input-url" className="form-label">
              <i className="fas fa-link me-1"></i> URL bài báo
            </label>
            <input 
              type="text" 
              id="input-url" 
              className="form-control" 
              placeholder="Nhập URL của bài báo (nếu có)..."
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              disabled={isLoading}
            />
          </div>
          
          <div className="form-group mb-3">
            <label htmlFor="input-text" className="form-label">
              <i className="fas fa-newspaper me-1"></i> Nội dung bài viết
            </label>
                  <textarea 
                    id="input-text" 
                    className="form-control" 
                    rows="8" 
              placeholder="Nhập nội dung bài viết cần kiểm tra..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    disabled={isLoading}
                  ></textarea>
                </div>
                
          <div className="form-actions d-flex flex-wrap gap-2 mb-3">
            <button 
              className="btn btn-outline-primary"
              onClick={() => setShowAdvancedOptions(true)}
              disabled={isLoading}
            >
              <i className="fas fa-sliders-h me-1"></i> Tùy chọn nâng cao
            </button>
            
            <div className="dropdown">
                  <button 
                    className="btn btn-outline-secondary-2 dropdown-toggle" 
                    type="button" 
                id="sampleDropdown" 
                    data-bs-toggle="dropdown" 
                    aria-expanded="false"
                    disabled={isLoading}
                  >
                <i className="fas fa-file-alt me-1"></i> Thử mẫu
                  </button>
              <ul className="dropdown-menu" aria-labelledby="sampleDropdown">
                <li><button className="dropdown-item" onClick={handleSampleNews}>Tin thật mẫu</button></li>
                <li><button className="dropdown-item" onClick={handleFakeNewsSample}>Tin giả mẫu</button></li>
                  </ul>
            </div>
            
            <button 
              className="btn btn-outline-secondary-1"
              onClick={() => setShowHistory(true)}
              disabled={isLoading}
            >
              <i className="fas fa-history me-1"></i> Lịch sử
            </button>
            
            <button 
              className="btn btn-outline-info"
              onClick={() => setShowGuide(true)}
              disabled={isLoading}
            >
              <i className="fas fa-question-circle me-1"></i> Hướng dẫn
            </button>
                </div>
                
                <div className="d-flex">
                  <button 
                    className="btn btn-light me-2"
                    onClick={handleClear}
              disabled={isLoading || (!inputText.trim() && !inputUrl.trim())}
                  >
                    <i className="fas fa-eraser me-1"></i> Xóa
                  </button>

                  <button 
                    className="btn btn-primary ms-auto"
                    onClick={handleProcess}
              disabled={isLoading || (!inputText.trim() && !inputUrl.trim())}
                  >
                    {isLoading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                        Đang xử lý...
                      </>
                    ) : (
                      <>
                  <i className="fas fa-search me-1"></i> Phân tích
                      </>
                    )}
                  </button>
                </div>
        </div>
      </div>
    </div>
  );

  const renderResults = () => {
    if (isLoading) {
      return (
        <div className="loading-indicator">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Đang xử lý...</span>
                  </div>
          <p className="mt-3">Đang phân tích bài viết...</p>
              </div>
      );
    }

    if (error) {
      return <ApiErrorAlert message={error} onRetry={handleProcess} />;
    }

    if (!results) {
      return (
        <div className="results-placeholder">
          <i className="fas fa-arrow-left fa-3x mb-3"></i>
          <p>Nhập thông tin bài viết và nhấn "Phân tích" để xem kết quả tại đây</p>
            </div>
      );
    }

    // Hiển thị kết quả
    return (
      <div className="results-container">
        <div className="result-card">
          <div className="result-header">
            <h4 className="mb-0">
              <i className={`fas fa-${results.is_fake ? 'times-circle text-danger' : 'check-circle text-success'} me-2`}></i>
              Kết quả phân tích
            </h4>
          </div>
          <div className="result-body">
            <div className="prediction-result p-4 text-center">
              <div className="prediction-badge mb-3">
                <span className={`badge ${results.is_fake ? 'bg-danger' : 'bg-success'} p-3 fs-4`}>
                  {results.is_fake ? 'TIN GIẢ' : 'TIN THẬT'}
                </span>
              </div>
              <div className="confidence-meter mt-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>Độ tin cậy</span>
                  <span><strong>{(results.confidence * 100).toFixed(2)}%</strong></span>
                </div>
                <div className="progress" style={{ height: '10px' }}>
                  <div 
                    className={`progress-bar ${results.is_fake ? 'bg-danger' : 'bg-success'}`}
                    role="progressbar" 
                    style={{ width: `${results.confidence * 100}%` }}
                    aria-valuenow={results.confidence * 100} 
                    aria-valuemin="0" 
                    aria-valuemax="100"
                  ></div>
                </div>
              </div>
          </div>

            {results.reasons && results.reasons.length > 0 && (
              <div className="reasons-section mt-4">
                <h5><i className="fas fa-info-circle me-2"></i>Lý do:</h5>
                <ul className="list-group">
                  {results.reasons.map((reason, index) => (
                    <li key={index} className="list-group-item">
                      <i className="fas fa-angle-right me-2"></i>
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {results.summary && (
              <div className="summary-section mt-4">
                <h5><i className="fas fa-compress-alt me-2"></i>Tóm tắt bài viết:</h5>
                <div className="card">
                  <div className="card-body bg-light">
                    <p className="card-text">{results.summary}</p>
                </div>
              </div>
              </div>
            )}

            {results.source_info && (
              <div className="source-section mt-4">
                <h5><i className="fas fa-link me-2"></i>Thông tin nguồn:</h5>
                <table className="table table-bordered">
                  <tbody>
                    {results.source_info.domain && (
                      <tr>
                        <td className="fw-bold" style={{width: "30%"}}>Tên miền:</td>
                        <td>{results.source_info.domain}</td>
                      </tr>
                    )}
                    {results.source_info.reputation && (
                      <tr>
                        <td className="fw-bold">Uy tín nguồn:</td>
                        <td>
                          <span className={`badge ${getReputationBadgeClass(results.source_info.reputation)}`}>
                            {getReputationText(results.source_info.reputation)}
                          </span>
                        </td>
                      </tr>
                    )}
                    {results.source_info.category && (
                      <tr>
                        <td className="fw-bold">Danh mục:</td>
                        <td>{results.source_info.category}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {results.fact_checks && results.fact_checks.length > 0 && (
              <div className="fact-checks-section mt-4">
                <h5><i className="fas fa-check-double me-2"></i>Kiểm tra thông tin:</h5>
                <div className="accordion" id="factChecksAccordion">
                  {results.fact_checks.map((factCheck, index) => (
                    <div className="accordion-item" key={index}>
                      <h2 className="accordion-header" id={`heading${index}`}>
                <button 
                          className="accordion-button collapsed" 
                          type="button" 
                          data-bs-toggle="collapse" 
                          data-bs-target={`#collapse${index}`} 
                          aria-expanded="false" 
                          aria-controls={`collapse${index}`}
                        >
                          <span className={`badge ${factCheck.accurate ? 'bg-success' : 'bg-danger'} me-2`}>
                            {factCheck.accurate ? 'Chính xác' : 'Không chính xác'}
                          </span>
                          {factCheck.claim}
                </button>
                      </h2>
                      <div 
                        id={`collapse${index}`} 
                        className="accordion-collapse collapse" 
                        aria-labelledby={`heading${index}`} 
                        data-bs-parent="#factChecksAccordion"
                      >
                        <div className="accordion-body">
                          <p><strong>Kết luận:</strong> {factCheck.explanation}</p>
                          {factCheck.sources && factCheck.sources.length > 0 && (
                            <>
                              <p className="mb-1"><strong>Nguồn tham khảo:</strong></p>
                              <ul className="sources-list">
                                {factCheck.sources.map((source, i) => (
                                  <li key={i}>
                                    <a href={source.url} target="_blank" rel="noopener noreferrer">
                                      {source.name}
                                    </a>
                                  </li>
                                ))}
                              </ul>
                            </>
                          )}
              </div>
            </div>
          </div>
                  ))}
        </div>
      </div>
            )}

            {results.linguistic_analysis && (
              <div className="linguistic-section mt-4">
                <h5><i className="fas fa-language me-2"></i>Phân tích ngôn ngữ:</h5>
                <div className="card">
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-6">
                        <h6 className="mb-3">Chỉ số độ tin cậy</h6>
                        {Object.entries(results.linguistic_analysis.scores).map(([key, value], index) => {
                          const score = parseFloat(value);
                          const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                          return (
                            <div className="mb-3" key={index}>
                              <div className="d-flex justify-content-between mb-1">
                                <span>{label}</span>
                                <span>{score.toFixed(2)}/10</span>
                              </div>
                              <div className="progress" style={{ height: '8px' }}>
                                <div 
                                  className={`progress-bar bg-${score >= 7 ? 'success' : score >= 4 ? 'warning' : 'danger'}`}
                                  role="progressbar" 
                                  style={{ width: `${score * 10}%` }}
                                  aria-valuenow={score * 10} 
                                  aria-valuemin="0" 
                                  aria-valuemax="100"
                                ></div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      <div className="col-md-6">
                        <h6 className="mb-3">Đặc điểm văn bản</h6>
                        <ul className="list-group">
                          {results.linguistic_analysis.features && 
                           Object.entries(results.linguistic_analysis.features).map(([key, value], index) => {
                            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                            return (
                              <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                                {label}
                                <span>{typeof value === 'boolean' ? (value ? 'Có' : 'Không') : value}</span>
                              </li>
                            );
                          })}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Hàm hỗ trợ để lấy class cho badge hiển thị độ tin cậy của nguồn
  const getReputationBadgeClass = (reputation) => {
    if (reputation >= 8) return 'bg-success';
    if (reputation >= 5) return 'bg-warning';
    return 'bg-danger';
  };

  // Hàm hỗ trợ để hiển thị text tương ứng với điểm độ tin cậy
  const getReputationText = (reputation) => {
    if (reputation >= 8) return 'Đáng tin cậy';
    if (reputation >= 5) return 'Cần kiểm chứng';
    return 'Đáng ngờ';
  };

  return (
    <>
      <div style={{
        backgroundImage: "url('/image/image.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center 5px", 
        position: "relative",
        padding: "6rem 1rem",
        marginBottom: "2rem",
        overflow: "hidden",
        textAlign: "center"
      }}>
        {/* Dark overlay */}
        <div style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.6)"
        }} />
        {/* Content */}
        <div className="container" style={{ position: "relative", zIndex: 1 }}>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="display-4" style={{ color: "white", fontWeight: "700", marginBottom: "1rem" }}>Kiểm Tra Tin Giả</h1>
              <p className="lead" style={{ color: "rgba(255, 255, 255, 0.9)", maxWidth: "800px", margin: "0 auto" }}>Công cụ giúp bạn xác định độ tin cậy của các bài báo</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container main-content">
        <div className="row">
          {/* Bố cục hai cột: input bên trái, kết quả bên phải */}
          <div className="col-lg-6 input-column">
            {renderInputPanel()}
          </div>
          <div className="col-lg-6 results-column">
            {renderResults()}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showGuide && renderGuide()}
      {showHistory && renderHistory()}
      {showAdvancedOptions && renderAdvancedOptions()}
    </>
  );
};

export default HomePage; 