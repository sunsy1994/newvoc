let selectedBatchId = null;

const taskList = document.querySelector("#task-list");
const selectedTask = document.querySelector("#selected-task");
const runButton = document.querySelector("#run-task");
const summaryBox = document.querySelector("#summary");
const tableSelect = document.querySelector("#table-select");
const tableMeta = document.querySelector("#table-meta");
const dataTable = document.querySelector("#data-table");
const tablePager = document.querySelector("#table-pager");
const exportTableButton = document.querySelector("#export-table");
const errorBox = document.querySelector("#error-box");
const uploadMessage = document.querySelector("#upload-message");
const flowList = document.querySelector("#flow-list");
const scriptEditor = document.querySelector("#script-editor");
const scriptMeta = document.querySelector("#script-meta");
const scriptMessage = document.querySelector("#script-message");
const backupList = document.querySelector("#backup-list");
const testScriptButton = document.querySelector("#test-script");
const mainNavItems = document.querySelectorAll(".main-nav-item");
const mainViews = document.querySelectorAll(".main-view");
const subnavItems = document.querySelectorAll(".subnav-item");
const workbenchViews = document.querySelectorAll(".workbench-view");
const assetTabs = document.querySelectorAll(".asset-tab");
const assetTitle = document.querySelector("#asset-title");
const assetMeta = document.querySelector("#asset-meta");
const assetTable = document.querySelector("#asset-table");
const assetSearchForm = document.querySelector("#asset-search-form");
const assetSearchInput = document.querySelector("#asset-search-input");
const assetPager = document.querySelector("#asset-pager");
const exportAssetButton = document.querySelector("#export-asset");
const competitorTabs = document.querySelectorAll(".competitor-tab");
const competitorViews = document.querySelectorAll(".competitor-view");
const competitorAccountTitle = document.querySelector("#competitor-account-title");
const competitorAccountMeta = document.querySelector("#competitor-account-meta");
const competitorAccountTable = document.querySelector("#competitor-account-table");
const competitorAccountSearchForm = document.querySelector("#competitor-account-search-form");
const competitorAccountSearchInput = document.querySelector("#competitor-account-search-input");
const competitorAccountPager = document.querySelector("#competitor-account-pager");
const exportCompetitorAccountsButton = document.querySelector("#export-competitor-accounts");
const competitorWorkTitle = document.querySelector("#competitor-work-title");
const competitorWorkMeta = document.querySelector("#competitor-work-meta");
const competitorWorkTable = document.querySelector("#competitor-work-table");
const competitorWorkFilterForm = document.querySelector("#competitor-work-filter-form");
const competitorWorkSearchInput = document.querySelector("#competitor-work-search-input");
const competitorBrandFilter = document.querySelector("#competitor-brand-filter");
const competitorAccountTypeFilter = document.querySelector("#competitor-account-type-filter");
const competitorStartDate = document.querySelector("#competitor-start-date");
const competitorEndDate = document.querySelector("#competitor-end-date");
const competitorWorkPager = document.querySelector("#competitor-work-pager");
const exportCompetitorWorksButton = document.querySelector("#export-competitor-works");
const profileTabs = document.querySelectorAll(".profile-tab");
const profileViews = document.querySelectorAll(".profile-view");
const kolSampleDays = document.querySelector("#kol-sample-days");
const exportKolSamplesButton = document.querySelector("#export-kol-samples");
const kolProfileUploadForm = document.querySelector("#kol-profile-upload-form");
const kolProfileUploadMessage = document.querySelector("#kol-profile-upload-message");
const kolProfileTitle = document.querySelector("#kol-profile-title");
const kolProfileMeta = document.querySelector("#kol-profile-meta");
const kolProfileTable = document.querySelector("#kol-profile-table");
const kolProfileSearchForm = document.querySelector("#kol-profile-search-form");
const kolProfileSearchInput = document.querySelector("#kol-profile-search-input");
const kolProfileBatchFilter = document.querySelector("#kol-profile-batch-filter");
const kolProfilePager = document.querySelector("#kol-profile-pager");
const exportCommentUserSamplesButton = document.querySelector("#export-comment-user-samples");
const commentUserProfileUploadForm = document.querySelector("#comment-user-profile-upload-form");
const commentUserProfileUploadMessage = document.querySelector("#comment-user-profile-upload-message");
const commentUserProfileTitle = document.querySelector("#comment-user-profile-title");
const commentUserProfileMeta = document.querySelector("#comment-user-profile-meta");
const commentUserProfileTable = document.querySelector("#comment-user-profile-table");
const commentUserProfileSearchForm = document.querySelector("#comment-user-profile-search-form");
const commentUserProfileSearchInput = document.querySelector("#comment-user-profile-search-input");
const commentUserProfileBatchFilter = document.querySelector("#comment-user-profile-batch-filter");
const commentUserProfilePager = document.querySelector("#comment-user-profile-pager");
let currentAssetKey = "events";
const pageSize = 50;
const tableState = { offset: 0, total: 0 };
const assetState = { offset: 0, total: 0 };
const competitorAccountState = { offset: 0, total: 0 };
const competitorWorkState = { offset: 0, total: 0 };
const kolProfileState = { offset: 0, total: 0 };
const commentUserProfileState = { offset: 0, total: 0 };

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json();
}

