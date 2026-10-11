/**
 * SkillPulse Bharat - Main Application Controller
 * Team: Syntax Society
 */

const API_BASE = window.location.origin;

const DEFAULT_ROLES = [
  "Data Scientist",
  "Data Analyst",
  "AI/ML Engineer",
  "Python Developer",
  "Software Developer",
  "Cloud/DevOps Architect",
  "Fullstack Developer",
  "Cybersecurity Analyst"
];

// State
let allSkillsList = [];
let allRolesList = [...DEFAULT_ROLES];
let currentSkill = 'Python';
let currentRole = 'Data Scientist';
let userSelectedSkills = ['Python', 'SQL', 'Git'];

// Each signed-in audience receives a deliberately focused workspace. Guests can
// explore every public feature; these rules shape the product after login.
const ROLE_WORKSPACES = {
  student: {
    label: 'Student workspace',
    note: 'Student workspace · Profile fit & learning roadmaps',
    defaultView: 'recommend',
    views: ['home', 'dashboard', 'skills', 'career', 'emerging', 'recommend', 'nlp', 'about'],
    navLabels: { dashboard: 'Market Dashboard', skills: 'Skill Search', career: 'Career Explorer', emerging: 'Emerging Skills', recommend: 'My Roadmap', nlp: 'Job Analyzer', about: 'Methodology' },
    hero: { title: 'Make your next<br>move <em>count.</em>', intro: 'Upload your resume, choose a target role, and get a focused view of the skills that will make the biggest difference.', primary: 'Analyse my profile', primaryView: 'recommend', secondary: 'Explore the market', secondaryView: 'dashboard' },
    cards: [
      ['01 / EXPLORE', 'Understand the<br>market.', 'See demand, salary context and role coverage across the skills employers use today.', 'Open dashboard', 'dashboard'],
      ['02 / ASSESS', 'See your<br>starting point.', 'Bring in your resume or add skills yourself. AROHA turns them into a usable profile.', 'Import resume', 'recommend'],
      ['03 / ACT', 'Learn with<br>purpose.', 'Identify the gaps that matter for your target role and build a focused learning roadmap.', 'Create roadmap', 'recommend']
    ]
  },
  recruiter: {
    label: 'Recruiter workspace',
    note: 'Recruiter workspace · Talent demand & role benchmarks',
    defaultView: 'dashboard',
    views: ['home', 'dashboard', 'skills', 'career', 'emerging', 'nlp', 'about'],
    navLabels: { dashboard: 'Talent Market', skills: 'Skill Demand', career: 'Role Benchmarks', emerging: 'Demand Radar', nlp: 'JD Analyzer', about: 'Methodology' },
    hero: { title: 'Find the talent<br>signals that <em>matter.</em>', intro: 'Compare demand, role coverage, and market momentum to make sharper hiring decisions.', primary: 'Explore talent demand', primaryView: 'dashboard', secondary: 'Compare role benchmarks', secondaryView: 'career' },
    cards: [
      ['01 / SCAN', 'Read the<br>talent market.', 'Track the skills, locations, and hiring signals moving across the Indian technology market.', 'Open talent market', 'dashboard'],
      ['02 / COMPARE', 'Benchmark<br>critical roles.', 'Compare in-demand roles, salary bands, and the capabilities your hiring plan needs.', 'View role benchmarks', 'career'],
      ['03 / ANTICIPATE', 'Plan for<br>what is next.', 'Spot emerging demand before it becomes a hiring bottleneck for your team.', 'Open demand radar', 'emerging']
    ]
  },
  other: {
    label: 'Educator workspace',
    note: 'Educator workspace · Curriculum alignment & future skills',
    defaultView: 'emerging',
    views: ['home', 'dashboard', 'skills', 'career', 'emerging', 'about'],
    navLabels: { dashboard: 'Workforce Signals', skills: 'Skill Trends', career: 'Curriculum Alignment', emerging: 'Future Skills', about: 'Data & Methodology' },
    hero: { title: 'Shape learning for<br>what comes <em>next.</em>', intro: 'Connect curriculum choices with real market demand, changing role needs, and future-ready skill signals.', primary: 'Review curriculum signals', primaryView: 'career', secondary: 'Track future skills', secondaryView: 'emerging' },
    cards: [
      ['01 / OBSERVE', 'See the<br>skills shifting.', 'Follow market signals and fast-growing capabilities across technology domains.', 'Open workforce signals', 'dashboard'],
      ['02 / ALIGN', 'Connect learning<br>to outcomes.', 'Use role requirements to examine where curriculum and employment needs meet.', 'Explore role alignment', 'career'],
      ['03 / PREPARE', 'Plan for<br>future skills.', 'Turn emerging-skill momentum into clearer curriculum and program priorities.', 'View future skills', 'emerging']
    ]
  }
};

const GUEST_WORKSPACE = {
  note: 'Guest workspace · Explore AROHA',
  views: ['home', 'dashboard', 'skills', 'career', 'emerging', 'recommend', 'nlp', 'about'],
  navLabels: { dashboard: 'Dashboard', skills: 'Skill Search', career: 'Career Explorer', emerging: 'Emerging Skills', recommend: 'Recommendations', nlp: 'NLP Job Analyzer', about: 'About & Methodology' },
  hero: { title: 'Make your next<br>move <em>count.</em>', intro: 'Upload your resume, choose a target role, and get a clear, evidence-based view of the skills that will make the biggest difference.', primary: 'Analyse my profile', primaryView: 'recommend', secondary: 'Explore the market', secondaryView: 'dashboard' },
  cards: ROLE_WORKSPACES.student.cards
};

function getRoleWorkspace() {
  return currentUser ? (ROLE_WORKSPACES[currentUser.role] || ROLE_WORKSPACES.student) : GUEST_WORKSPACE;
}

function getRoleDefaultView() {
  return getRoleWorkspace().defaultView || 'dashboard';
}

function applyRoleExperience() {
  const workspace = getRoleWorkspace();
  const note = document.getElementById('role-workspace-note');
  if (note) {
    note.innerText = workspace.note;
    note.style.display = currentUser ? 'block' : 'none';
  }

  document.querySelectorAll('.nav-item').forEach(item => {
    const view = item.getAttribute('data-view');
    const isVisible = workspace.views.includes(view);
    item.classList.toggle('role-hidden', !isVisible);
    item.setAttribute('aria-hidden', String(!isVisible));
    const label = item.querySelector('span:last-child');
    if (label && workspace.navLabels[view]) label.innerText = workspace.navLabels[view];
  });

  const title = document.getElementById('home-hero-title');
  const intro = document.getElementById('home-intro');
  const primary = document.getElementById('home-primary-action');
  const secondary = document.getElementById('home-secondary-action');
  if (title) title.innerHTML = workspace.hero.title;
  if (intro) intro.innerText = workspace.hero.intro;
  if (primary) {
    primary.innerHTML = `${workspace.hero.primary} <span>↗</span>`;
    primary.onclick = () => switchView(workspace.hero.primaryView);
  }
  if (secondary) {
    secondary.innerHTML = `${workspace.hero.secondary} <span>→</span>`;
    secondary.onclick = () => switchView(workspace.hero.secondaryView);
  }

  workspace.cards.forEach((card, index) => {
    const number = index + 1;
    const [kicker, cardTitle, copy, action, target] = card;
    const kickerEl = document.getElementById(`home-card-kicker-${number}`);
    const titleEl = document.getElementById(`home-card-title-${number}`);
    const copyEl = document.getElementById(`home-card-copy-${number}`);
    const actionEl = document.getElementById(`home-card-action-${number}`);
    if (kickerEl) kickerEl.innerText = kicker;
    if (titleEl) titleEl.innerHTML = cardTitle;
    if (copyEl) copyEl.innerText = copy;
    if (actionEl) {
      actionEl.innerHTML = `${action} <b>↗</b>`;
      actionEl.onclick = () => switchView(target);
    }
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  setupQuickChips();
  setupNLPPlayground();
  setupRecommendationControls();
  setupResumeUpload();
  
  // Initialize Authentication System
  await initAuthSystem();

  // Initial loads
  await loadDashboard();
  await loadSkillsList();
  await loadRolesList();
  await loadEmergingSkills();
  
  // Pre-load default views
  searchSkill('Python');
  loadRoleDetail('Data Scientist');
  runRecommendationAnalysis();
});

// ----------------- Navigation ----------------- //

function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetView = item.getAttribute('data-view');
      switchView(targetView);
    });
  });
}

