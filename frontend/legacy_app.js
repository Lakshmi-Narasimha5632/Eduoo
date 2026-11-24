const API_BASE = 'http://localhost:8000/api';
const { useEffect, useMemo, useState } = React;

const tabs = [
  'dashboard',
  'tasks',
  'progress',
  'analytics',
  'resume',
  'recommendations',
  'insights',
  'interview',
  'ai',
];

function getErrorMessage(data, fallback) {
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (data.error && typeof data.error === 'string') return data.error;
  if (data.error && data.error.message) return data.error.message;
  if (data.errors) {
    const first = Object.values(data.errors)[0];
    if (Array.isArray(first)) return first[0];
    if (typeof first === 'string') return first;
  }
  return fallback;
}

function App() {
  const [mode, setMode] = useState('login');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [form, setForm] = useState({
    email: 'demo@eduoo.local',
    username: 'demo',
    password: 'StrongPass123!',
    password_confirm: 'StrongPass123!',
  });
  const [token, setToken] = useState(localStorage.getItem('eduoo_token') || '');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('eduoo_user') || 'null'));
  const [dashboard, setDashboard] = useState(null);
  const [tasks, setTasks] = useState({ tasks: [] });
  const [progress, setProgress] = useState(null);
  const [weeklyProgress, setWeeklyProgress] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [insights, setInsights] = useState([]);
  const [resume, setResume] = useState(null);
  const [skillGaps, setSkillGaps] = useState(null);
  const [mockInterview, setMockInterview] = useState({ questions: [] });
  const [mockAnswer, setMockAnswer] = useState('');
  const [selectedQuestion, setSelectedQuestion] = useState('');
  const [mockResult, setMockResult] = useState(null);
  const [aiPrompt, setAiPrompt] = useState('Assess my current readiness for a backend engineer role.');
  const [aiContext, setAiContext] = useState('I have completed multiple coding problems, built a few projects, and want stronger system design communication.');
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const authHeader = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  async function apiRequest(path, options = {}) {
    const headers = {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...authHeader,
      ...(options.headers || {}),
    };

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await response.json() : {};

    if (!response.ok) {
      throw new Error(getErrorMessage(data, 'Request failed'));
    }

    return data;
  }

  async function refreshData() {
    if (!token) return;

    try {
      const [dashboardData, tasksData, progressData, weeklyData, analyticsData, recommendationsData, insightsData, resumeData, skillGapData, interviewData, aiData] = await Promise.all([
        apiRequest('/dashboard/'),
        apiRequest('/tasks/today/'),
        apiRequest('/progress/'),
        apiRequest('/progress/weekly/'),
        apiRequest('/analytics/'),
        apiRequest('/recommendations/'),
        apiRequest('/insights/'),
        apiRequest('/resume/'),
        apiRequest('/skill-gaps/'),
        apiRequest('/mock-interviews/'),
        apiRequest('/ai-evaluation/'),
      ]);

      setDashboard(dashboardData);
      setTasks(tasksData.plan || { tasks: [] });
      setProgress(progressData);
      setWeeklyProgress(weeklyData);
      setAnalytics(analyticsData);
      setRecommendations(recommendationsData.recommendations || []);
      setInsights(insightsData.insights || []);
      setResume(resumeData);
      setSkillGaps(skillGapData);
      setMockInterview(interviewData);
      setSelectedQuestion(interviewData.questions?.[0] || '');
      setAiResult(aiData);
      setError('');
    } catch (err) {
      setError(err.message || 'Unable to load app data.');
    }
  }

  useEffect(() => {
    if (!token || !user) {
      setDashboard(null);
      return;
    }

    refreshData();
  }, [token, user]);

  async function handleAuth(e) {
    e.preventDefault();
    setLoading(true);
    setError('');

    const endpoint = mode === 'login' ? '/auth/login/' : '/auth/register/';
    const payload = mode === 'login'
      ? { email: form.email, password: form.password }
      : {
          email: form.email,
          username: form.username,
          password: form.password,
          password_confirm: form.password_confirm || form.password,
        };

    try {
      const data = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).then(async (res) => {
        const json = await res.json();
        if (!res.ok) {
          throw new Error(getErrorMessage(json, 'Authentication failed.'));
        }
        return json;
      });

      const nextToken = data.access;
      const nextUser = data.user;

      setToken(nextToken);
      setUser(nextUser);
      localStorage.setItem('eduoo_token', nextToken);
      localStorage.setItem('eduoo_user', JSON.stringify(nextUser));
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  }

  async function completeTask(taskId) {
    try {
      await apiRequest(`/tasks/${taskId}/complete/`, { method: 'POST' });
      await refreshData();
    } catch (err) {
      setError(err.message || 'Unable to complete task.');
    }
  }

  async function submitMockInterview() {
    if (!mockAnswer.trim()) {
      setError('Answer is required before submitting.');
      return;
    }

    try {
      const result = await apiRequest('/mock-interviews/', {
        method: 'POST',
        body: JSON.stringify({ question: selectedQuestion, answer: mockAnswer }),
      });
      setMockResult(result);
      setMockAnswer('');
      await refreshData();
    } catch (err) {
      setError(err.message || 'Unable to submit interview answer.');
    }
  }

  async function submitAiEvaluation() {
    try {
      const result = await apiRequest('/ai-evaluation/', {
        method: 'POST',
        body: JSON.stringify({ prompt: aiPrompt, context: aiContext }),
      });
      setAiResult(result);
    } catch (err) {
      setError(err.message || 'Unable to generate AI evaluation.');
    }
  }

  function handleLogout() {
    setToken('');
    setUser(null);
    setDashboard(null);
    setTasks({ tasks: [] });
    setProgress(null);
    setAnalytics(null);
    setRecommendations([]);
    setInsights([]);
    setResume(null);
    setSkillGaps(null);
    setMockInterview({ questions: [] });
    setMockResult(null);
    setAiResult(null);
    localStorage.removeItem('eduoo_token');
    localStorage.removeItem('eduoo_user');
  }

  const greeting = user ? (user.full_name || user.username || user.email.split('@')[0]) : 'Student';

  if (!token || !user) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="brand-badge">Eduoo</div>
          <div className="auth-toggle">
            <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')} type="button">Login</button>
            <button className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')} type="button">Register</button>
          </div>

          {error && <div className="error-box">{error}</div>}

          <form onSubmit={handleAuth} className="auth-form">
            {mode === 'register' && (
              <div className="field-group">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  placeholder="yourname"
                />
              </div>
            )}

            <div className="field-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="you@example.com"
              />
            </div>

            <div className="field-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder="Password"
              />
            </div>

            {mode === 'register' && (
              <div className="field-group">
                <label htmlFor="password_confirm">Confirm password</label>
                <input
                  id="password_confirm"
                  type="password"
                  value={form.password_confirm}
                  onChange={(e) => setForm({ ...form, password_confirm: e.target.value })}
                  placeholder="Confirm password"
                />
              </div>
            )}

            <button className="primary-btn wide" type="submit" disabled={loading}>
              {loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <div className="helper-box">
            Demo login: <strong>demo@eduoo.local</strong> / <strong>StrongPass123!</strong>
          </div>
        </div>
      </div>
    );
  }

  const renderDashboard = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Overview</div>
          <h1>Welcome back, {greeting}</h1>
        </div>
        <button className="secondary-btn" onClick={refreshData} type="button">Refresh</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Target role</span>
          <strong>{dashboard?.overview?.target_role || 'Not set'}</strong>
        </div>
        <div className="stat-card">
          <span className="stat-label">Daily hours</span>
          <strong>{dashboard?.overview?.daily_study_hours ?? 0}h</strong>
        </div>
        <div className="stat-card">
          <span className="stat-label">Recommendations</span>
          <strong>{dashboard?.overview?.active_recommendations ?? 0}</strong>
        </div>
        <div className="stat-card">
          <span className="stat-label">Insights</span>
          <strong>{dashboard?.overview?.active_insights ?? 0}</strong>
        </div>
      </div>

      <div className="panel-grid two-col">
        <div className="panel-card">
          <div className="panel-header">
            <h3>Today’s plan</h3>
            <span className="chip success">{dashboard?.daily_plan?.status || 'planned'}</span>
          </div>
          <div className="plan-block">
            <div className="big-label">{dashboard?.daily_plan?.date || 'No date set'}</div>
            <div className="muted-row">
              <span>{dashboard?.daily_plan?.completed_minutes || 0} / {dashboard?.daily_plan?.total_minutes || 0} minutes</span>
            </div>
          </div>
        </div>

        <div className="panel-card">
          <div className="panel-header">
            <h3>Quick summary</h3>
          </div>
          <ul className="mini-list">
            <li><span>Total plans</span><strong>{dashboard?.overview?.total_plans ?? 0}</strong></li>
            <li><span>Recommendations</span><strong>{dashboard?.overview?.active_recommendations ?? 0}</strong></li>
            <li><span>Insights</span><strong>{dashboard?.overview?.active_insights ?? 0}</strong></li>
          </ul>
        </div>
      </div>

      <div className="panel-grid two-col">
        <div className="panel-card">
          <div className="panel-header">
            <h3>Priority recommendations</h3>
          </div>
          <div className="stack-list">
            {(dashboard?.recommendations || []).map((item) => (
              <div className="list-item" key={item.id}>
                <span className="chip">{item.category}</span>
                <h4>{item.title}</h4>
                <p>{item.action}</p>
              </div>
            )) || <p className="muted">No recommendations yet.</p>}
          </div>
        </div>

        <div className="panel-card">
          <div className="panel-header">
            <h3>Latest insight</h3>
          </div>
          <div className="stack-list">
            {(dashboard?.insights || []).map((item) => (
              <div className="list-item" key={item.id}>
                <span className="chip">{item.type}</span>
                <h4>{item.title}</h4>
                <p>{item.message}</p>
              </div>
            )) || <p className="muted">No insights yet.</p>}
          </div>
        </div>
      </div>
    </div>
  );

  const renderTasks = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Your plan</div>
          <h1>Daily tasks</h1>
        </div>
      </div>

      <div className="panel-card">
        <div className="panel-header">
          <h3>{tasks?.date || 'Today'}</h3>
          <span className="chip">{tasks?.status || 'planned'}</span>
        </div>
        <div className="tasks-list">
          {(tasks?.tasks || []).map((task) => (
            <div className="task-row" key={task.id}>
              <div>
                <div className="task-title">{task.title}</div>
                <div className="task-meta">{task.task_type} • {task.difficulty || 'General'} • {task.estimated_minutes} min</div>
              </div>
              <div className="task-actions">
                <span className={`priority ${task.priority}`}>{task.priority}</span>
                {task.status !== 'completed' ? (
                  <button className="primary-btn small" onClick={() => completeTask(task.id)} type="button">Mark done</button>
                ) : (
                  <span className="done-pill">Done</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderProgress = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Progress</div>
          <h1>Momentum overview</h1>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card"><span className="stat-label">Current streak</span><strong>{progress?.current_streak ?? 0} days</strong></div>
        <div className="stat-card"><span className="stat-label">Longest streak</span><strong>{progress?.longest_streak ?? 0} days</strong></div>
        <div className="stat-card"><span className="stat-label">Tasks completed</span><strong>{progress?.total_tasks_completed ?? 0}</strong></div>
        <div className="stat-card"><span className="stat-label">Study minutes</span><strong>{progress?.total_study_minutes ?? 0}</strong></div>
      </div>

      <div className="panel-card">
        <div className="panel-header">
          <h3>Weekly progress</h3>
        </div>
        <div className="weekly-chart">
          {(weeklyProgress?.daily || []).map((day) => (
            <div className="bar-col" key={day.date}>
              <div className="bar" style={{ height: `${Math.max(10, (day.study_minutes / Math.max(1, Math.max(...(weeklyProgress?.daily || []).map((item) => item.study_minutes))) || 1) * 100)}%` }}></div>
              <span>{day.date.slice(5)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Performance</div>
          <h1>Analytics</h1>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card"><span className="stat-label">Completed tasks</span><strong>{analytics?.overview?.total_tasks_completed ?? 0}</strong></div>
        <div className="stat-card"><span className="stat-label">Study minutes</span><strong>{analytics?.overview?.total_study_minutes ?? 0}</strong></div>
        <div className="stat-card"><span className="stat-label">Platforms</span><strong>{analytics?.overview?.active_platforms ?? 0}</strong></div>
        <div className="stat-card"><span className="stat-label">Daily target</span><strong>{analytics?.overview?.daily_target_hours ?? 0}h</strong></div>
      </div>

      <div className="panel-card">
        <div className="panel-header">
          <h3>Connected platforms</h3>
        </div>
        <div className="platform-grid">
          {(analytics?.platforms || []).map((platform) => (
            <div className="platform-card" key={platform.platform}>
              <div className="platform-name">{platform.display_name}</div>
              <div className={`platform-state ${platform.connected ? 'on' : 'off'}`}>{platform.connected ? 'Connected' : 'Not connected'}</div>
              <div className="platform-user">{platform.username || 'Not linked'}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderResume = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Career</div>
          <h1>Resume snapshot</h1>
        </div>
      </div>

      <div className="panel-grid two-col">
        <div className="panel-card">
          <div className="panel-header"><h3>Profile</h3></div>
          <div className="profile-grid">
            <div><span>Name</span><strong>{resume?.profile?.full_name || user.full_name || user.username}</strong></div>
            <div><span>Email</span><strong>{resume?.profile?.email || user.email}</strong></div>
            <div><span>Target role</span><strong>{resume?.profile?.target_role || 'Not set'}</strong></div>
            <div><span>College</span><strong>{resume?.profile?.college || 'Not provided'}</strong></div>
            <div><span>Branch</span><strong>{resume?.profile?.branch || 'Not provided'}</strong></div>
            <div><span>Experience</span><strong>{resume?.profile?.experience_level || 'Not set'}</strong></div>
          </div>
          <p className="bio-text">{resume?.profile?.bio || 'Add a bio to highlight your work and goals.'}</p>
        </div>

        <div className="panel-card">
          <div className="panel-header"><h3>Strengths</h3></div>
          <ul className="bullet-list">
            {(resume?.strengths || []).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </div>

      <div className="panel-card">
        <div className="panel-header"><h3>Skill gaps</h3></div>
        <ul className="bullet-list">
          {(resume?.skill_gaps || []).map((item) => <li key={item}>{item}</li>)}
        </ul>
      </div>
    </div>
  );

  const renderRecommendations = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Guidance</div>
          <h1>Recommendations</h1>
        </div>
      </div>

      <div className="stack-list large-gap">
        {recommendations.map((item) => (
          <div className="list-item" key={item.id}>
            <span className="chip">{item.category}</span>
            <h4>{item.title}</h4>
            <p>{item.description}</p>
            <small>{item.action}</small>
          </div>
        ))}
      </div>
    </div>
  );

  const renderInsights = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Signals</div>
          <h1>Insights</h1>
        </div>
      </div>

      <div className="stack-list large-gap">
        {insights.map((item) => (
          <div className="list-item" key={item.id}>
            <span className="chip">{item.type}</span>
            <h4>{item.title}</h4>
            <p>{item.message}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const renderInterview = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">Practice</div>
          <h1>Mock interviews</h1>
        </div>
      </div>

      <div className="panel-card">
        <div className="panel-header">
          <h3>Question</h3>
        </div>
        <select className="select-input" value={selectedQuestion} onChange={(e) => setSelectedQuestion(e.target.value)}>
          {(mockInterview.questions || []).map((question) => (
            <option key={question} value={question}>{question}</option>
          ))}
        </select>
        <textarea className="text-area" value={mockAnswer} onChange={(e) => setMockAnswer(e.target.value)} placeholder="Write your interview answer here..." />
        <button className="primary-btn" onClick={submitMockInterview} type="button">Submit answer</button>
      </div>

      {mockResult && (
        <div className="panel-card result-card">
          <div className="panel-header">
            <h3>Feedback</h3>
            <span className="chip success">Score: {mockResult.score}</span>
          </div>
          <p>{mockResult.feedback}</p>
        </div>
      )}
    </div>
  );

  const renderAi = () => (
    <div className="content-stack">
      <div className="header-row">
        <div>
          <div className="eyebrow">AI evaluation</div>
          <h1>Interview readiness check</h1>
        </div>
      </div>

      <div className="panel-card">
        <label className="label-style">Prompt</label>
        <textarea className="text-area small" value={aiPrompt} onChange={(e) => setAiPrompt(e.target.value)} />
        <label className="label-style">Context</label>
        <textarea className="text-area small" value={aiContext} onChange={(e) => setAiContext(e.target.value)} />
        <button className="primary-btn" onClick={submitAiEvaluation} type="button">Generate feedback</button>
      </div>

      {aiResult && (
        <div className="panel-card result-card">
          <div className="panel-header">
            <h3>AI summary</h3>
            <span className="chip success">Score: {aiResult.overall_score}</span>
          </div>
          <p>{aiResult.summary}</p>
          <div className="list-columns">
            <div>
              <h4>Strengths</h4>
              <ul className="bullet-list compact">
                {(aiResult.strengths || []).map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
            <div>
              <h4>Areas to improve</h4>
              <ul className="bullet-list compact">
                {(aiResult.improvement_areas || []).map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  function renderTabContent() {
    switch (activeTab) {
      case 'dashboard': return renderDashboard();
      case 'tasks': return renderTasks();
      case 'progress': return renderProgress();
      case 'analytics': return renderAnalytics();
      case 'resume': return renderResume();
      case 'recommendations': return renderRecommendations();
      case 'insights': return renderInsights();
      case 'interview': return renderInterview();
      case 'ai': return renderAi();
      default: return renderDashboard();
    }
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">E</div>
          <div>
            <div className="brand-name">Eduoo</div>
            <small>Learning OS</small>
          </div>
        </div>

        <nav className="nav-menu">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={activeTab === tab ? 'nav-item active' : 'nav-item'}
              onClick={() => setActiveTab(tab)}
              type="button"
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1).replace(/([A-Z])/g, ' $1')}
            </button>
          ))}
        </nav>

        <div className="profile-card">
          <div className="mini-avatar">{greeting.charAt(0).toUpperCase()}</div>
          <div>
            <strong>{greeting}</strong>
            <small>{user.email}</small>
          </div>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar-main">
          <div>
            <div className="eyebrow">Growth dashboard</div>
            <h2>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1).replace(/([A-Z])/g, ' $1')}</h2>
          </div>
          <button className="ghost-btn" onClick={handleLogout} type="button">Logout</button>
        </header>

        {error && <div className="error-box">{error}</div>}
        {renderTabContent()}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