function renderPager(container, state, onPageChange) {
  const totalPages = Math.max(1, Math.ceil(state.total / pageSize));
  const currentPage = Math.floor(state.offset / pageSize) + 1;
  const canPrev = state.offset > 0;
  const canNext = state.offset + pageSize < state.total;
  container.innerHTML = `
    <button class="ghost pager-prev" type="button" ${canPrev ? "" : "disabled"}>上一页</button>
    <span>第 ${currentPage} / ${totalPages} 页，共 ${state.total} 条</span>
    <button class="ghost pager-next" type="button" ${canNext ? "" : "disabled"}>下一页</button>
  `;
  container.querySelector(".pager-prev").addEventListener("click", () => {
    if (!canPrev) return;
    state.offset = Math.max(0, state.offset - pageSize);
    onPageChange();
  });
  container.querySelector(".pager-next").addEventListener("click", () => {
    if (!canNext) return;
    state.offset += pageSize;
    onPageChange();
  });
}

function downloadExcel(path) {
  window.location.href = path;
}

function statusLabel(status) {
  return { uploaded: "待执行", running: "运行中", success: "成功", failed: "失败" }[status] || status;
}

function renderTasks(tasks) {
  taskList.innerHTML = "";
  if (!tasks.length) {
    taskList.innerHTML = '<p class="message">还没有导入批次。</p>';
    return;
  }
  for (const task of tasks) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `task-item ${task.batch_id === selectedBatchId ? "selected" : ""}`;
    button.innerHTML = `
      <div class="task-row">
        <strong>${task.batch_id}</strong>
        <span class="status ${task.status}">${statusLabel(task.status)}</span>
      </div>
      <small>${task.created_at}</small>
    `;
    button.addEventListener("click", () => selectTask(task.batch_id));
    taskList.appendChild(button);
  }
}

async function loadTasks() {
  const tasks = await api("/api/tasks");
  renderTasks(tasks);
  if (!selectedBatchId && tasks.length) {
    await selectTask(tasks[0].batch_id);
  }
}

function renderSummary(summary = {}) {
  const keys = [
    ["ods_event_upload", "事件ODS"],
    ["ods_content_upload", "内容ODS"],
    ["ods_comment_upload", "评论ODS"],
    ["dwd_content", "标准内容"],
    ["dwd_comment", "标准评论"],
    ["rejected_comment", "拒绝评论"],
  ];
  summaryBox.innerHTML = keys.map(([key, label]) => `
    <div class="metric">
      <strong>${summary[key] ?? "-"}</strong>
      <span>${label}</span>
    </div>
  `).join("");
}

async function selectTask(batchId) {
  selectedBatchId = batchId;
  const task = await api(`/api/tasks/${batchId}`);
  selectedTask.textContent = `${task.batch_id} / ${statusLabel(task.status)}`;
  runButton.disabled = task.status === "running";
  testScriptButton.disabled = task.status === "running";
  renderSummary(task.summary);
  errorBox.style.display = task.error_message ? "block" : "none";
  errorBox.textContent = task.error_message || "";
  await loadTasks();
  await loadTables(batchId);
  await loadFlow();
}