function switchView(viewId) {
  const workspace = getRoleWorkspace();
  const requestedSection = document.getElementById(`view-${viewId}`);
  if (!requestedSection) return;

  // A role cannot reach a workspace feature that is intentionally hidden,
  // including through a home-page button or a stale browser action.
  if (currentUser && viewId !== 'auth' && !workspace.views.includes(viewId)) {
    viewId = getRoleDefaultView();
  }

  // Update sidebar active state
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('data-view') === viewId) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Switch view section visibility
  document.querySelectorAll('.view-section').forEach(sec => {
    if (sec.id === `view-${viewId}`) {
      sec.classList.add('active');
    } else {
      sec.classList.remove('active');
    }
  });

  // Scroll content to top
  const scrollContainer = document.querySelector('.content-scroll');
  if (scrollContainer) scrollContainer.scrollTop = 0;
}

// ----------------- Dashboard ----------------- //

async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard`);
    const data = await res.json();

    document.getElementById('kpi-total-jobs').innerText = data.total_jobs_analyzed.toLocaleString();
    document.getElementById('kpi-total-skills').innerText = data.total_skills_identified;
    
    // Fastest growing skill highlight
    if (data.fastest_growing_skills && data.fastest_growing_skills.length > 0) {
      const topGrow = data.fastest_growing_skills[0];
      document.getElementById('kpi-top-growth-name').innerText = topGrow.skill_name;
      document.getElementById('kpi-top-growth-pct').innerText = `+${topGrow.growth_rate_pct}% YoY`;
    }

    // Render charts
    renderTopSkillsChart('chart-top-skills', data.top_skills);
    renderIndustrySpreadChart('chart-industries', data.industries);

    // Render top in-demand skills table / badges
    const topSkillsContainer = document.getElementById('dashboard-top-skills-list');
    if (topSkillsContainer) {
      topSkillsContainer.innerHTML = data.top_skills.slice(0, 8).map(s => `
        <div class="skill-tag core" style="cursor: pointer;" onclick="inspectSkillFromDashboard('${s.skill}')">
          <strong>${s.skill}</strong>
          <span style="opacity: 0.8; font-size: 0.75rem;">${s.percentage}%</span>
        </div>
      `).join('');
    }

  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

function inspectSkillFromDashboard(skillName) {
  switchView('skills');
  searchSkill(skillName);
}

// ----------------- Skill Intelligence Search ----------------- //

async function loadSkillsList() {
  try {
    const res = await fetch(`${API_BASE}/api/skills`);
    const data = await res.json();
    allSkillsList = data.skills;

    // Populate datalist for auto-complete
    const datalist = document.getElementById('skills-datalist');
    if (datalist) {
      datalist.innerHTML = allSkillsList.map(s => `<option value="${s}">`).join('');
    }
  } catch (err) {
    console.error('Failed to load skills list:', err);
  }
}

function setupQuickChips() {
  const chips = document.querySelectorAll('.quick-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const skill = chip.getAttribute('data-skill');
      document.getElementById('skill-search-input').value = skill;
      searchSkill(skill);
    });
  });

  const searchInput = document.getElementById('skill-search-input');
  if (searchInput) {
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = searchInput.value.trim();
        if (query) searchSkill(query);
      }
    });
  }
}

async function searchSkill(skillName) {
  currentSkill = skillName;
  const loadingIndicator = document.getElementById('skill-detail-loading');
  const contentContainer = document.getElementById('skill-detail-content');

  if (loadingIndicator) loadingIndicator.style.display = 'block';
  if (contentContainer) contentContainer.style.display = 'none';

  try {
    const res = await fetch(`${API_BASE}/api/skills/${encodeURIComponent(skillName)}`);
    if (!res.ok) {
      alert(`Skill "${skillName}" not found in current dataset. Try Python, SQL, AWS, Docker, React, or Generative AI.`);
      if (loadingIndicator) loadingIndicator.style.display = 'none';
      return;
    }
    const data = await res.json();

    // Populate skill detail elements
    document.getElementById('skill-name-header').innerText = data.skill_name;
    document.getElementById('skill-cat-header').innerText = data.category;
    document.getElementById('skill-demand-score').innerText = `${data.demand_score}/100`;
    document.getElementById('skill-jobs-count').innerText = `${data.total_jobs} Postings (${data.demand_percentage}%)`;
    document.getElementById('skill-momentum-tag').innerText = data.momentum;
    document.getElementById('skill-growth-rate').innerText = `+${data.annual_cagr_projection}% Annual CAGR`;
    document.getElementById('skill-verdict-text').innerText = data.verdict;

    // Related skills
    const relatedContainer = document.getElementById('skill-related-tags');
    if (relatedContainer) {
      relatedContainer.innerHTML = data.related_skills.map(r => `
        <span class="skill-tag" style="cursor: pointer;" onclick="searchSkill('${r.skill}')">
          ${r.skill} <span style="color: #6366f1; font-weight: 700;">${Math.round(r.correlation * 100)}% corr</span>
        </span>
      `).join('');
    }

    // Top industries for this skill
    const indContainer = document.getElementById('skill-industry-pills');
    if (indContainer) {
      indContainer.innerHTML = data.top_industries.map(ind => `
        <span class="skill-tag core">${ind.industry}: <strong>${ind.count} jobs</strong></span>
      `).join('');
    }

    // Render trend line chart (historical + forecast)
    renderSkillTrendChart('chart-skill-trend', data.historical_trend, data.forecast_trend);

    if (loadingIndicator) loadingIndicator.style.display = 'none';
    if (contentContainer) contentContainer.style.display = 'block';

  } catch (err) {
    console.error('Error fetching skill:', err);
    if (loadingIndicator) loadingIndicator.style.display = 'none';
  }
}

// ----------------- Career Explorer ----------------- //

function populateRoleSelectors() {
  const roleSelect = document.getElementById('role-selector');
  if (roleSelect) {
    const currentVal = roleSelect.value || currentRole || 'Data Scientist';
    roleSelect.innerHTML = allRolesList.map(r => `<option value="${r}">${r}</option>`).join('');
    if (allRolesList.includes(currentVal)) {
      roleSelect.value = currentVal;
    }
  }

  const recSelect = document.getElementById('rec-target-role');
  if (recSelect) {
    const currentVal = recSelect.value || 'Data Analyst';
    recSelect.innerHTML = allRolesList.map(r => `<option value="${r}">${r}</option>`).join('');
    if (allRolesList.includes(currentVal)) {
      recSelect.value = currentVal;
    }
    updateActiveRoleChip(recSelect.value);
  }

  const signupSelect = document.getElementById('signup-target-role');
  if (signupSelect) {
    const currentVal = signupSelect.value;
    signupSelect.innerHTML = allRolesList.map(r => `<option value="${r}">${r}</option>`).join('');
    if (currentVal && allRolesList.includes(currentVal)) {
      signupSelect.value = currentVal;
    }
  }
}

function updateActiveRoleChip(roleName) {
  document.querySelectorAll('#rec-role-chips-container .role-suggestion-chip').forEach(chip => {
    if (chip.getAttribute('data-role') === roleName) {
      chip.classList.add('active');
    } else {
      chip.classList.remove('active');
    }
  });
}

function selectTargetRoleSuggestion(roleName) {
  const recSelect = document.getElementById('rec-target-role');
  if (recSelect) {
    recSelect.value = roleName;
    updateActiveRoleChip(roleName);
    runRecommendationAnalysis();
  }
}

function selectCareerRoleSuggestion(roleName) {
  const roleSelect = document.getElementById('role-selector');
  if (roleSelect) {
    roleSelect.value = roleName;
    loadRoleDetail(roleName);
  }
}

async function loadRolesList() {
  try {
    const res = await fetch(`${API_BASE}/api/roles`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.roles) && data.roles.length > 0) {
        allRolesList = data.roles;
      }
    }
  } catch (err) {
    console.warn('Failed to load roles list from API, keeping default catalog:', err);
  } finally {
    populateRoleSelectors();
  }

  const select = document.getElementById('role-selector');
  if (select && !select.dataset.bound) {
    select.dataset.bound = 'true';
    select.addEventListener('change', (e) => loadRoleDetail(e.target.value));
  }
}

async function loadRoleDetail(roleName) {
  currentRole = roleName;
  try {
    const res = await fetch(`${API_BASE}/api/roles/${encodeURIComponent(roleName)}`);
    const data = await res.json();

    document.getElementById('role-title-display').innerText = data.role_name;
    document.getElementById('role-desc-display').innerText = data.description;
    document.getElementById('role-salary-display').innerText = `₹ ${data.avg_salary_lpa} LPA Avg`;
    document.getElementById('role-jobs-display').innerText = `${data.total_jobs} Active Postings`;

    // Core skills
    const coreContainer = document.getElementById('role-core-skills');
    if (coreContainer) {
      coreContainer.innerHTML = data.core_skills.map(s => `
        <div class="skill-tag core" style="cursor: pointer;" onclick="inspectSkillFromDashboard('${s.skill}')">
          ${s.skill} <span style="font-size: 0.74rem; opacity: 0.85;">(${s.percentage}%)</span>
        </div>
      `).join('');
    }

    // Complementary skills
    const compContainer = document.getElementById('role-comp-skills');
    if (compContainer) {
      compContainer.innerHTML = data.complementary_skills.map(s => `
        <div class="skill-tag" style="cursor: pointer;" onclick="inspectSkillFromDashboard('${s.skill}')">
          ${s.skill} <span style="font-size: 0.74rem; opacity: 0.85;">(${s.percentage}%)</span>
        </div>
      `).join('');
    }

    // Emerging skills
    const emergContainer = document.getElementById('role-emerging-skills');
    if (emergContainer) {
      emergContainer.innerHTML = data.emerging_skills.map(s => `
        <div class="skill-tag emerging" style="cursor: pointer;" onclick="inspectSkillFromDashboard('${s}')">
          ${s}
        </div>
      `).join('');
    }

    // Top locations
    const locContainer = document.getElementById('role-locations-list');
    if (locContainer) {
      locContainer.innerHTML = data.location_spread.map(l => `
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem;">
          <span style="color: #cbd5e1;">${l.location}</span>
          <span style="font-weight: 700; color: #a5b4fc;">${l.count} jobs</span>
        </div>
      `).join('');
    }

  } catch (err) {
    console.error('Failed to load role details:', err);
  }
}

// ----------------- Emerging Skills ----------------- //

async function loadEmergingSkills() {
  try {
    const res = await fetch(`${API_BASE}/api/emerging`);
    const data = await res.json();

    const grid = document.getElementById('emerging-skills-grid');
    if (!grid) return;

    grid.innerHTML = data.skills.map(item => `
      <div class="emerging-card">
        <div>
          <div class="emerging-card-top">
            <div>
              <h3 style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">${item.skill_name}</h3>
              <span style="font-size: 0.78rem; color: #06b6d4; font-weight: 600;">${item.adoption_stage}</span>
            </div>
            <span class="emerging-growth-pill">+${item.growth_rate_pct}% Demand Surge</span>
          </div>
          <p class="emerging-desc">${item.description}</p>
        </div>
        <div class="emerging-footer">
          <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span>Momentum Index: <strong>${item.momentum_score}/100</strong></span>
            <span style="color: #94a3b8;">${item.category}</span>
          </div>
          <p style="font-size: 0.75rem; color: #fde68a; font-style: italic;">Note: ${item.forecast_note}</p>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Failed to load emerging skills:', err);
  }
}

