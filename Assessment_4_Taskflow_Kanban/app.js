/**
 * ==========================================================================
 * TASKFLOW — MODULAR KANBAN CONTROLLER (app.js)
 * Features:
 * 1. LocalStorage State Persistence (Tasks, Theme, User Account, Activity Log)
 * 2. Full CRUD Task Operations + Overdue Date Detection
 * 3. Smooth HTML5 Drag-and-Drop between columns
 * 4. Custom Priority Filter Dropdown + Live Search + Overdue Toggle
 * ==========================================================================
 */

const STORAGE_KEYS = {
  TASKS: "taskflow_tasks_v1",
  THEME: "taskflow_theme_v1",
  PROFILE: "taskflow_profile_v1",
  ACTIVITY: "taskflow_activity_v1"
};

/* Helper to generate relative YYYY-MM-DD dates for sample data */
function getRelativeDate(offsetDays) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().split("T")[0];
}

/* Assessment 4 Required Sample Data (with Due Dates for Bonus Challenge) */
const SAMPLE_TASKS = [
  {
    id: 1,
    title: "Design homepage",
    desc: "Create wireframes",
    priority: "High",
    status: "todo",
    dueDate: getRelativeDate(-1) // Yesterday -> demonstrates Vibrant Red Overdue state immediately
  },
  {
    id: 2,
    title: "Setup CI/CD",
    desc: "GitHub Actions pipeline",
    priority: "Medium",
    status: "inprogress",
    dueDate: getRelativeDate(3)
  },
  {
    id: 3,
    title: "Write API docs",
    desc: "OpenAPI spec",
    priority: "Low",
    status: "review",
    dueDate: getRelativeDate(5)
  }
];

const DEFAULT_PROFILE = {
  name: "User Account",
  workspace: "Personal Workspace",
  initials: "UA"
};

/* Application State */
let state = {
  tasks: [],
  activity: [],
  profile: { ...DEFAULT_PROFILE },
  selectedPriority: "all",
  overdueOnly: false,
  searchQuery: "",
  draggedTaskId: null,
  activeColumnMenuStatus: null
};

/* ==========================================================================
   1. INITIALIZATION & LOCALSTORAGE PERSISTENCE
   ========================================================================== */
function loadState() {
  try {
    const savedTasks = localStorage.getItem(STORAGE_KEYS.TASKS);
    state.tasks = savedTasks ? JSON.parse(savedTasks) : structuredClone(SAMPLE_TASKS);

    const savedProfile = localStorage.getItem(STORAGE_KEYS.PROFILE);
    state.profile = savedProfile ? JSON.parse(savedProfile) : { ...DEFAULT_PROFILE };

    const savedActivity = localStorage.getItem(STORAGE_KEYS.ACTIVITY);
    state.activity = savedActivity
      ? JSON.parse(savedActivity)
      : [{ id: Date.now(), text: "Initialized board with sample tasks", time: new Date().toLocaleTimeString() }];
  } catch (err) {
    state.tasks = structuredClone(SAMPLE_TASKS);
  }
}

