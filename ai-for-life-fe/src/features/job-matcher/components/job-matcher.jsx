import React, { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/";
const ENDPOINTS = {
  matchManual: "jobs/search",
  matchCV: "job-matcher/match-cv",
  uploadResume: "jobs/upload-resume",
};

const normalizeJobs = (raw) => {
  const list = Array.isArray(raw?.data) ? raw.data : Array.isArray(raw) ? raw : [];
  return list.map((j, idx) => {
    const rawSkills = j.skills ?? j.requiredSkills ?? [];
    const skills = Array.isArray(rawSkills)
      ? rawSkills
          .map((s) => (typeof s === "string" ? s : s?.name ?? s?.skill ?? s?.label ?? s?.title ?? s?.value ?? ""))
          .filter(Boolean)
      : [];
    return ({
      id: j.id ?? j._id ?? idx,
      title: j.title ?? j.jobTitle ?? "",
      company: j.company ?? j.companyName ?? "",
      location: j.location ?? j.city ?? "",
      salary: j.salary ?? j.salary_range ?? "",
      type: j.type ?? j.employmentType ?? "",
      postedTime: j.postedTime ?? j.posted_at ?? "",
      description: j.description ?? j.summary ?? "",
      skills,
      matchPercentage: Math.round(
        (j.matchPercentage ?? j.match_score ?? j.score ?? 0) * (j.matchPercentage ? 1 : 100)
      ),
      raw: j,
    });
  });
};

const FieldLabel = ({ children }) => (
  <label className="block text-sm font-medium text-gray-700 mb-1">{children}</label>
);

const JobCard = ({ job }) => {
  const [showDetails, setShowDetails] = useState(false);
  return (
  <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <div className="flex items-start justify-between mb-3">
      <div className="flex-1">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{job.title}</h3>
        <p className="text-gray-600 text-sm">{job.company}</p>
      </div>
      <div className="text-right ml-4">
        <div className="inline-flex items-center gap-2 bg-gray-900 text-white px-3 py-1 rounded-full text-sm font-medium">
          {job.matchPercentage}% phù hợp
        </div>
        <div className="mt-2 w-24 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gray-900 rounded-full"
            style={{ width: `${job.matchPercentage}%` }}
          />
        </div>
      </div>
    </div>

    <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
      <div className="flex items-center gap-2 text-gray-600">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span>{job.location}</span>
      </div>
      <div className="flex items-center gap-2 text-gray-600">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span>{job.type}</span>
      </div>
      <div className="flex items-center gap-2 text-gray-600">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{job.salary}</span>
      </div>
      <div className="flex items-center gap-2 text-gray-600">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{job.postedTime}</span>
      </div>
    </div>

    <p className="text-gray-700 text-sm mb-4 line-clamp-3">{job.description}</p>

    <div className="flex flex-wrap gap-2 mb-4">
      {job.skills.map((skill, idx) => (
        <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
          {skill}
        </span>
      ))}
    </div>

    {showDetails && (
      <div className="mt-3">
        <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs overflow-auto max-h-60">
{JSON.stringify(job.raw ?? job, null, 2)}
        </pre>
      </div>
    )}

    <div className="flex gap-3 mt-2">
      <button className="flex-1 bg-gray-900 text-white py-2.5 rounded-lg font-medium hover:bg-black transition-colors flex items-center justify-center gap-2">
        Ứng tuyển ngay
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
      </button>
      <button type="button" onClick={() => setShowDetails((v) => !v)} className="px-3 py-2.5 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
        {showDetails ? "Ẩn chi tiết" : "Chi tiết"}
      </button>
    </div>
  </div>
  );
};

export const JobMatcherPage = () => {
  const [inputMode, setInputMode] = useState("manual"); // "manual" or "cv"
  const [form, setForm] = useState({
    position: "",
    skills: "",
    years: "",
    summary: "",
  });
  const [cvFile, setCvFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [results, setResults] = useState(null);
  const [lastQuery, setLastQuery] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState("match");

  const onChange = (e) => setForm((s) => ({ ...s, [e.target.name]: e.target.value }));
  
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && (file.type === "application/pdf" || file.name.endsWith(".pdf"))) {
      setCvFile(file);
      // Immediately upload to extract JD info
      (async () => {
        try {
          const fd = new FormData();
          fd.append("file", file);
          fd.append("title", form.position || "");
          const url = `${API_BASE}${ENDPOINTS.uploadResume}`;
          console.log("[JobMatcher] POST", url);
          const res = await fetch(url, { method: "POST", body: fd });
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`HTTP ${res.status} ${res.statusText} - ${text}`);
          }
          const data = await res.json().catch(() => ({}));
          // Normalize potential response fields
          const position = data.position || data.jobTitle || data.title || "";
          const skillsRaw = data.skills || data.requiredSkills || data.keywords || [];
          const skills = Array.isArray(skillsRaw)
            ? skillsRaw
                .map((s) => (typeof s === "string" ? s : s?.name ?? s?.skill ?? s?.label ?? s?.title ?? s?.value ?? ""))
                .filter(Boolean)
            : [];
          const years = data.years || data.experienceYears || data.experience || "";
          const summary = data.summary || data.description || data.overview || "";

          // Prefill form and show JD info summary like manual mode
          setForm((s) => ({
            ...s,
            position,
            skills: skills.join(", "),
            years,
            summary,
          }));
          setLastQuery({ mode: "manual", position, skills, years, summary });
        } catch (err) {
          console.error("[JobMatcher] Upload resume API error:", err);
          alert(`Có lỗi khi trích xuất thông tin từ CV. Vui lòng thử lại.\n\n${err?.message ?? err}`);
        }
      })();
    } else if (file) {
      alert("Vui lòng chọn file PDF");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type === "application/pdf" || file.name.endsWith(".pdf"))) {
      setCvFile(file);
      // Upload dropped file to extract JD info
      (async () => {
        try {
          const fd = new FormData();
          fd.append("file", file);
          fd.append("title", form.position || "");
          const url = `${API_BASE}${ENDPOINTS.uploadResume}`;
          console.log("[JobMatcher] POST", url);
          const res = await fetch(url, { method: "POST", body: fd });
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`HTTP ${res.status} ${res.statusText} - ${text}`);
          }
          const data = await res.json().catch(() => ({}));
          const position = data.position || data.jobTitle || data.title || "";
          const skillsRaw = data.skills || data.requiredSkills || data.keywords || [];
          const skills = Array.isArray(skillsRaw)
            ? skillsRaw
                .map((s) => (typeof s === "string" ? s : s?.name ?? s?.skill ?? s?.label ?? s?.title ?? s?.value ?? ""))
                .filter(Boolean)
            : [];
          const years = data.years || data.experienceYears || data.experience || "";
          const summary = data.summary || data.description || data.overview || "";

          setForm((s) => ({
            ...s,
            position,
            skills: skills.join(", "),
            years,
            summary,
          }));
          setLastQuery({ mode: "manual", position, skills, years, summary });
        } catch (err) {
          console.error("[JobMatcher] Upload resume API error:", err);
          alert(`Có lỗi khi trích xuất thông tin từ CV. Vui lòng thử lại.\n\n${err?.message ?? err}`);
        }
      })();
    } else if (file) {
      alert("Vui lòng chọn file PDF");
    }
  };

  const removeFile = () => {
    setCvFile(null);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (inputMode === "cv") {
        if (!cvFile) {
          alert("Vui lòng upload CV");
          setIsLoading(false);
          return;
        }
        const fd = new FormData();
        fd.append("file", cvFile);
        fd.append("title", form.position || "");
        const url = `${API_BASE}${ENDPOINTS.uploadResume}`;
        console.log("[JobMatcher] POST", url);
        const res = await fetch(url, {
          method: "POST",
          body: fd,
        });
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`HTTP ${res.status} ${res.statusText} - ${text}`);
        }
        const data = await res.json().catch(() => ({}));
        setResults(normalizeJobs(data));
        setLastQuery({ mode: "cv", fileName: cvFile?.name || "CV.pdf" });
      } else {
        const payload = {
          position: form.position,
          skills: form.skills.split(',').map(skill => skill.trim()).filter(Boolean),
          years: form.years,
          summary: form.summary,
        };
        const url = `${API_BASE}${ENDPOINTS.matchManual}`;
        console.log("[JobMatcher] POST", url, JSON.stringify(payload, null, 2));
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`HTTP ${res.status} ${res.statusText} - ${text}`);
        }
        const data = await res.json().catch(() => ({}));
        setResults(normalizeJobs(data));
        setLastQuery({ mode: "manual", ...payload });
      }
    } catch (err) {
      console.error("[JobMatcher] API error:", err);
      alert(`Có lỗi khi gọi API. Vui lòng thử lại.\n\n${err?.message ?? err}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#eef4ff]">
      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 text-indigo-600 font-semibold text-lg mb-2">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20 6h-3V4c0-1.11-.89-2-2-2H9c-1.11 0-2 .89-2 2v2H4c-1.11 0-2 .89-2 2v11c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zM9 4h6v2H9V4zm11 15H4V8h16v11z"/>
            </svg>
            <span>AI Job Matcher</span>
          </div>
          <p className="text-gray-600">Tìm công việc phù hợp với CV của bạn bằng AI</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6">
          {/* Left: Form */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="text-base font-semibold text-gray-800 mb-5">Nhập thông tin của bạn</h2>
            
            {/* Mode Selection */}
            <div className="mb-6">
              <div className="inline-flex rounded-lg border border-gray-300 p-1 bg-gray-50">
                <button
                  type="button"
                  onClick={() => setInputMode("manual")}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                    inputMode === "manual"
                      ? "bg-white text-gray-900 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  Nhập thủ công
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode("cv")}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                    inputMode === "cv"
                      ? "bg-white text-gray-900 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  Upload CV
                </button>
              </div>
            </div>

            <form className="space-y-4" onSubmit={onSubmit}>
              {/* CV Upload Section - Only show in CV mode */}
              {inputMode === "cv" && <div>
                <FieldLabel>Upload CV (PDF)</FieldLabel>
                {!cvFile ? (
                  <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
                      isDragging
                        ? "border-indigo-500 bg-indigo-50"
                        : "border-gray-300 hover:border-indigo-400 hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="file"
                      accept=".pdf,application/pdf"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <svg
                      className="w-10 h-10 mx-auto mb-2 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                    <p className="text-sm text-gray-600 font-medium mb-1">
                      Kéo thả file CV hoặc click để chọn
                    </p>
                    <p className="text-xs text-gray-500">Chỉ hỗ trợ file PDF</p>
                  </div>
                ) : (
                  <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                          <svg
                            className="w-5 h-5 text-red-600"
                            fill="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM8 18v-2h8v2H8zm0-4v-2h8v2H8z" />
                          </svg>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">
                            {cvFile.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(cvFile.size / 1024).toFixed(1)} KB
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={removeFile}
                        className="ml-2 flex-shrink-0 p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
                      >
                        <svg
                          className="w-5 h-5 text-gray-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
                {/* Extracted JD info summary (from uploaded CV) */}
                {lastQuery?.mode === "manual" && (
                  <div className="mt-4 border border-gray-200 rounded-xl p-4 bg-white">
                    <div className="text-sm text-gray-700 font-medium mb-2">Thông tin JD trích xuất</div>
                    <div className="flex flex-wrap gap-2 text-sm">
                      {lastQuery.position && (
                        <span className="px-3 py-1 bg-gray-100 rounded-full">Vị trí: <span className="font-medium">{lastQuery.position}</span></span>
                      )}
                      {Array.isArray(lastQuery.skills) && lastQuery.skills.length > 0 && (
                        <span className="px-3 py-1 bg-gray-100 rounded-full">Kỹ năng: <span className="font-medium">{lastQuery.skills.join(', ')}</span></span>
                      )}
                      {lastQuery.years && (
                        <span className="px-3 py-1 bg-gray-100 rounded-full">Kinh nghiệm: <span className="font-medium">{lastQuery.years}</span></span>
                      )}
                      {lastQuery.summary && (
                        <span className="px-3 py-1 bg-gray-100 rounded-full">Tóm tắt: <span className="font-medium">{lastQuery.summary}</span></span>
                      )}
                    </div>
                  </div>
                )}
              </div>}

              {/* Manual Input Section - Only show in manual mode */}
              {inputMode === "manual" && <>
              <div>
                <FieldLabel>Vị trí mong muốn</FieldLabel>
                <input
                  type="text"
                  name="position"
                  value={form.position}
                  onChange={onChange}
                  placeholder="VD: Senior Frontend Developer"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 transition"
                />
              </div>

              <div>
                <FieldLabel>Kỹ năng</FieldLabel>
                <input
                  type="text"
                  name="skills"
                  value={form.skills}
                  onChange={onChange}
                  placeholder="VD: React, TypeScript, Node.js"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 transition"
                />
              </div>

              <div>
                <FieldLabel>Số năm kinh nghiệm</FieldLabel>
                <input
                  type="text"
                  name="years"
                  value={form.years}
                  onChange={onChange}
                  placeholder="VD: 3 năm"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 transition"
                />
              </div>

              <div>
                <FieldLabel>Mô tả bản thân</FieldLabel>
                <textarea
                  name="summary"
                  value={form.summary}
                  onChange={onChange}
                  rows={5}
                  placeholder="Mô tả kinh nghiệm làm việc, dự án đã tham gia, thành tích..."
                  className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 transition resize-y"
                />
              </div>
              </>}

              <button
                type="submit"
                className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gray-900 text-white py-3 font-medium hover:bg-black transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                {inputMode === "cv" ? "Scan CV & Tìm việc" : "Tìm công việc phù hợp"}
              </button>
            </form>
          </div>

          {/* Right: Results */}
          <div className="space-y-4">
            {isLoading ? (
              <div className="bg-white rounded-2xl shadow-sm p-8 flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-indigo-600 mb-4"></div>
                  <div className="text-gray-600 font-medium">Đang tìm kiếm công việc phù hợp...</div>
                </div>
              </div>
            ) : results ? (
              <>
                <div className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">Công việc phù hợp ({results.length})</h2>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Sắp xếp theo độ phù hợp</span>
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                {lastQuery && (
                  <div className="bg-white rounded-xl shadow-sm p-4">
                    <div className="text-sm text-gray-700 font-medium mb-2">Thông tin tìm kiếm</div>
                    {lastQuery.mode === "manual" ? (
                      <div className="flex flex-wrap gap-2 text-sm">
                        {lastQuery.position && (
                          <span className="px-3 py-1 bg-gray-100 rounded-full">Vị trí: <span className="font-medium">{lastQuery.position}</span></span>
                        )}
                        {Array.isArray(lastQuery.skills) && lastQuery.skills.length > 0 && (
                          <span className="px-3 py-1 bg-gray-100 rounded-full">Kỹ năng: <span className="font-medium">{lastQuery.skills.join(', ')}</span></span>
                        )}
                        {lastQuery.years && (
                          <span className="px-3 py-1 bg-gray-100 rounded-full">Kinh nghiệm: <span className="font-medium">{lastQuery.years}</span></span>
                        )}
                        {lastQuery.summary && (
                          <span className="px-3 py-1 bg-gray-100 rounded-full">Tóm tắt: <span className="font-medium">{lastQuery.summary}</span></span>
                        )}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-600">Nguồn: CV ({lastQuery.fileName})</div>
                    )}
                  </div>
                )}
                <div className="space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
                  {results.map((job) => (
                    <JobCard key={job.id} job={job} />
                  ))}
                </div>
              </>
            ) : (
              <div className="bg-white rounded-2xl shadow-sm p-8 flex items-center justify-center min-h-[400px]">
                <div className="text-center text-gray-400 max-w-sm">
                  <svg className="w-24 h-24 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <div className="font-medium text-gray-600 text-lg mb-2">Chưa có kết quả tìm kiếm</div>
                  <div className="text-sm text-gray-500">Vui lòng nhập thông tin để bắt đầu tìm kiếm công việc phù hợp</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