// ----------------- Skill Gap Recommendations ----------------- //

function setupRecommendationControls() {
  populateRoleSelectors();

  const targetSelect = document.getElementById('rec-target-role');
  if (targetSelect && !targetSelect.dataset.bound) {
    targetSelect.dataset.bound = 'true';
    targetSelect.addEventListener('change', (e) => {
      updateActiveRoleChip(e.target.value);
      runRecommendationAnalysis();
    });
  }

  renderSelectedUserSkillsChips();

  // Add skill input
  const addBtn = document.getElementById('btn-add-user-skill');
  const addInput = document.getElementById('input-add-user-skill');
  if (addBtn && addInput) {
    addBtn.addEventListener('click', () => {
      const val = addInput.value.trim();
      if (val && !userSelectedSkills.includes(val)) {
        userSelectedSkills.push(val);
        addInput.value = '';
        renderSelectedUserSkillsChips();
      }
    });
  }

  // Run button
  const analyzeBtn = document.getElementById('btn-run-recommendation');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', runRecommendationAnalysis);
  }
}

// ----------------- Resume Skill Import ----------------- //

function setupResumeUpload() {
  const input = document.getElementById('resume-upload-input');
  const dropzone = document.getElementById('resume-dropzone');
  if (!input || !dropzone) return;

  input.addEventListener('change', () => {
    const [file] = input.files;
    if (file) extractResumeSkills(file);
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, event => {
      event.preventDefault();
      dropzone.classList.add('is-dragging');
    });
  });
  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, event => {
      event.preventDefault();
      dropzone.classList.remove('is-dragging');
    });
  });
  dropzone.addEventListener('drop', event => {
    const [file] = event.dataTransfer.files;
    if (file) extractResumeSkills(file);
  });
}