async function loadTables(batchId) {
  tableSelect.innerHTML = "";
  dataTable.innerHTML = "";
  tableMeta.textContent = "";
  tablePager.innerHTML = "";
  exportTableButton.disabled = true;
  try {
    const payload = await api(`/api/tasks/${batchId}/tables`);
    for (const table of payload.tables) {
      const option = document.createElement("option");
      option.value = table;
      option.textContent = table;
      tableSelect.appendChild(option);
    }
    if (payload.tables.length) {
      tableState.offset = 0;
      await loadTable(batchId, payload.tables[0]);
    }
  } catch {
    tableMeta.textContent = "该批次暂无输出表。";
  }
}

async function loadTable(batchId, tableName) {
  if (!tableName) return;
  const payload = await api(`/api/tasks/${batchId}/tables/${tableName}?limit=${pageSize}&offset=${tableState.offset}`);
  tableState.total = payload.total;
  const startRow = payload.total ? tableState.offset + 1 : 0;
  const endRow = Math.min(tableState.offset + pageSize, payload.total);
  tableMeta.textContent = `${payload.total} 行，当前显示 ${startRow}-${endRow} 行`;
  exportTableButton.disabled = false;
  const head = `<thead><tr>${payload.columns.map(column => `<th>${column}</th>`).join("")}</tr></thead>`;
  const rows = payload.rows.map(row => `
    <tr>${payload.columns.map(column => `<td>${row[column] ?? ""}</td>`).join("")}</tr>
  `).join("");
  dataTable.innerHTML = `${head}<tbody>${rows}</tbody>`;
  renderPager(tablePager, tableState, () => loadTable(batchId, tableName));
}

document.querySelector("#upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const uploadForm = event.currentTarget;
  uploadMessage.textContent = "正在上传...";
  const formData = new FormData(uploadForm);
  try {
    const task = await api("/api/tasks/upload", { method: "POST", body: formData });
    uploadMessage.textContent = `已创建批次：${task.batch_id}`;
    uploadForm.reset();
    await loadTasks();
    await selectTask(task.batch_id);
  } catch (error) {
    uploadMessage.textContent = error.message;
  }
});

runButton.addEventListener("click", async () => {
  if (!selectedBatchId) return;
  runButton.disabled = true;
  selectedTask.textContent = `${selectedBatchId} / 运行中`;
  const task = await api(`/api/tasks/${selectedBatchId}/run`, { method: "POST" });
  await selectTask(task.batch_id);
});

tableSelect.addEventListener("change", () => {
  tableState.offset = 0;
  loadTable(selectedBatchId, tableSelect.value);
});

exportTableButton.addEventListener("click", () => {
  if (!selectedBatchId || !tableSelect.value) return;
  downloadExcel(`/api/tasks/${selectedBatchId}/tables/${tableSelect.value}/export`);
});

document.querySelector("#refresh-tasks").addEventListener("click", loadTasks);

function activateView(viewId) {
  for (const view of workbenchViews) {
    view.classList.toggle("active", view.id === viewId);
  }
  for (const item of subnavItems) {
    item.classList.toggle("active", item.dataset.viewTarget === viewId);
  }
}

function activateMainView(viewId) {
  for (const view of mainViews) {
    view.classList.toggle("active", view.id === viewId);
  }
  for (const item of mainNavItems) {
    item.classList.toggle("active", item.dataset.mainTarget === viewId);
  }
  if (viewId === "asset-library-view") {
    loadAsset(currentAssetKey);
  }
  if (viewId === "competitor-activity-view") {
    loadCompetitorAccounts();
    loadCompetitorOptions();
    loadCompetitorWorks();
  }
  if (viewId === "profile-maintenance-view") {
    loadKolProfileBatches();
    loadKolProfiles();
  }
}

for (const item of mainNavItems) {
  item.addEventListener("click", () => activateMainView(item.dataset.mainTarget));
}

for (const item of subnavItems) {
  item.addEventListener("click", () => activateView(item.dataset.viewTarget));
}

