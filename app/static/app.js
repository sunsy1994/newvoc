let selectedBatchId = null;

const taskList = document.querySelector("#task-list");
const selectedTask = document.querySelector("#selected-task");
const runButton = document.querySelector("#run-task");
const summaryBox = document.querySelector("#summary");
const tableSelect = document.querySelector("#table-select");
const tableMeta = document.querySelector("#table-meta");
const dataTable = document.querySelector("#data-table");
const errorBox = document.querySelector("#error-box");
const uploadMessage = document.querySelector("#upload-message");
const flowList = document.querySelector("#flow-list");
const scriptEditor = document.querySelector("#script-editor");
const scriptMeta = document.querySelector("#script-meta");
const scriptMessage = document.querySelector("#script-message");
const backupList = document.querySelector("#backup-list");
const testScriptButton = document.querySelector("#test-script");

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json();
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
  try {
    const payload = await api(`/api/tasks/${batchId}/tables`);
    for (const table of payload.tables) {
      const option = document.createElement("option");
      option.value = table;
      option.textContent = table;
      tableSelect.appendChild(option);
    }
    if (payload.tables.length) {
      await loadTable(batchId, payload.tables[0]);
    }
  } catch {
    tableMeta.textContent = "该批次暂无输出表。";
  }
}

async function loadTable(batchId, tableName) {
  if (!tableName) return;
  const payload = await api(`/api/tasks/${batchId}/tables/${tableName}?limit=50`);
  tableMeta.textContent = `${payload.total} 行，当前预览前 50 行`;
  const head = `<thead><tr>${payload.columns.map(column => `<th>${column}</th>`).join("")}</tr></thead>`;
  const rows = payload.rows.map(row => `
    <tr>${payload.columns.map(column => `<td>${row[column] ?? ""}</td>`).join("")}</tr>
  `).join("");
  dataTable.innerHTML = `${head}<tbody>${rows}</tbody>`;
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
  loadTable(selectedBatchId, tableSelect.value);
});

document.querySelector("#refresh-tasks").addEventListener("click", loadTasks);

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

async function boot() {
  await loadTasks();
  await loadFlow();
  await loadScript();
}

boot();