async function extractResumeSkills(file) {
  const status = document.getElementById('resume-upload-status');
  const dropzone = document.getElementById('resume-dropzone');
  const allowed = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  const extension = file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(file.type) && !['pdf', 'docx', 'txt'].includes(extension)) {
    setResumeStatus('Please choose a PDF, DOCX, or TXT resume.', 'error');
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    setResumeStatus('Please upload a resume smaller than 5 MB.', 'error');
    return;
  }

  dropzone?.classList.add('is-processing');
  setResumeStatus(`Reading ${file.name} and mapping your skills…`, 'loading');
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE}/api/extract-resume`, { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Resume analysis failed.');

    userSelectedSkills = [...new Set([...userSelectedSkills, ...data.extracted_skills])];
    renderSelectedUserSkillsChips();
    const count = data.extracted_skills.length;
    setResumeStatus(
      count ? `${count} skills found and added to your profile. Your gap analysis has been refreshed.` : 'Your resume was read, but no indexed skills were found. Add skills manually below.',
      count ? 'success' : 'warning'
    );
    if (Array.isArray(data.top_matching_roles) && data.top_matching_roles.length > 0) {
      const suggContainer = document.getElementById('rec-role-suggestions');
      if (suggContainer) {
        suggContainer.innerHTML = `
          <span style="font-size: 0.75rem; color: #38bdf8; display: block; margin-bottom: 6px; font-weight: 600;">
            Suggested Roles from Resume:
          </span>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            ${data.top_matching_roles.slice(0, 4).map(r => `
              <button type="button" class="quick-chip" onclick="selectTargetRoleSuggestion('${r.role}')" style="border-color: #38bdf8; color: #ffffff;">
                ${r.role} <small style="color: #38bdf8; font-weight: 700;">(${r.match_percentage}%)</small>
              </button>
            `).join('')}
          </div>
        `;
      }
      const topRole = data.top_matching_roles[0].role;
      const recSelect = document.getElementById('rec-target-role');
      if (recSelect && allRolesList.includes(topRole)) {
        recSelect.value = topRole;
      }
    }

    if (count) runRecommendationAnalysis();
  } catch (error) {
    console.error('Resume extraction error:', error);
    setResumeStatus(error.message || 'We could not analyse that resume. Please try another file.', 'error');
  } finally {
    dropzone?.classList.remove('is-processing');
  }
}

function setResumeStatus(message, type) {
  const status = document.getElementById('resume-upload-status');
  if (!status) return;
  status.className = `resume-upload-status is-${type}`;
  status.textContent = message;
}

function renderSelectedUserSkillsChips() {
  const container = document.getElementById('user-skills-chips');
  if (!container) return;

  container.innerHTML = userSelectedSkills.map((s, idx) => `
    <span class="skill-tag" style="background-color: rgba(99, 102, 241, 0.2); border-color: #6366f1;">
      ${s} <span style="cursor: pointer; margin-left: 6px; font-weight: bold;" onclick="removeUserSkill(${idx})">×</span>
    </span>
  `).join('');
}

function removeUserSkill(index) {
  userSelectedSkills.splice(index, 1);
  renderSelectedUserSkillsChips();
}

async function runRecommendationAnalysis() {
  const roleSelect = document.getElementById('rec-target-role');
  const role = roleSelect ? roleSelect.value : 'Data Analyst';

  try {
    const res = await fetch(`${API_BASE}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_role: role,
        user_skills: userSelectedSkills,
        experience_level: 'Student/Fresher'
      })
    });

    const data = await res.json();

    // Fill match percentage
    document.getElementById('rec-match-score').innerText = `${data.match_percentage}%`;
    const badgeEl = document.getElementById('rec-readiness-badge');
    badgeEl.innerText = data.readiness_badge;
    badgeEl.style.color = data.readiness_color;

    // Missing core skills
    const missingCoreEl = document.getElementById('rec-missing-core');
    if (missingCoreEl) {
      if (data.missing_core_skills.length === 0) {
        missingCoreEl.innerHTML = '<span style="color: #10b981;">✓ All core competencies met!</span>';
      } else {
        missingCoreEl.innerHTML = data.missing_core_skills.map(s => `
          <span class="skill-tag" style="background-color: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.3); color: #fca5a5;">
            ! ${s}
          </span>
        `).join('');
      }
    }

    // Missing emerging skills
    const missingEmergEl = document.getElementById('rec-missing-emerging');
    if (missingEmergEl) {
      missingEmergEl.innerHTML = data.missing_emerging_skills.map(s => `
        <span class="skill-tag emerging">${s}</span>
      `).join('');
    }

    // Roadmap timeline
    const roadmapEl = document.getElementById('rec-roadmap-list');
    if (roadmapEl) {
      roadmapEl.innerHTML = data.learning_roadmap.map(step => {
        let badgeClass = 'impact';
        if (step.importance.includes('Core')) badgeClass = 'core';
        if (step.importance.includes('Edge')) badgeClass = 'edge';

        const resourcesHtml = step.recommended_resources.map(r => `
          <span class="resource-pill">${r}</span>
        `).join('');

        return `
          <div class="roadmap-step">
            <div class="step-number-bubble">${step.step_number}</div>
            <div class="step-content">
              <div class="step-header">
                <span class="step-skill-title">${step.skill}</span>
                <span class="step-importance-badge ${badgeClass}">${step.importance} (~${step.estimated_weeks} weeks)</span>
              </div>
              <p class="step-why">${step.why_needed}</p>
              <div class="step-resources">${resourcesHtml}</div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Render Radar Chart
    const summary = data.skill_gap_summary;
    renderSkillGapRadarChart('chart-skill-gap-radar', summary.radar_pillars, summary.benchmark_scores, summary.user_scores);

  } catch (err) {
    console.error('Failed to run recommendation analysis:', err);
  }
}

// ----------------- NLP Job Extractor Playground ----------------- //

function setupNLPPlayground() {
  const analyzeBtn = document.getElementById('btn-analyze-jd');
  const jdTextarea = document.getElementById('jd-sample-input');

  if (analyzeBtn && jdTextarea) {
    analyzeBtn.addEventListener('click', async () => {
      const text = jdTextarea.value.trim();
      if (!text) return;
      await runNLPExtraction(text);
    });
  }
}

function loadSampleJD(sampleIndex) {
  const textarea = document.getElementById('jd-sample-input');
  if (!textarea) return;

  const samples = [
    "Looking for a Python developer with experience in SQL, AWS, Docker and Machine Learning to build automated data pipelines.",
    "Hiring a Data Scientist proficient in Python, SQL, Statistics, Pandas, and deep learning architectures like PyTorch or TensorFlow. Experience with Generative AI and RAG is a strong plus.",
    "Seeking Fullstack Engineer with proven track record in React, Node.js, TypeScript, REST APIs, PostgreSQL and Docker container deployments."
  ];

  textarea.value = samples[sampleIndex] || samples[0];
  runNLPExtraction(textarea.value);
}

async function runNLPExtraction(text) {
  const resultContainer = document.getElementById('nlp-results-container');
  const skillsPillContainer = document.getElementById('nlp-extracted-skills');
  const rolesPillContainer = document.getElementById('nlp-matched-roles');
  const timeEl = document.getElementById('nlp-proc-time');

  try {
    const res = await fetch(`${API_BASE}/api/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });

    const data = await res.json();

    if (resultContainer) resultContainer.style.display = 'block';
    if (timeEl) timeEl.innerText = `${data.processing_time_ms} ms`;

    // Render skills
    if (skillsPillContainer) {
      if (data.extracted_skills.length === 0) {
        skillsPillContainer.innerHTML = '<span style="color: #94a3b8;">No technical competencies detected.</span>';
      } else {
        skillsPillContainer.innerHTML = data.extracted_skills.map(s => `
          <span class="skill-tag core">${s}</span>
        `).join('');
      }
    }

    // Render matched roles
    if (rolesPillContainer) {
      rolesPillContainer.innerHTML = data.top_matching_roles.map(r => `
        <div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
          <div>
            <span style="font-weight: 600; color: #ffffff;">${r.role}</span>
            <span style="font-weight: 700; color: #06b6d4; font-size: 0.95rem; margin-left: 10px;">${r.match_percentage}% Alignment</span>
          </div>
          <button type="button" class="quick-chip" onclick="selectTargetRoleSuggestion('${r.role}'); switchView('recommend');" style="font-size: 0.75rem;">
            Set as Target Role ➔
          </button>
        </div>
      `).join('');
    }

  } catch (err) {
    console.error('NLP extraction error:', err);
  }
}