function renderFlow(nodes) {
  flowList.innerHTML = nodes.map(node => {
    const metrics = Object.entries(node.metrics || {}).map(([key, value]) => `<span class="chip metric-chip">${key}: ${value}</span>`).join("");
    const outputs = node.output_tables.map(item => `<span class="chip">${item}</span>`).join("");
    return `
      <article class="flow-node">
        <small>${String(node.order).padStart(2, "0")} / ${node.function_name}</small>
        <strong>${node.title}</strong>
        <p>${node.desc}</p>
        <div class="flow-tags">${outputs}</div>
        <p>${node.rules.join("；")}</p>
        <div class="flow-metrics">${metrics || '<span class="chip">暂无批次指标</span>'}</div>
      </article>
    `;
  }).join("");
}

async function loadFlow() {
  const suffix = selectedBatchId ? `?batch_id=${selectedBatchId}` : "";
  const payload = await api(`/api/etl/flow${suffix}`);
  renderFlow(payload.nodes);
}

function renderBackups(backups) {
  backupList.innerHTML = (backups || []).slice(0, 5).map(backup => `<span class="chip">${backup.name}</span>`).join("");
}

async function loadScript() {
  const payload = await api("/api/etl/script");
  scriptEditor.value = payload.content;
  scriptMeta.textContent = `${payload.path} / ${(payload.size / 1024).toFixed(1)} KB / ${payload.updated_at}`;
  renderBackups(payload.backups);
}

document.querySelector("#refresh-flow").addEventListener("click", loadFlow);

document.querySelector("#reload-script").addEventListener("click", loadScript);

document.querySelector("#save-script").addEventListener("click", async () => {
  scriptMessage.textContent = "保存中...";
  try {
    const payload = await api("/api/etl/script", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: scriptEditor.value }),
    });
    scriptMessage.textContent = "已保存，旧脚本已备份。";
    scriptMeta.textContent = `${payload.path} / ${(payload.size / 1024).toFixed(1)} KB / ${payload.updated_at}`;
    renderBackups(payload.backups);
  } catch (error) {
    scriptMessage.textContent = error.message;
  }
});

document.querySelector("#test-script").addEventListener("click", async () => {
  if (!selectedBatchId) return;
  scriptMessage.textContent = "试跑中...";
  const task = await api("/api/etl/script/test-run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ batch_id: selectedBatchId }),
  });
  scriptMessage.textContent = task.status === "success" ? "试跑成功，结果已更新。" : "试跑失败，请查看错误信息。";
  await selectTask(task.batch_id);
});

function renderAssetTable(payload) {
  assetTitle.textContent = payload.label;
  assetState.total = payload.total;
  const startRow = payload.total ? assetState.offset + 1 : 0;
  const endRow = Math.min(assetState.offset + pageSize, payload.total);
  assetMeta.textContent = `${payload.total} 条资产，当前显示 ${startRow}-${endRow} 条`;
  renderBusinessTable(assetTable, payload);
  renderPager(assetPager, assetState, () => loadAsset(currentAssetKey));
}

async function loadAsset(assetKey = currentAssetKey) {
  currentAssetKey = assetKey;
  for (const tab of assetTabs) {
    tab.classList.toggle("active", tab.dataset.assetKey === assetKey);
  }
  const params = new URLSearchParams({ limit: String(pageSize), offset: String(assetState.offset) });
  if (assetSearchInput.value.trim()) params.set("q", assetSearchInput.value.trim());
  try {
    const payload = await api(`/api/assets/${assetKey}?${params.toString()}`);
    renderAssetTable(payload);
  } catch (error) {
    assetTitle.textContent = "资产库加载失败";
    assetMeta.textContent = "请确认 PostgreSQL 已启动，且 DATABASE_URL 指向正确的本地数据库。";
    assetTable.innerHTML = `<tbody><tr><td>${error.message}</td></tr></tbody>`;
  }
}

for (const tab of assetTabs) {
  tab.addEventListener("click", () => {
    assetState.offset = 0;
    loadAsset(tab.dataset.assetKey);
  });
}

assetSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  assetState.offset = 0;
  loadAsset(currentAssetKey);
});

exportAssetButton.addEventListener("click", () => {
  const params = new URLSearchParams();
  if (assetSearchInput.value.trim()) params.set("q", assetSearchInput.value.trim());
  const suffix = params.toString() ? `?${params.toString()}` : "";
  downloadExcel(`/api/assets/${currentAssetKey}/export${suffix}`);
});