function saveTasks() {
  try {
    localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(state.tasks));
    const syncLabel = document.getElementById("syncStatusLabel");
    if (syncLabel) syncLabel.textContent = `Saved ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  } catch (err) {
    // Fallback if private browsing blocks storage
  }
}

function logActivity(message) {
  const entry = {
    id: Date.now() + Math.random(),
    text: message,
    time: new Date().toLocaleString([], { hour: "2-digit", minute: "2-digit", month: "short", day: "numeric" })
  };
  state.activity.unshift(entry);
  state.activity = state.activity.slice(0, 50);
  try {
    localStorage.setItem(STORAGE_KEYS.ACTIVITY, JSON.stringify(state.activity));
  } catch (err) {}
  renderActivityLog();
}

/* ==========================================================================
   2. UTILITIES & OVERDUE DETECTION
   ========================================================================== */
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function isTaskOverdue(task) {
  if (!task.dueDate || task.status === "done") return false;
  const todayStr = new Date().toISOString().split("T")[0];
  return task.dueDate < todayStr;
}

function priorityCardClass(priority) {
  return {
    High: "card-priority-high",
    Medium: "card-priority-medium",
    Low: "card-priority-low"
  }[priority] || "card-priority-low";
}

function priorityBadgeClass(priority) {
  return {
    High: "priority-high",
    Medium: "priority-medium",
    Low: "priority-low"
  }[priority] || "priority-low";
}

/* ==========================================================================
   3. BOARD RENDERING PIPELINE
   ========================================================================== */
function renderBoard() {
  const query = state.searchQuery.trim().toLowerCase();

  // Filter tasks for display
  const filteredTasks = state.tasks.filter(task => {
    const matchesSearch =
      task.title.toLowerCase().includes(query) ||
      task.desc.toLowerCase().includes(query);

    const matchesPriority =
      state.selectedPriority === "all" || task.priority === state.selectedPriority;

    const matchesOverdue = !state.overdueOnly || isTaskOverdue(task);

    return matchesSearch && matchesPriority && matchesOverdue;
  });

  // Populate each of the 4 columns
  document.querySelectorAll("[data-list]").forEach(listEl => {
    listEl.replaceChildren();
    const status = listEl.dataset.list;
    const columnTasks = filteredTasks.filter(t => t.status === status);

    if (columnTasks.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-column-state";
      empty.textContent = "Drop tasks here or click + Add task";
      listEl.appendChild(empty);
    } else {
      columnTasks.forEach(task => {
        listEl.appendChild(createTaskCardElement(task));
      });
    }

    // Column total badge reflects total tasks in that column
    const totalInCol = state.tasks.filter(t => t.status === status).length;
    const countBadge = document.querySelector(`[data-count="${status}"]`);
    if (countBadge) countBadge.textContent = totalInCol;
  });

  updateToolbarCounters();
  renderNotifications();
}

function createTaskCardElement(task) {
  const overdue = isTaskOverdue(task);
  const card = document.createElement("article");
  card.className = `task-card ${priorityCardClass(task.priority)} ${overdue ? "card-overdue" : ""}`;
  card.setAttribute("draggable", "true");
  card.dataset.taskId = String(task.id);

  const dueDisplay = task.dueDate
    ? `<span class="due-badge">📅 ${escapeHTML(task.dueDate)}</span>`
    : `<span class="due-badge">No due date</span>`;

  card.innerHTML = `
    ${overdue ? `<div class="overdue-banner">⚠ OVERDUE TASK</div>` : ""}
    <div class="task-card-top">
      <h3 class="task-title">${escapeHTML(task.title)}</h3>
      <div class="task-actions">
        <button type="button" class="card-icon-btn" data-edit="${task.id}" title="Edit task" aria-label="Edit ${escapeHTML(task.title)}">✎</button>
        <button type="button" class="card-icon-btn" data-delete="${task.id}" title="Delete task" aria-label="Delete ${escapeHTML(task.title)}">🗑</button>
      </div>
    </div>
    <p class="task-description">${escapeHTML(task.desc)}</p>
    <div class="task-meta">
      <span class="priority ${priorityBadgeClass(task.priority)}">${escapeHTML(task.priority)}</span>
      ${dueDisplay}
    </div>
  `;

  // Drag Events on Card
  card.addEventListener("dragstart", handleDragStart);
  card.addEventListener("dragend", handleDragEnd);

  // Double-click card to edit
  card.addEventListener("dblclick", () => openTaskModal({ taskId: task.id }));

  return card;
}

function updateToolbarCounters() {
  const total = state.tasks.length;
  document.getElementById("totalTasks").textContent = `${total} ${total === 1 ? "task" : "tasks"}`;

  // Priority Dropdown live counts
  const counts = {
    all: total,
    High: state.tasks.filter(t => t.priority === "High").length,
    Medium: state.tasks.filter(t => t.priority === "Medium").length,
    Low: state.tasks.filter(t => t.priority === "Low").length
  };

  Object.entries(counts).forEach(([key, val]) => {
    const el = document.querySelector(`[data-prio-count="${key}"]`);
    if (el) el.textContent = val;
  });

  // Overdue count
  const overdueCount = state.tasks.filter(isTaskOverdue).length;
  document.getElementById("overdueCountPill").textContent = overdueCount;
}

/* ==========================================================================
   4. SMOOTH HTML5 DRAG-AND-DROP ENGINE
   ========================================================================== */
function handleDragStart(event) {
  const card = event.currentTarget;
  state.draggedTaskId = Number(card.dataset.taskId);
  card.classList.add("dragging");
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", String(state.draggedTaskId));
}

function handleDragEnd(event) {
  event.currentTarget.classList.remove("dragging");
  document.querySelectorAll(".kanban-column").forEach(col => col.classList.remove("drag-over"));
  state.draggedTaskId = null;
}

function setupColumnDropZones() {
  document.querySelectorAll(".kanban-column").forEach(column => {
    column.addEventListener("dragover", event => {
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
      column.classList.add("drag-over");
    });

    column.addEventListener("dragleave", event => {
      if (!column.contains(event.relatedTarget)) {
        column.classList.remove("drag-over");
      }
    });

    column.addEventListener("drop", event => {
      event.preventDefault();
      column.classList.remove("drag-over");

      const targetStatus = column.dataset.status;
      const taskId = state.draggedTaskId || Number(event.dataTransfer.getData("text/plain"));
      const taskIndex = state.tasks.findIndex(t => t.id === taskId);
      if (taskIndex === -1) return;

      const [movedTask] = state.tasks.splice(taskIndex, 1);
      const oldStatus = movedTask.status;
      movedTask.status = targetStatus;
      state.tasks.push(movedTask);

      saveTasks();
      renderBoard();

      if (oldStatus !== targetStatus) {
        logActivity(`Moved "${movedTask.title}" to ${targetStatus.toUpperCase()}`);
      }
    });
  });
}

/* ==========================================================================
   5. TASK CRUD MODAL OPERATIONS
   ========================================================================== */
const taskModalBackdrop = document.getElementById("taskModalBackdrop");
const taskForm = document.getElementById("taskForm");
const deleteTaskModalBtn = document.getElementById("deleteTaskModalBtn");

function openTaskModal({ taskId = null, defaultStatus = "todo" } = {}) {
  const titleEl = document.getElementById("taskModalTitle");
  const idInput = document.getElementById("taskIdInput");
  const titleInput = document.getElementById("taskTitleInput");
  const descInput = document.getElementById("taskDescInput");
  const prioInput = document.getElementById("taskPriorityInput");
  const statusInput = document.getElementById("taskStatusInput");
  const dueInput = document.getElementById("taskDueDateInput");

  if (taskId !== null) {
    const task = state.tasks.find(t => t.id === Number(taskId));
    if (!task) return;
    titleEl.textContent = "Edit Task";
    idInput.value = String(task.id);
    titleInput.value = task.title;
    descInput.value = task.desc;
    prioInput.value = task.priority;
    statusInput.value = task.status;
    dueInput.value = task.dueDate || "";
    deleteTaskModalBtn.hidden = false;
  } else {
    titleEl.textContent = "Add New Task";
    idInput.value = "";
    titleInput.value = "";
    descInput.value = "";
    prioInput.value = "Medium";
    statusInput.value = defaultStatus;
    dueInput.value = getRelativeDate(2);
    deleteTaskModalBtn.hidden = true;
  }

  taskModalBackdrop.hidden = false;
  titleInput.focus();
}

function closeTaskModal() {
  taskModalBackdrop.hidden = true;
}

taskForm.addEventListener("submit", event => {
  event.preventDefault();
  const idVal = document.getElementById("taskIdInput").value;
  const title = document.getElementById("taskTitleInput").value.trim();
  const desc = document.getElementById("taskDescInput").value.trim();
  const priority = document.getElementById("taskPriorityInput").value;
  const status = document.getElementById("taskStatusInput").value;
  const dueDate = document.getElementById("taskDueDateInput").value;

  if (!title || !desc) return;

  if (idVal) {
    const task = state.tasks.find(t => t.id === Number(idVal));
    if (task) {
      task.title = title;
      task.desc = desc;
      task.priority = priority;
      task.status = status;
      task.dueDate = dueDate;
      logActivity(`Updated task "${title}" (${priority})`);
    }
  } else {
    const newTask = {
      id: Date.now(),
      title,
      desc,
      priority,
      status,
      dueDate
    };
    state.tasks.push(newTask);
    logActivity(`Created task "${title}" in ${status.toUpperCase()}`);
  }

  saveTasks();
  renderBoard();
  closeTaskModal();
});

deleteTaskModalBtn.addEventListener("click", () => {
  const idVal = Number(document.getElementById("taskIdInput").value);
  deleteTaskById(idVal);
  closeTaskModal();
});

function deleteTaskById(taskId) {
  const target = state.tasks.find(t => t.id === Number(taskId));
  if (!target) return;
  state.tasks = state.tasks.filter(t => t.id !== Number(taskId));
  saveTasks();
  renderBoard();
  logActivity(`Deleted task "${target.title}"`);
}

/* ==========================================================================
   6. CUSTOM FILTER DROPDOWN, SEARCH & NOTIFICATIONS
   ========================================================================== */
function setupToolbarControls() {
  const searchInput = document.getElementById("searchInput");
  const dropdownTrigger = document.getElementById("priorityDropdownTrigger");
  const dropdownMenu = document.getElementById("priorityDropdownMenu");
  const activeSwatch = document.getElementById("activeFilterSwatch");
  const activeLabel = document.getElementById("activeFilterLabel");
  const overdueBtn = document.getElementById("overdueFilterBtn");

  searchInput.addEventListener("input", e => {
    state.searchQuery = e.target.value;
    renderBoard();
  });

  dropdownTrigger.addEventListener("click", e => {
    e.stopPropagation();
    const isHidden = dropdownMenu.hidden;
    dropdownMenu.hidden = !isHidden;
    dropdownTrigger.setAttribute("aria-expanded", String(isHidden));
  });

  dropdownMenu.addEventListener("click", e => {
    const option = e.target.closest("[data-priority]");
    if (!option) return;

    state.selectedPriority = option.dataset.priority;
    document.querySelectorAll(".dropdown-option").forEach(el => el.classList.remove("selected"));
    option.classList.add("selected");

    const swatchMap = {
      all: "swatch-all",
      High: "swatch-high",
      Medium: "swatch-medium",
      Low: "swatch-low"
    };
    activeSwatch.className = `swatch ${swatchMap[state.selectedPriority]}`;
    activeLabel.textContent =
      state.selectedPriority === "all" ? "All priorities" : `${state.selectedPriority} priority`;

    dropdownMenu.hidden = true;
    dropdownTrigger.setAttribute("aria-expanded", "false");
    renderBoard();
  });

  overdueBtn.addEventListener("click", () => {
    state.overdueOnly = !state.overdueOnly;
    overdueBtn.setAttribute("aria-pressed", String(state.overdueOnly));
    renderBoard();
  });
}

function renderNotifications() {
  const urgentTasks = state.tasks.filter(t => isTaskOverdue(t) || (t.priority === "High" && t.status !== "done"));
  const badge = document.getElementById("notifBadge");
  const summary = document.getElementById("notifSummaryText");
  const list = document.getElementById("notifList");

  badge.hidden = urgentTasks.length === 0;
  badge.textContent = urgentTasks.length;
  summary.textContent = `${urgentTasks.length} active`;

  list.replaceChildren();
  if (urgentTasks.length === 0) {
    list.innerHTML = `<div class="notif-item">🎉 No overdue or urgent tasks!</div>`;
    return;
  }

  urgentTasks.forEach(t => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "notif-item";
    const statusTag = isTaskOverdue(t) ? "⚠ OVERDUE" : "🔥 HIGH PRIORITY";
    btn.innerHTML = `<strong>${statusTag}: ${escapeHTML(t.title)}</strong><span>Status: ${escapeHTML(t.status.toUpperCase())}</span>`;
    btn.addEventListener("click", () => {
      document.getElementById("notifPopover").hidden = true;
      openTaskModal({ taskId: t.id });
    });
    list.appendChild(btn);
  });
}

/* ==========================================================================
   7. USER ACCOUNT, ACTIVITY DRAWER & THEME ENGINE
   ========================================================================== */
function renderProfile() {
  document.getElementById("userNameDisplay").textContent = state.profile.name;
  document.getElementById("userWorkspaceDisplay").textContent = state.profile.workspace;
  document.getElementById("breadcrumbWorkspace").textContent = state.profile.workspace;
  document.getElementById("userAvatar").textContent = state.profile.initials.toUpperCase();
}

function renderActivityLog() {
  const list = document.getElementById("activityList");
  const badge = document.getElementById("activityCountBadge");
  if (badge) badge.textContent = state.activity.length;
  if (!list) return;

  list.replaceChildren();
  state.activity.forEach(item => {
    const div = document.createElement("div");
    div.className = "activity-item";
    div.innerHTML = `<strong>${escapeHTML(item.text)}</strong><time>${escapeHTML(item.time)}</time>`;
    list.appendChild(div);
  });
}

function setupTheme() {
  const themeToggle = document.getElementById("themeToggle");
  const themeIcon = themeToggle.querySelector(".theme-icon");
  const themeLabel = themeToggle.querySelector(".theme-label");

  function applyTheme(theme) {
    const isDark = theme === "dark";
    document.documentElement.dataset.theme = theme;
    themeIcon.textContent = isDark ? "☀" : "☾";
    themeLabel.textContent = isDark ? "Light mode" : "Dark mode";
    themeToggle.setAttribute("aria-pressed", String(isDark));
  }

  const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME) === "dark" ? "dark" : "light";
  applyTheme(savedTheme);

  themeToggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(next);
    try {
      localStorage.setItem(STORAGE_KEYS.THEME, next);
    } catch (e) {}
  });
}

/* ==========================================================================
   8. GLOBAL EVENT LISTENERS
   ========================================================================== */
function setupEventListeners() {
  // Add Task buttons
  document.getElementById("addTaskButton").addEventListener("click", () => openTaskModal());
  document.querySelectorAll("[data-add]").forEach(btn => {
    btn.addEventListener("click", () => openTaskModal({ defaultStatus: btn.dataset.add }));
  });

  // Card Edit & Delete Delegation
  document.getElementById("boardGrid").addEventListener("click", e => {
    const editBtn = e.target.closest("[data-edit]");
    if (editBtn) {
      openTaskModal({ taskId: Number(editBtn.dataset.edit) });
      return;
    }
    const delBtn = e.target.closest("[data-delete]");
    if (delBtn) {
      deleteTaskById(Number(delBtn.dataset.delete));
    }
  });

  // Close Modals
  document.getElementById("closeTaskModalBtn").addEventListener("click", closeTaskModal);
  document.getElementById("cancelTaskModalBtn").addEventListener("click", closeTaskModal);

  // User Account Modal
  const profileModal = document.getElementById("profileModalBackdrop");
  document.getElementById("userProfileBtn").addEventListener("click", () => {
    document.getElementById("profileNameInput").value = state.profile.name;
    document.getElementById("profileWorkspaceInput").value = state.profile.workspace;
    document.getElementById("profileInitialsInput").value = state.profile.initials;
    profileModal.hidden = false;
  });
  document.getElementById("closeProfileModalBtn").addEventListener("click", () => (profileModal.hidden = true));
  document.getElementById("cancelProfileModalBtn").addEventListener("click", () => (profileModal.hidden = true));
  document.getElementById("profileForm").addEventListener("submit", e => {
    e.preventDefault();
    state.profile = {
      name: document.getElementById("profileNameInput").value.trim() || "User Account",
      workspace: document.getElementById("profileWorkspaceInput").value.trim() || "Personal Workspace",
      initials: (document.getElementById("profileInitialsInput").value.trim() || "UA").slice(0, 2)
    };
    try {
      localStorage.setItem(STORAGE_KEYS.PROFILE, JSON.stringify(state.profile));
    } catch (err) {}
    renderProfile();
    logActivity(`Updated User Account profile to "${state.profile.name}"`);
    profileModal.hidden = true;
  });

  // Activity Drawer
  const activityDrawer = document.getElementById("activityDrawerBackdrop");
  document.getElementById("navActivityBtn").addEventListener("click", () => {
    renderActivityLog();
    activityDrawer.hidden = false;
  });
  document.getElementById("closeActivityDrawerBtn").addEventListener("click", () => (activityDrawer.hidden = true));
  document.getElementById("clearActivityBtn").addEventListener("click", () => {
    state.activity = [];
    try {
      localStorage.removeItem(STORAGE_KEYS.ACTIVITY);
    } catch (e) {}
    renderActivityLog();
  });

  // Notifications Toggle
  document.getElementById("notifButton").addEventListener("click", e => {
    e.stopPropagation();
    const pop = document.getElementById("notifPopover");
    pop.hidden = !pop.hidden;
  });

  // Column Context Menu (···)
  const colMenu = document.getElementById("colContextMenu");
  document.querySelectorAll("[data-col-menu]").forEach(btn => {
    btn.addEventListener("click", e => {
      e.stopPropagation();
      state.activeColumnMenuStatus = btn.dataset.colMenu;
      const rect = btn.getBoundingClientRect();
      colMenu.style.top = `${rect.bottom + 6}px`;
      colMenu.style.left = `${Math.min(rect.left, window.innerWidth - 230)}px`;
      colMenu.hidden = false;
    });
  });

  colMenu.addEventListener("click", e => {
    const actionBtn = e.target.closest("[data-col-action]");
    if (!actionBtn || !state.activeColumnMenuStatus) return;
    const status = state.activeColumnMenuStatus;
    const action = actionBtn.dataset.colAction;

    if (action === "add") {
      openTaskModal({ defaultStatus: status });
    } else if (action === "sort-priority") {
      const rank = { High: 1, Medium: 2, Low: 3 };
      state.tasks.sort((a, b) => {
        if (a.status === status && b.status === status) {
          return (rank[a.priority] || 3) - (rank[b.priority] || 3);
        }
        return 0;
      });
      saveTasks();
      renderBoard();
      logActivity(`Sorted ${status.toUpperCase()} column by Priority`);
    } else if (action === "clear") {
      state.tasks = state.tasks.filter(t => t.status !== status);
      saveTasks();
      renderBoard();
      logActivity(`Cleared all tasks in ${status.toUpperCase()}`);
    }
    colMenu.hidden = true;
  });

  // Sidebar Quick Actions
  document.getElementById("resetSampleBtn").addEventListener("click", () => {
    state.tasks = structuredClone(SAMPLE_TASKS);
    saveTasks();
    renderBoard();
    logActivity("Reset board to default Assessment 4 sample tasks");
  });

  document.getElementById("exportJsonBtn").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(state.tasks, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "taskflow-board.json";
    a.click();
    URL.revokeObjectURL(url);
    logActivity("Exported board tasks as JSON");
  });

  // Global click-outside & keyboard shortcuts
  document.addEventListener("click", () => {
    document.getElementById("priorityDropdownMenu").hidden = true;
    document.getElementById("notifPopover").hidden = true;
    colMenu.hidden = true;
  });

  document.addEventListener("keydown", event => {
    if (event.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
      event.preventDefault();
      document.getElementById("searchInput").focus();
    }
    if (event.key === "Escape") {
      closeTaskModal();
      profileModal.hidden = true;
      activityDrawer.hidden = true;
      colMenu.hidden = true;
    }
  });
}

/* Boot Application */
loadState();
setupTheme();
setupColumnDropZones();
setupToolbarControls();
setupEventListeners();
renderProfile();
renderActivityLog();
renderBoard();