// ==========================================================================
// AUTHENTICATION & MULTI-ROLE USER MANAGEMENT CONTROLLER
// Supports: Student, Recruiter, Other / Educator
// Options: Email/Password, Social Single Sign-On, 1-Click Fast Demo Logins
// ==========================================================================

let currentUser = null;
let currentAuthRole = 'student'; // 'student' | 'recruiter' | 'other'
let currentAuthMode = 'signin';  // 'signin'  | 'signup'

/**
 * Initializes authentication system, restores saved sessions,
 * and sets up global click listeners.
 */
async function initAuthSystem() {
  // Check URL path: if /login was requested, open auth view
  if (window.location.pathname === '/login') {
    switchView('auth');
  }

  // Set up role specific initial dynamic fields
  updateRoleFormFields('student');

  // Global click listener to close user profile dropdown
  document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('user-dropdown-menu');
    const pill = document.getElementById('user-profile-pill');
    if (dropdown && dropdown.classList.contains('active')) {
      if (!dropdown.contains(e.target) && !pill.contains(e.target)) {
        dropdown.classList.remove('active');
      }
    }
  });

  // Restore session from localStorage
  const token = localStorage.getItem('skillpulse_auth_token');
  const storedUser = localStorage.getItem('skillpulse_auth_user');

  if (token && storedUser) {
    try {
      currentUser = JSON.parse(storedUser);
      // Validate session with backend
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        currentUser = data.user;
        localStorage.setItem('skillpulse_auth_user', JSON.stringify(currentUser));
      } else {
        // Token expired
        localStorage.removeItem('skillpulse_auth_token');
        localStorage.removeItem('skillpulse_auth_user');
        currentUser = null;
      }
    } catch (err) {
      console.warn('Session verification fallback:', err);
    }
  }

  updateNavAuthUI();
}

/**
 * Toggles user selection between Student, Recruiter, and Other.
 */
function selectAuthRole(role) {
  currentAuthRole = role;

  // Update role card visual indicators
  ['student', 'recruiter', 'other'].forEach(r => {
    const card = document.getElementById(`role-card-${r}`);
    if (card) {
      if (r === role) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    }
  });

  // Update contextual hint message
  const hintText = document.getElementById('role-context-text');
  if (hintText) {
    if (role === 'student') {
      hintText.innerHTML = 'Logging in as <strong>Student</strong>: You will get personalized skill gap scoring, target role alignments, and structured learning roadmaps.';
    } else if (role === 'recruiter') {
      hintText.innerHTML = 'Logging in as <strong>Tech Recruiter</strong>: You will get live talent supply indices, salary benchmarks, and demand momentum signals across Indian hubs.';
    } else {
      hintText.innerHTML = 'Logging in as <strong>Educator / Policy Advisor</strong>: You will access academic curriculum alignments, macroeconomic trends, and multi-quarter forecasting models.';
    }
  }

  // Update submit button labels
  const roleName = role === 'student' ? 'Student' : role === 'recruiter' ? 'Recruiter' : 'Educator';
  const signinBtn = document.getElementById('signin-btn-text');
  const signupBtn = document.getElementById('signup-btn-text');
  if (signinBtn) signinBtn.innerText = `Sign In as ${roleName} ➔`;
  if (signupBtn) signupBtn.innerText = `Create ${roleName} Account ➔`;

  // Update dynamic fields for sign up
  updateRoleFormFields(role);
}

/**
 * Renders role-specific input fields in the registration form.
 */
function updateRoleFormFields(role) {
  const container = document.getElementById('signup-role-fields');
  if (!container) return;

  if (role === 'student') {
    container.innerHTML = `
      <div class="auth-form-group">
        <label for="signup-college">College / University Name</label>
        <input type="text" id="signup-college" class="auth-input" placeholder="e.g., IIT Bombay / BITS Pilani" required>
      </div>
      <div class="auth-form-group">
        <label for="signup-target-role">Target Career Role</label>
        <select id="signup-target-role" class="auth-input" style="background: #0a101c; color: #fff;">
          <option value="Data Scientist">Data Scientist</option>
          <option value="Machine Learning Engineer">Machine Learning Engineer</option>
          <option value="Full Stack Developer">Full Stack Developer</option>
          <option value="DevOps Engineer">DevOps Engineer</option>
          <option value="Cloud Architect">Cloud Architect</option>
          <option value="Data Engineer">Data Engineer</option>
          <option value="Cybersecurity Analyst">Cybersecurity Analyst</option>
        </select>
      </div>
    `;
  } else if (role === 'recruiter') {
    container.innerHTML = `
      <div class="auth-form-group">
        <label for="signup-company">Company / Hiring Organization</label>
        <input type="text" id="signup-company" class="auth-input" placeholder="e.g., Zomato / Infosys / Tech Unicorn" required>
      </div>
      <div class="auth-form-group">
        <label for="signup-domain">Hiring Domain / Skill Cluster</label>
        <input type="text" id="signup-domain" class="auth-input" placeholder="e.g., Cloud & AI, Fullstack, Mobile" required>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="auth-form-group">
        <label for="signup-org">Institution / Organization</label>
        <input type="text" id="signup-org" class="auth-input" placeholder="e.g., NSDC / IIIT Hyderabad / Policy Lab" required>
      </div>
      <div class="auth-form-group">
        <label for="signup-title">Professional Role / Title</label>
        <input type="text" id="signup-title" class="auth-input" placeholder="e.g., CS Professor / Career Advisor / Analyst" required>
      </div>
    `;
  }
}

/**
 * Toggles between Sign In and Sign Up modes.
 */