function renderBusinessTable(table, payload) {
  const head = `<thead><tr>${payload.columns.map(column => `<th>${column.label}</th>`).join("")}</tr></thead>`;
  const rows = payload.rows.map(row => `
    <tr>${payload.columns.map(column => {
      const value = row[column.key] ?? "";
      if (column.key.endsWith("_url") || column.key === "video_url") {
        return `<td>${value ? `<a href="${value}" target="_blank" rel="noreferrer">打开链接</a>` : ""}</td>`;
      }
      return `<td>${value}</td>`;
    }).join("")}</tr>
  `).join("");
  table.innerHTML = `${head}<tbody>${rows}</tbody>`;
}

function activateCompetitorView(viewId) {
  for (const view of competitorViews) {
    view.classList.toggle("active", view.id === viewId);
  }
  for (const tab of competitorTabs) {
    tab.classList.toggle("active", tab.dataset.competitorTarget === viewId);
  }
  if (viewId === "competitor-accounts-view") {
    loadCompetitorAccounts();
  }
  if (viewId === "competitor-works-view") {
    loadCompetitorOptions();
    loadCompetitorWorks();
  }
}

for (const tab of competitorTabs) {
  tab.addEventListener("click", () => activateCompetitorView(tab.dataset.competitorTarget));
}

async function loadCompetitorAccounts() {
  const params = new URLSearchParams({ limit: String(pageSize), offset: String(competitorAccountState.offset) });
  if (competitorAccountSearchInput.value.trim()) params.set("q", competitorAccountSearchInput.value.trim());
  try {
    const payload = await api(`/api/competitors/accounts?${params.toString()}`);
    competitorAccountState.total = payload.total;
    const startRow = payload.total ? competitorAccountState.offset + 1 : 0;
    const endRow = Math.min(competitorAccountState.offset + pageSize, payload.total);
    competitorAccountTitle.textContent = payload.label;
    competitorAccountMeta.textContent = `${payload.total} 个账号，当前显示 ${startRow}-${endRow} 个`;
    renderBusinessTable(competitorAccountTable, payload);
    renderPager(competitorAccountPager, competitorAccountState, loadCompetitorAccounts);
  } catch (error) {
    competitorAccountTitle.textContent = "竞品账号库加载失败";
    competitorAccountMeta.textContent = "请确认 PostgreSQL 已启动，且竞品账号表已入库。";
    competitorAccountTable.innerHTML = `<tbody><tr><td>${error.message}</td></tr></tbody>`;
  }
}

async function loadCompetitorOptions() {
  try {
    const payload = await api("/api/competitors/options");
    const currentBrand = competitorBrandFilter.value;
    const currentType = competitorAccountTypeFilter.value;
    competitorBrandFilter.innerHTML = '<option value="">全部品牌</option>' +
      payload.brands.map(item => `<option value="${item}">${item}</option>`).join("");
    competitorAccountTypeFilter.innerHTML = '<option value="">全部账号类型</option>' +
      payload.account_types.map(item => `<option value="${item}">${item}</option>`).join("");
    competitorBrandFilter.value = currentBrand;
    competitorAccountTypeFilter.value = currentType;
  } catch {
    // 过滤项加载失败不阻断作品库主体展示。
  }
}

async function loadCompetitorWorks() {
  const params = new URLSearchParams({ limit: String(pageSize), offset: String(competitorWorkState.offset) });
  if (competitorWorkSearchInput.value.trim()) params.set("q", competitorWorkSearchInput.value.trim());
  if (competitorBrandFilter.value) params.set("brand_name", competitorBrandFilter.value);
  if (competitorAccountTypeFilter.value) params.set("account_type", competitorAccountTypeFilter.value);
  if (competitorStartDate.value) params.set("start_date", competitorStartDate.value);
  if (competitorEndDate.value) params.set("end_date", competitorEndDate.value);
  try {
    const payload = await api(`/api/competitors/works?${params.toString()}`);
    competitorWorkState.total = payload.total;
    const startRow = payload.total ? competitorWorkState.offset + 1 : 0;
    const endRow = Math.min(competitorWorkState.offset + pageSize, payload.total);
    competitorWorkTitle.textContent = payload.label;
    competitorWorkMeta.textContent = `${payload.total} 条作品，当前显示 ${startRow}-${endRow} 条`;
    renderBusinessTable(competitorWorkTable, payload);
    renderPager(competitorWorkPager, competitorWorkState, loadCompetitorWorks);
  } catch (error) {
    competitorWorkTitle.textContent = "竞品作品库加载失败";
    competitorWorkMeta.textContent = "请确认 PostgreSQL 已启动，且竞品作品表已入库。";
    competitorWorkTable.innerHTML = `<tbody><tr><td>${error.message}</td></tr></tbody>`;
  }
}

competitorAccountSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  competitorAccountState.offset = 0;
  loadCompetitorAccounts();
});

competitorWorkFilterForm.addEventListener("submit", (event) => {
  event.preventDefault();
  competitorWorkState.offset = 0;
  loadCompetitorWorks();
});

exportCompetitorAccountsButton.addEventListener("click", () => {
  const params = new URLSearchParams();
  if (competitorAccountSearchInput.value.trim()) params.set("q", competitorAccountSearchInput.value.trim());
  const suffix = params.toString() ? `?${params.toString()}` : "";
  downloadExcel(`/api/competitors/accounts/export${suffix}`);
});

exportCompetitorWorksButton.addEventListener("click", () => {
  const params = new URLSearchParams();
  if (competitorWorkSearchInput.value.trim()) params.set("q", competitorWorkSearchInput.value.trim());
  if (competitorBrandFilter.value) params.set("brand_name", competitorBrandFilter.value);
  if (competitorAccountTypeFilter.value) params.set("account_type", competitorAccountTypeFilter.value);
  if (competitorStartDate.value) params.set("start_date", competitorStartDate.value);
  if (competitorEndDate.value) params.set("end_date", competitorEndDate.value);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  downloadExcel(`/api/competitors/works/export${suffix}`);
});

for (const button of document.querySelectorAll(".competitor-range")) {
  button.addEventListener("click", () => {
    const days = Number(button.dataset.days || 0);
    if (!days) {
      competitorStartDate.value = "";
      competitorEndDate.value = "";
    } else {
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - days + 1);
      competitorStartDate.value = start.toISOString().slice(0, 10);
      competitorEndDate.value = end.toISOString().slice(0, 10);
    }
    competitorWorkState.offset = 0;
    loadCompetitorWorks();
  });
}

function activateProfileView(viewId) {
  for (const view of profileViews) {
    view.classList.toggle("active", view.id === viewId);
  }
  for (const tab of profileTabs) {
    tab.classList.toggle("active", tab.dataset.profileTarget === viewId);
  }
  if (viewId === "kol-profile-view") {
    loadKolProfileBatches();
    loadKolProfiles();
  }
  if (viewId === "comment-user-profile-view") {
    loadCommentUserProfileBatches();
    loadCommentUserProfiles();
  }
}

for (const tab of profileTabs) {
  tab.addEventListener("click", () => activateProfileView(tab.dataset.profileTarget));
}

async function loadKolProfileBatches() {
  try {
    const payload = await api("/api/profiles/kols/batches");
    const currentBatch = kolProfileBatchFilter.value;
    kolProfileBatchFilter.innerHTML = '<option value="">全部批次</option>' +
      payload.batches.map(item => `<option value="${item}">${item}</option>`).join("");
    kolProfileBatchFilter.value = currentBatch;
  } catch {
    // 批次为空或数据库未初始化时，不阻断画像主表展示。
  }
}

async function loadKolProfiles() {
  const params = new URLSearchParams({ limit: String(pageSize), offset: String(kolProfileState.offset) });
  if (kolProfileSearchInput.value.trim()) params.set("q", kolProfileSearchInput.value.trim());
  if (kolProfileBatchFilter.value) params.set("profile_batch", kolProfileBatchFilter.value);
  try {
    const payload = await api(`/api/profiles/kols?${params.toString()}`);
    kolProfileState.total = payload.total;
    const startRow = payload.total ? kolProfileState.offset + 1 : 0;
    const endRow = Math.min(kolProfileState.offset + pageSize, payload.total);
    kolProfileTitle.textContent = payload.label;
    kolProfileMeta.textContent = `${payload.total} 条画像，当前显示 ${startRow}-${endRow} 条`;
    renderBusinessTable(kolProfileTable, payload);
    renderPager(kolProfilePager, kolProfileState, loadKolProfiles);
  } catch (error) {
    kolProfileTitle.textContent = "KOL画像加载失败";
    kolProfileMeta.textContent = "请确认 PostgreSQL 已启动，且 KOL画像表已初始化。";
    kolProfileTable.innerHTML = `<tbody><tr><td>${error.message}</td></tr></tbody>`;
  }
}

