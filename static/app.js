// Smart Resume Job Matching & Skill Gap Analyzer - Frontend Logic

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  let presetsData = { sample_resumes: [], sample_jds: [], skills_db: {} };
  let selectedFile = null;

  // DOM Elements
  const navTabs = document.querySelectorAll(".nav-tab");
  const tabContents = document.querySelectorAll(".tab-content");

  const modeTextBtn = document.getElementById("mode-text-btn");
  const modeFileBtn = document.getElementById("mode-file-btn");
  const textInputContainer = document.getElementById("text-input-container");
  const fileUploadContainer = document.getElementById("file-upload-container");

  const resumeFileInput = document.getElementById("resume-file-input");
  const dropZone = document.getElementById("drop-zone");
  const fileSelectedName = document.getElementById("file-selected-name");

  const resumeTextInput = document.getElementById("resume-text-input");
  const jdPresetSelect = document.getElementById("jd-preset-select");
  const jdTextInput = document.getElementById("jd-text-input");

  const btnRunMatch = document.getElementById("btn-run-match");
  const matchResultsPlaceholder = document.getElementById("match-results-placeholder");
  const matchResultsContainer = document.getElementById("match-results-container");

  // Output elements
  const resOverallScore = document.getElementById("res-overall-score");
  const resSkillScore = document.getElementById("res-skill-score");
  const resSemanticScore = document.getElementById("res-semantic-score");
  const resAtsScore = document.getElementById("res-ats-score");
  const matchedCount = document.getElementById("matched-count");
  const missingCount = document.getElementById("missing-count");
  const matchedSkillsBadges = document.getElementById("matched-skills-badges");
  const missingSkillsBadges = document.getElementById("missing-skills-badges");
  const roadmapContainer = document.getElementById("roadmap-container");

  // Recruiter Tab Elements
  const batchJdInput = document.getElementById("batch-jd-input");
  const btnRunBatch = document.getElementById("btn-run-batch");
  const batchResultsContainer = document.getElementById("batch-results-container");
  const leaderboardBody = document.getElementById("leaderboard-body");

  // Samples Tab
  const samplesGrid = document.getElementById("samples-grid");

  // Bullet Enhancer
  const bulletInput = document.getElementById("bullet-input");
  const btnEnhanceBullet = document.getElementById("btn-enhance-bullet");
  const bulletResultContainer = document.getElementById("bullet-result-container");
  const bulletEnhancedText = document.getElementById("bullet-enhanced-text");
  const bulletTipsList = document.getElementById("bullet-tips-list");

  // Fetch Presets on Load
  fetchPresets();

  // Tab Navigation Handler
  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      navTabs.forEach(t => t.classList.remove("active"));
      tabContents.forEach(c => c.classList.add("hidden"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      document.getElementById(targetId).classList.remove("hidden");
    });
  });

  // Mode Toggle (Text vs File)
  modeTextBtn.addEventListener("click", () => {
    modeTextBtn.classList.add("active");
    modeFileBtn.classList.remove("active");
    textInputContainer.classList.remove("hidden");
    fileUploadContainer.classList.add("hidden");
  });

  modeFileBtn.addEventListener("click", () => {
    modeFileBtn.classList.add("active");
    modeTextBtn.classList.remove("active");
    fileUploadContainer.classList.remove("hidden");
    textInputContainer.classList.add("hidden");
  });

  // File Upload Handlers
  dropZone.addEventListener("click", () => resumeFileInput.click());

  resumeFileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      selectedFile = e.target.files[0];
      fileSelectedName.textContent = `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
      fileSelectedName.style.color = "var(--accent-green)";
    }
  });

  // Preset JD Selection Handler
  jdPresetSelect.addEventListener("change", (e) => {
    const selectedId = e.target.value;
    if (selectedId) {
      const found = presetsData.sample_jds.find(j => j.id === selectedId);
      if (found) {
        jdTextInput.value = found.description;
      }
    }
  });

  // Fetch presets API
  async function fetchPresets() {
    try {
      const res = await fetch("/api/presets");
      presetsData = await res.json();

      // Populate JD presets
      jdPresetSelect.innerHTML = `<option value="">-- Choose a Preset Benchmark Job Role --</option>`;
      presetsData.sample_jds.forEach(jd => {
        const opt = document.createElement("option");
        opt.value = jd.id;
        opt.textContent = `${jd.role_title} (${jd.company})`;
        jdPresetSelect.appendChild(opt);
      });

      // Set default JD text if available
      if (presetsData.sample_jds.length > 0) {
        jdPresetSelect.value = presetsData.sample_jds[0].id;
        jdTextInput.value = presetsData.sample_jds[0].description;
        batchJdInput.value = presetsData.sample_jds[0].description;
      }

      // Populate Samples Grid
      renderSamplesGrid();

    } catch (err) {
      console.error("Error loading presets:", err);
    }
  }

  // Render Sample Resumes Grid
  function renderSamplesGrid() {
    samplesGrid.innerHTML = "";
    presetsData.sample_resumes.forEach(sample => {
      const card = document.createElement("div");
      card.className = "roadmap-card";
      card.style.cursor = "pointer";
      card.innerHTML = `
        <div class="roadmap-header">
          <div class="roadmap-skill">${sample.title}</div>
          <span class="priority-pill Bonus">${sample.role}</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4; margin-top: 0.5rem;">
          ${sample.text.substring(0, 150)}...
        </p>
        <button class="btn-secondary" style="margin-top: 1rem; width: 100%;">
          <i class="fa-solid fa-square-check"></i> Load into Analyzer
        </button>
      `;

      card.addEventListener("click", () => {
        resumeTextInput.value = sample.text;
        modeTextBtn.click();
        document.querySelector('[data-tab="tab-analyzer"]').click();
      });

      samplesGrid.appendChild(card);
    });
  }

  // Run Match Analysis Handler
  btnRunMatch.addEventListener("click", async () => {
    let resumeText = resumeTextInput.value;

    if (modeFileBtn.classList.contains("active") && selectedFile) {
      // Parse uploaded file first
      btnRunMatch.innerHTML = `<span class="loading-spinner"></span> Parsing File...`;
      const formData = new FormData();
      formData.append("file", selectedFile);

      try {
        const parseRes = await fetch("/api/parse-resume", {
          method: "POST",
          body: formData
        });
        const parseData = await parseRes.json();
        resumeText = parseData.parsed.raw_text;
      } catch (err) {
        alert("Failed to parse resume file.");
        btnRunMatch.innerHTML = `<i class="fa-solid fa-rocket"></i> Analyze Job Fit & Skill Gap`;
        return;
      }
    }

    const jdText = jdTextInput.value || "";
    if (!resumeText || !resumeText.trim() || !jdText || !jdText.trim()) {
      alert("Please provide both resume text (or file) and target job description.");
      btnRunMatch.innerHTML = `<i class="fa-solid fa-rocket"></i> Analyze Job Fit & Skill Gap`;
      return;
    }

    btnRunMatch.innerHTML = `<span class="loading-spinner"></span> Running Match Engine...`;

    try {
      const matchRes = await fetch("/api/analyze-match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resumeText, jd_text: jdText })
      });
      const data = await matchRes.json();

      renderMatchResults(data);

    } catch (err) {
      console.error(err);
      alert("Error analyzing match.");
    } finally {
      btnRunMatch.innerHTML = `<i class="fa-solid fa-rocket"></i> Analyze Job Fit & Skill Gap`;
    }
  });

  // Render Match Results
  function renderMatchResults(data) {
    matchResultsPlaceholder.classList.add("hidden");
    matchResultsContainer.classList.remove("hidden");

    const match = data.match_analysis;
    const ats = data.ats_analysis;
    const roadmap = data.learning_roadmap;

    resOverallScore.textContent = `${match.overall_score}%`;
    resSkillScore.textContent = `${match.skill_score}%`;
    resSemanticScore.textContent = `${match.semantic_score}%`;
    resAtsScore.textContent = `${ats.ats_score}%`;

    const matched = match.skill_gap_matrix.matched_skills;
    const missing = match.skill_gap_matrix.missing_skills;

    matchedCount.textContent = matched.length;
    missingCount.textContent = missing.length;

    // Matched Badges
    matchedSkillsBadges.innerHTML = matched.map(s => 
      `<span class="skill-badge matched"><i class="fa-solid fa-check"></i> ${s.name}</span>`
    ).join("") || `<span style="color: var(--text-muted); font-size: 0.85rem;">None detected</span>`;

    // Missing Badges
    missingSkillsBadges.innerHTML = missing.map(s => 
      `<span class="skill-badge missing"><i class="fa-solid fa-xmark"></i> ${s.name}</span>`
    ).join("") || `<span style="color: var(--accent-green); font-size: 0.85rem;">No missing essential skills!</span>`;

    // Learning Roadmap
    roadmapContainer.innerHTML = roadmap.map(r => `
      <div class="roadmap-card ${(r.priority || '').split(' ')[0]}">
        <div class="roadmap-header">
          <div class="roadmap-skill">${r.step || r.id || 1}. ${r.skill || r.missing_skill} (${r.category})</div>
          <span class="priority-pill ${(r.priority || '').split(' ')[0]}">${r.priority} ${r.estimated_time ? '(' + r.estimated_time + ')' : ''}</span>
        </div>
        <div class="roadmap-details">
          <p><strong>Course:</strong> ${r.recommended_course}</p>
          <p><strong>Project:</strong> ${r.hands_on_project || r.suggested_project}</p>
        </div>
        <div class="roadmap-links">
          <a href="${r.documentation_link || r.documentation_url}" target="_blank" class="roadmap-link">
            <i class="fa-solid fa-book-open"></i> Documentation & Learning Link
          </a>
        </div>
      </div>
    `).join("");
  }

  // Recruiter Batch Match Handler
  btnRunBatch.addEventListener("click", async () => {
    const jdText = batchJdInput.value;
    if (!jdText.trim()) {
      alert("Please enter a Job Description for ranking.");
      return;
    }

    if (!presetsData.sample_resumes || presetsData.sample_resumes.length === 0) {
      alert("No sample resumes available to batch match.");
      return;
    }

    btnRunBatch.innerHTML = `<span class="loading-spinner"></span> Ranking Candidates...`;

    try {
      const payload = {
        jd_text: jdText,
        resumes: presetsData.sample_resumes.map(r => ({ id: r.id, name: r.title, text: r.text }))
      };

      const res = await fetch("/api/batch-match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      renderBatchLeaderboard(data.leaderboard);

    } catch (err) {
      console.error(err);
      alert("Failed batch matching.");
    } finally {
      btnRunBatch.innerHTML = `<i class="fa-solid fa-ranking-star"></i> Rank Sample Candidate Profiles`;
    }
  });

  function renderBatchLeaderboard(leaderboard) {
    batchResultsContainer.classList.remove("hidden");
    leaderboardBody.innerHTML = leaderboard.map((c, idx) => `
      <tr>
        <td><strong style="color: var(--accent-cyan);">#${idx + 1}</strong></td>
        <td><strong>${c.name}</strong><br><span style="font-size:0.75rem; color:var(--text-muted);">${c.email || ''}</span></td>
        <td><span class="skill-badge matched">${c.overall_score}%</span></td>
        <td>${c.skill_score}%</td>
        <td>${c.ats_score}%</td>
        <td>${c.matched_skills.slice(0, 4).join(", ")}</td>
        <td><span style="color: var(--accent-rose); font-size: 0.8rem;">${c.missing_skills.slice(0, 3).join(", ")}</span></td>
      </tr>
    `).join("");
  }

  // Bullet Enhancer Handler
  btnEnhanceBullet.addEventListener("click", async () => {
    const bullet = bulletInput.value;
    if (!bullet.trim()) {
      alert("Please enter a bullet point to enhance.");
      return;
    }

    btnEnhanceBullet.innerHTML = `<span class="loading-spinner"></span> Enhancing...`;

    try {
      const res = await fetch("/api/enhance-bullet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bullet })
      });
      const data = await res.json();

      bulletResultContainer.classList.remove("hidden");
      bulletEnhancedText.textContent = `"${data.enhanced}"`;
      bulletTipsList.innerHTML = data.tips.map(t => `<li>${t}</li>`).join("");

    } catch (err) {
      console.error(err);
      alert("Error enhancing bullet point.");
    } finally {
      btnEnhanceBullet.innerHTML = `<i class="fa-solid fa-bolt"></i> Enhance Bullet Point`;
    }
  });
});