function setAuthMode(mode) {
  currentAuthMode = mode;
  const btnSignIn = document.getElementById('btn-mode-signin');
  const btnSignUp = document.getElementById('btn-mode-signup');
  const formSignIn = document.getElementById('form-signin');
  const formSignUp = document.getElementById('form-signup');
  const alertBox = document.getElementById('auth-alert');

  if (alertBox) alertBox.style.display = 'none';

  if (mode === 'signin') {
    btnSignIn?.classList.add('active');
    btnSignUp?.classList.remove('active');
    if (formSignIn) formSignIn.style.display = 'block';
    if (formSignUp) formSignUp.style.display = 'none';
  } else {
    btnSignUp?.classList.add('active');
    btnSignIn?.classList.remove('active');
    if (formSignIn) formSignIn.style.display = 'none';
    if (formSignUp) formSignUp.style.display = 'block';
  }
}

/**
 * Updates top navbar, sidebar, dashboard welcome banner, and auth view based on active login state.
 */
function updateNavAuthUI() {
  const btnLogin = document.getElementById('btn-open-login');
  const profilePill = document.getElementById('user-profile-pill');
  const navAvatar = document.getElementById('nav-user-avatar');
  const navName = document.getElementById('nav-user-name');
  const navRoleBadge = document.getElementById('nav-user-role-badge');
  const ddName = document.getElementById('dd-user-name');
  const ddEmail = document.getElementById('dd-user-email');
  const ddOrg = document.getElementById('dd-user-org');
  const welcomeBanner = document.getElementById('dashboard-welcome-banner');
  const authLoggedInView = document.getElementById('auth-logged-in-view');
  const authFormsView = document.getElementById('auth-forms-view');

  applyRoleExperience();

  if (currentUser) {
    // 1. Logged In State
    if (btnLogin) btnLogin.style.display = 'none';
    if (profilePill) profilePill.style.display = 'inline-flex';

    const initials = (currentUser.name || 'User')
      .split(' ')
      .filter(Boolean)
      .map(n => n[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();

    if (navAvatar) {
      navAvatar.innerText = initials;
      navAvatar.className = `user-avatar-circle role-${currentUser.role}`;
    }

    if (navName) {
      navName.innerText = currentUser.name.split(' ')[0];
    }

    if (navRoleBadge) {
      const roleText = currentUser.role === 'student' ? 'Student' : currentUser.role === 'recruiter' ? 'Recruiter' : 'Educator';
      navRoleBadge.innerText = roleText;
      navRoleBadge.className = `user-role-badge badge-role-${currentUser.role}`;
    }

    if (ddName) ddName.innerText = currentUser.name;
    if (ddEmail) ddEmail.innerText = currentUser.email;
    if (ddOrg) {
      ddOrg.innerText = currentUser.organization || 'Verified Profile';
    }

    // 2. Personalize Dashboard Welcome Banner
    if (welcomeBanner) {
      welcomeBanner.style.display = 'flex';
      welcomeBanner.className = `user-welcome-banner role-${currentUser.role}`;
      const titleEl = document.getElementById('welcome-banner-title');
      const subtitleEl = document.getElementById('welcome-banner-subtitle');
      const actionBtn = document.getElementById('welcome-banner-action-btn');

      if (currentUser.role === 'student') {
        if (titleEl) titleEl.innerHTML = `Welcome back, <span id="welcome-user-name">${currentUser.name}</span>!`;
        if (subtitleEl) subtitleEl.innerText = `Personalized skill gap analysis calibrated for your target role (${currentUser.target_role || 'Data Scientist'}) at ${currentUser.organization || 'your university'}.`;
        if (actionBtn) actionBtn.innerText = 'Explore My Skill Roadmap ↗';
      } else if (currentUser.role === 'recruiter') {
        if (titleEl) titleEl.innerHTML = `Recruiter mode: <span id="welcome-user-name">${currentUser.name}</span> (${currentUser.organization || 'Tech Hiring'})`;
        if (subtitleEl) subtitleEl.innerText = `Market talent supply, emerging tech demand, and salary benchmarks are prioritized for your domain.`;
        if (actionBtn) actionBtn.innerText = 'View Role Salary Benchmarks ↗';
      } else {
        if (titleEl) titleEl.innerHTML = `Academic & policy mode: <span id="welcome-user-name">${currentUser.name}</span>`;
        if (subtitleEl) subtitleEl.innerText = `Curriculum alignment tools and multi-quarter tech momentum projections are active.`;
        if (actionBtn) actionBtn.innerText = 'Inspect Emerging Tech Radar ↗';
      }
    }

    // 3. Auth View Profile Card
    if (authLoggedInView) authLoggedInView.style.display = 'block';
    if (authFormsView) authFormsView.style.display = 'none';

    const cardAvatar = document.getElementById('card-avatar-large');
    const cardName = document.getElementById('card-user-name');
    const cardRoleTag = document.getElementById('card-role-tag');
    const cardEmail = document.getElementById('card-user-email');
    const cardOrg = document.getElementById('card-user-org');
    const cardTarget = document.getElementById('card-user-target');
    const cardProvider = document.getElementById('card-user-provider');

    if (cardAvatar) {
      cardAvatar.innerText = initials;
      cardAvatar.className = `logged-in-avatar-large role-${currentUser.role}`;
    }
    if (cardName) cardName.innerText = currentUser.name;
    if (cardRoleTag) {
      const tagText = currentUser.role === 'student' ? 'Student / Learner Profile' : currentUser.role === 'recruiter' ? 'Tech Recruiter Profile' : 'Educator / Research Profile';
      cardRoleTag.innerText = tagText;
      cardRoleTag.className = `logged-in-role-tag badge-role-${currentUser.role}`;
    }
    if (cardEmail) cardEmail.innerText = currentUser.email;
    if (cardOrg) cardOrg.innerText = currentUser.organization || 'Not Specified';
    if (cardTarget) cardTarget.innerText = currentUser.target_role || currentUser.domain || 'Tech Industry Intelligence';
    if (cardProvider) cardProvider.innerText = `${(currentUser.auth_provider || 'local').toUpperCase()} Authentication`;

  } else {
    // Guest State
    if (btnLogin) btnLogin.style.display = 'inline-flex';
    if (profilePill) profilePill.style.display = 'none';
    if (welcomeBanner) welcomeBanner.style.display = 'none';
    if (authLoggedInView) authLoggedInView.style.display = 'none';
    if (authFormsView) authFormsView.style.display = 'block';
  }
}

/**
 * Toggles navbar user dropdown menu.
 */
function toggleUserDropdown(event) {
  if (event) event.stopPropagation();
  const menu = document.getElementById('user-dropdown-menu');
  if (menu) {
    menu.classList.toggle('active');
  }
}

function closeUserDropdown() {
  const menu = document.getElementById('user-dropdown-menu');
  if (menu) menu.classList.remove('active');
}

/**
 * Handle Sign In Submission.
 */
async function handleSignInSubmit(event) {
  event.preventDefault();
  const emailInput = document.getElementById('signin-email');
  const passwordInput = document.getElementById('signin-password');
  const email = emailInput ? emailInput.value.trim() : '';
  const password = passwordInput ? passwordInput.value : '';
  const submitBtn = document.getElementById('btn-submit-signin');
  const btnText = document.getElementById('signin-btn-text');

  if (!email || !email.includes('@') || !email.includes('.')) {
    showAuthAlert('Please enter a valid email address.', 'error');
    if (emailInput) emailInput.focus();
    return;
  }

  if (!password) {
    showAuthAlert('Please enter your password.', 'error');
    if (passwordInput) passwordInput.focus();
    return;
  }

  const originalBtnContent = submitBtn ? submitBtn.innerHTML : '';
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Verifying credentials...</span>';
  }

  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email,
        password: password,
        role: currentAuthRole
      })
    });

    const data = await res.json();

    if (!res.ok) {
      showAuthAlert(data.detail || 'Sign-in failed. Please check your credentials.', 'error');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnContent;
      }
      return;
    }

    // Success
    localStorage.setItem('skillpulse_auth_token', data.token);
    localStorage.setItem('skillpulse_auth_user', JSON.stringify(data.user));
    currentUser = data.user;

    showAuthAlert(data.message || 'Welcome back to AROHA!', 'success');
    updateNavAuthUI();

    setTimeout(() => {
      switchView(getRoleDefaultView());
    }, 600);

  } catch (err) {
    showAuthAlert('Unable to reach server. Please ensure the backend is running.', 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnContent;
    }
  }
}