exportKolSamplesButton.addEventListener("click", () => {
  const days = Math.max(1, Number(kolSampleDays.value || 7));
  downloadExcel(`/api/profiles/kols/samples/export?days=${days}`);
});

kolProfileUploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  kolProfileUploadMessage.textContent = "正在上传...";
  const formData = new FormData(kolProfileUploadForm);
  try {
    const payload = await api("/api/profiles/kols/upload", { method: "POST", body: formData });
    kolProfileUploadMessage.textContent = `已上传 ${payload.loaded} 条KOL画像`;
    kolProfileUploadForm.reset();
    kolProfileState.offset = 0;
    await loadKolProfileBatches();
    await loadKolProfiles();
  } catch (error) {
    kolProfileUploadMessage.textContent = error.message;
  }
});

kolProfileSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  kolProfileState.offset = 0;
  loadKolProfiles();
});

async function loadCommentUserProfileBatches() {
  try {
    const payload = await api("/api/profiles/comment-users/batches");
    const currentBatch = commentUserProfileBatchFilter.value;
    commentUserProfileBatchFilter.innerHTML = '<option value="">全部批次</option>' +
      payload.batches.map(item => `<option value="${item}">${item}</option>`).join("");
    commentUserProfileBatchFilter.value = currentBatch;
  } catch {
    // 批次为空或数据库未初始化时，不阻断画像主表展示。
  }
}

async function loadCommentUserProfiles() {
  const params = new URLSearchParams({ limit: String(pageSize), offset: String(commentUserProfileState.offset) });
  if (commentUserProfileSearchInput.value.trim()) params.set("q", commentUserProfileSearchInput.value.trim());
  if (commentUserProfileBatchFilter.value) params.set("profile_batch", commentUserProfileBatchFilter.value);
  try {
    const payload = await api(`/api/profiles/comment-users?${params.toString()}`);
    commentUserProfileState.total = payload.total;
    const startRow = payload.total ? commentUserProfileState.offset + 1 : 0;
    const endRow = Math.min(commentUserProfileState.offset + pageSize, payload.total);
    commentUserProfileTitle.textContent = payload.label;
    commentUserProfileMeta.textContent = `${payload.total} 条画像，当前显示 ${startRow}-${endRow} 条`;
    renderBusinessTable(commentUserProfileTable, payload);
    renderPager(commentUserProfilePager, commentUserProfileState, loadCommentUserProfiles);
  } catch (error) {
    commentUserProfileTitle.textContent = "评论用户画像加载失败";
    commentUserProfileMeta.textContent = "请确认 PostgreSQL 已启动，且评论用户画像表已初始化。";
    commentUserProfileTable.innerHTML = `<tbody><tr><td>${error.message}</td></tr></tbody>`;
  }
}

exportCommentUserSamplesButton.addEventListener("click", () => {
  downloadExcel("/api/profiles/comment-users/samples/export");
});

commentUserProfileUploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  commentUserProfileUploadMessage.textContent = "正在上传...";
  const formData = new FormData(commentUserProfileUploadForm);
  try {
    const payload = await api("/api/profiles/comment-users/upload", { method: "POST", body: formData });
    commentUserProfileUploadMessage.textContent =
      `已上传 ${payload.raw_loaded} 条LLM结果，生成 ${payload.profiles_loaded} 条用户画像`;
    commentUserProfileUploadForm.reset();
    commentUserProfileState.offset = 0;
    await loadCommentUserProfileBatches();
    await loadCommentUserProfiles();
  } catch (error) {
    commentUserProfileUploadMessage.textContent = error.message;
  }
});

commentUserProfileSearchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  commentUserProfileState.offset = 0;
  loadCommentUserProfiles();
});

async function boot() {
  await loadTasks();
  await loadFlow();
  await loadScript();
  await loadAsset();
}

boot();