/**
 * Handle Sign Up Submission.
 */
async function handleSignUpSubmit(event) {
  event.preventDefault();
  const nameInput = document.getElementById('signup-name');
  const emailInput = document.getElementById('signup-email');
  const passwordInput = document.getElementById('signup-password');
  const confirmPasswordInput = document.getElementById('signup-confirm-password');

  const name = nameInput ? nameInput.value.trim() : '';
  const email = emailInput ? emailInput.value.trim().toLowerCase() : '';
  const password = passwordInput ? passwordInput.value : '';
  const confirmPassword = confirmPasswordInput ? confirmPasswordInput.value : '';
  const submitBtn = document.getElementById('btn-submit-signup');

  if (name.length < 2) {
    showAuthAlert('Please enter your full name (minimum 2 characters).', 'error');
    if (nameInput) nameInput.focus();
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showAuthAlert('Please enter a valid email address.', 'error');
    if (emailInput) emailInput.focus();
    return;
  }

  if (password.length < 6) {
    showAuthAlert('Password must be at least 6 characters long.', 'error');
    if (passwordInput) passwordInput.focus();
    return;
  }

  if (password !== confirmPassword) {
    showAuthAlert('Passwords do not match. Please re-enter your password.', 'error');
    if (confirmPasswordInput) confirmPasswordInput.focus();
    return;
  }

  // Extract role metadata
  let organization = null;
  let targetRole = null;
  let domain = null;

  if (currentAuthRole === 'student') {
    organization = document.getElementById('signup-college')?.value.trim();
    targetRole = document.getElementById('signup-target-role')?.value.trim();
  } else if (currentAuthRole === 'recruiter') {
    organization = document.getElementById('signup-company')?.value.trim();
    domain = document.getElementById('signup-domain')?.value.trim();
  } else {
    organization = document.getElementById('signup-org')?.value.trim();
    domain = document.getElementById('signup-title')?.value.trim();
  }

  const originalBtnContent = submitBtn ? submitBtn.innerHTML : '';
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Creating Account...</span>';
  }

  try {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        email: email,
        password: password,
        role: currentAuthRole,
        organization: organization || null,
        target_role: targetRole || null,
        domain: domain || null
      })
    });

    const data = await res.json();

    if (!res.ok) {
      showAuthAlert(data.detail || 'Registration failed. This email may already be in use.', 'error');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnContent;
      }
      return;
    }

    // Success
    localStorage.setItem('skillpulse_auth_token', data.token);
    localStorage.setItem('skillpulse_auth_user', JSON.stringify(data.user));
    currentUser = data.user;

    showAuthAlert(`Account created successfully! Welcome to AROHA, ${data.user.name}.`, 'success');
    updateNavAuthUI();

    setTimeout(() => {
      switchView(getRoleDefaultView());
    }, 700);

  } catch (err) {
    showAuthAlert('Network error during registration. Please check your connection.', 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnContent;
    }
  }
}

let currentSocialProvider = 'google';

const SOCIAL_ICONS = {
  google: `<svg viewBox="0 0 24 24" width="22" height="22"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>`,
  linkedin: `<svg viewBox="0 0 24 24" width="22" height="22" fill="#0A66C2"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 8.76c-.97 0-1.75-.79-1.75-1.76s.78-1.76 1.75-1.76 1.75.79 1.75 1.76-.78 1.76-1.75 1.76m1.39 9.74v-8.37H5.07v8.37h2.78z"/></svg>`,
  github: `<svg viewBox="0 0 24 24" width="22" height="22" fill="#FFFFFF"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>`,
  microsoft: `<svg viewBox="0 0 24 24" width="22" height="22"><rect x="1" y="1" width="10" height="10" fill="#F25022"/><rect x="13" y="1" width="10" height="10" fill="#7FBA00"/><rect x="1" y="13" width="10" height="10" fill="#00A4EF"/><rect x="13" y="13" width="10" height="10" fill="#FFB900"/></svg>`
};

/**
 * Handle Single-Sign-On trigger with Social Providers (Google, LinkedIn, GitHub, Microsoft).
 * Opens dedicated identity modal allowing the user to sign in with their own account.
 */
function handleSocialAuth(provider) {
  currentSocialProvider = provider;
  const providerNames = {
    google: 'Google',
    linkedin: 'LinkedIn',
    github: 'GitHub',
    microsoft: 'Microsoft'
  };
  const pName = providerNames[provider] || provider.toUpperCase();

  const titleEl = document.getElementById('social-modal-title');
  const iconEl = document.getElementById('social-modal-icon');
  const descEl = document.getElementById('social-modal-desc');
  const labelEl = document.getElementById('social-input-email-label');
  const emailInput = document.getElementById('social-input-email');
  const nameInput = document.getElementById('social-input-name');
  const submitBtn = document.getElementById('btn-social-modal-submit');
  const alertEl = document.getElementById('social-modal-alert');

  if (titleEl) titleEl.innerText = `Sign in with ${pName}`;
  if (iconEl) iconEl.innerHTML = SOCIAL_ICONS[provider] || '';
  if (descEl) descEl.innerText = `Connect your ${pName} account to access AROHA instantly as a ${currentAuthRole.toUpperCase()} without needing a password.`;
  if (labelEl) labelEl.innerText = `Your ${pName} Email Address`;
  if (submitBtn) submitBtn.innerText = `Continue with ${pName} ➔`;
  if (alertEl) alertEl.style.display = 'none';

  // Pre-fill email and name if user typed anything on main forms
  const mainEmail = (document.getElementById('signin-email')?.value || document.getElementById('signup-email')?.value || '').trim();
  const mainName = (document.getElementById('signup-name')?.value || '').trim();

  if (emailInput) {
    emailInput.placeholder = provider === 'google' ? 'e.g., yourname@gmail.com' :
                             provider === 'microsoft' ? 'e.g., yourname@outlook.com' :
                             provider === 'linkedin' ? 'e.g., yourname@domain.com' : 'e.g., username@github.com';
    if (mainEmail) emailInput.value = mainEmail;
  }
  if (nameInput && mainName) nameInput.value = mainName;

  const modal = document.getElementById('auth-social-modal');
  if (modal) modal.classList.add('active');
}

function closeSocialAuthModal(e) {
  if (e && e.target && e.target.id !== 'auth-social-modal') return;
  const modal = document.getElementById('auth-social-modal');
  if (modal) modal.classList.remove('active');
}

async function handleSocialModalSubmit(event) {
  event.preventDefault();
  const name = document.getElementById('social-input-name').value.trim();
  const email = document.getElementById('social-input-email').value.trim().toLowerCase();
  const submitBtn = document.getElementById('btn-social-modal-submit');
  const alertEl = document.getElementById('social-modal-alert');

  if (!email || !email.includes('@')) {
    if (alertEl) {
      alertEl.className = 'auth-alert error';
      alertEl.innerText = 'Please provide a valid email address.';
      alertEl.style.display = 'block';
    }
    return;
  }

  const pName = currentSocialProvider.toUpperCase();
  const originalBtn = submitBtn ? submitBtn.innerText : '';
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerText = `Connecting via ${pName}...`;
  }

  try {
    const res = await fetch(`${API_BASE}/api/auth/social-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: currentSocialProvider,
        name: name || 'Verified User',
        email: email,
        role: currentAuthRole,
        organization: currentAuthRole === 'student' ? 'Tech University' : currentAuthRole === 'recruiter' ? 'Tech Enterprise' : 'Academic Council'
      })
    });

    const data = await res.json();
    if (!res.ok) {
      if (alertEl) {
        alertEl.className = 'auth-alert error';
        alertEl.innerText = data.detail || 'Social sign-in failed. Please try again.';
        alertEl.style.display = 'block';
      }
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = originalBtn;
      }
      return;
    }

    // Success
    localStorage.setItem('skillpulse_auth_token', data.token);
    localStorage.setItem('skillpulse_auth_user', JSON.stringify(data.user));
    currentUser = data.user;

    if (alertEl) {
      alertEl.className = 'auth-alert success';
      alertEl.innerText = `Authenticated successfully as ${currentUser.name}! Redirecting...`;
      alertEl.style.display = 'block';
    }

    setTimeout(() => {
      closeSocialAuthModal();
      updateNavAuthUI();
      showAuthAlert(`Signed in with ${pName} as ${currentUser.name}.`, 'success');
      switchView(getRoleDefaultView());
    }, 600);

  } catch (err) {
    if (alertEl) {
      alertEl.className = 'auth-alert error';
      alertEl.innerText = 'Unable to reach authentication server. Please check connection.';
      alertEl.style.display = 'block';
    }
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerText = originalBtn;
    }
  }
}


/**
 * Sign out active user.
 */
async function handleLogout() {
  const token = localStorage.getItem('skillpulse_auth_token');
  if (token) {
    try {
      await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (e) {
      // Ignore network errors on logout
    }
  }

  localStorage.removeItem('skillpulse_auth_token');
  localStorage.removeItem('skillpulse_auth_user');
  currentUser = null;

  closeUserDropdown();
  updateNavAuthUI();

  // If currently on Auth view, reset to signin form
  setAuthMode('signin');
  showAuthAlert('You have successfully signed out.', 'success');
}

/**
 * Password Visibility Toggle.
 */
function togglePasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    btn.innerText = 'Hide';
  } else {
    input.type = 'password';
    btn.innerText = 'Show';
  }
}

/**
 * Real-time Password Strength Meter.
 */
function checkPasswordStrength(pw) {
  const bar1 = document.getElementById('pw-bar-1');
  const bar2 = document.getElementById('pw-bar-2');
  const bar3 = document.getElementById('pw-bar-3');
  const text = document.getElementById('pw-strength-text');
  if (!bar1 || !bar2 || !bar3 || !text) return;

  if (!pw || pw.length === 0) {
    bar1.style.background = 'rgba(255,255,255,0.1)';
    bar2.style.background = 'rgba(255,255,255,0.1)';
    bar3.style.background = 'rgba(255,255,255,0.1)';
    text.innerText = 'Password strength: Empty';
    text.style.color = '#94a3b8';
    return;
  }

  let score = 0;
  if (pw.length >= 6) score++;
  if (pw.length >= 8 && /[A-Z]/.test(pw) && /[0-9]/.test(pw)) score++;
  if (pw.length >= 10 && /[^A-Za-z0-9]/.test(pw)) score++;

  if (score === 1) {
    bar1.style.background = '#ef4444';
    bar2.style.background = 'rgba(255,255,255,0.1)';
    bar3.style.background = 'rgba(255,255,255,0.1)';
    text.innerText = 'Password strength: Weak (min 6 chars)';
    text.style.color = '#ef4444';
  } else if (score === 2) {
    bar1.style.background = '#f59e0b';
    bar2.style.background = '#f59e0b';
    bar3.style.background = 'rgba(255,255,255,0.1)';
    text.innerText = 'Password strength: Good';
    text.style.color = '#f59e0b';
  } else {
    bar1.style.background = '#10b981';
    bar2.style.background = '#10b981';
    bar3.style.background = '#10b981';
    text.innerText = 'Password strength: Excellent & Secure';
    text.style.color = '#10b981';
  }
}

/**
 * Display alert banner inside auth form.
 */
function showAuthAlert(message, type) {
  const alertBox = document.getElementById('auth-alert');
  if (!alertBox) return;
  alertBox.className = `auth-alert ${type}`;
  alertBox.innerText = message;
  alertBox.style.display = 'block';
}

/**
 * Forgot Password Modal Controllers.
 */
function openForgotPasswordModal() {
  const modal = document.getElementById('auth-forgot-modal');
  if (modal) modal.classList.add('active');
}

function closeForgotPasswordModal(e) {
  if (e && e.target && e.target.id !== 'auth-forgot-modal') return;
  const modal = document.getElementById('auth-forgot-modal');
  if (modal) modal.classList.remove('active');
}

async function handleResetPasswordSubmit(event) {
  event.preventDefault();
  const email = document.getElementById('reset-email').value.trim();
  const newPw = document.getElementById('reset-new-password').value;
  const resetAlert = document.getElementById('reset-alert');

  try {
    const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, new_password: newPw })
    });

    const data = await res.json();
    if (!res.ok) {
      if (resetAlert) {
        resetAlert.className = 'auth-alert error';
        resetAlert.innerText = data.detail || 'Reset failed.';
        resetAlert.style.display = 'block';
      }
      return;
    }

    if (resetAlert) {
      resetAlert.className = 'auth-alert success';
      resetAlert.innerText = 'Password updated successfully. Closing...';
      resetAlert.style.display = 'block';
    }

    setTimeout(() => {
      closeForgotPasswordModal();
      showAuthAlert('Password updated. Please log in with your new password.', 'success');
    }, 1500);

  } catch (err) {
    if (resetAlert) {
      resetAlert.className = 'auth-alert error';
      resetAlert.innerText = 'Network error during reset.';
      resetAlert.style.display = 'block';
    }
  }
}

/**
 * Welcome Banner Role-Based Action Trigger.
 */
function handleWelcomeBannerAction() {
  if (!currentUser) {
    switchView('auth');
    return;
  }
  if (currentUser.role === 'student') {
    switchView('recommend');
  } else if (currentUser.role === 'recruiter') {
    switchView('career');
  } else {
    switchView('emerging');
  }
}



