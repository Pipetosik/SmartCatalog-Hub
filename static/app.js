// SmartCatalog Hub Client
let allApps = [];
let allCategories = [];
let userData = { favorites: [], launch_stats: {}, settings: {} };
let activeCategory = 'all';
let searchQuery = '';
let frequentSort = 'launches';
let focusedIndex = -1;
let catalogVersion = null;
let activeContextApp = null;
let runningApps = {};
let playtimeStats = null;
let workspacesList = [];
let clipboardHistory = [];

// DOM Elements
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const categoriesBar = document.getElementById('categoriesBar');
const appsGrid = document.getElementById('appsGrid');
const emptyState = document.getElementById('emptyState');
const currentCategoryTitle = document.getElementById('currentCategoryTitle');
const resultCount = document.getElementById('resultCount');
const allCount = document.getElementById('allCount');
const frequentCount = document.getElementById('frequentCount');
const favoritesCount = document.getElementById('favoritesCount');
const statsSubtitle = document.getElementById('statsSubtitle');
const footerStats = document.getElementById('footerStats');
const statusText = document.getElementById('statusText');
const sortSelector = document.getElementById('sortSelector');
const openPlayniteBtn = document.getElementById('openPlayniteBtn');
const openFolderBtn = document.getElementById('openFolderBtn');
const rescanBtn = document.getElementById('rescanBtn');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettingsBtn = document.getElementById('closeSettingsBtn');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const startupTabSelect = document.getElementById('startupTabSelect');
const toastHub = document.getElementById('toastHub');

// Running processes filter on 'Все программы'
const filterRunningBtn = document.getElementById('filterRunningBtn');
const runningFilterBadge = document.getElementById('runningFilterBadge');
let isFilterRunningActive = false;

// Header Action Modals
const openWorkspacesBtn = document.getElementById('openWorkspacesBtn');
const workspacesModal = document.getElementById('workspacesModal');
const closeWorkspacesBtn = document.getElementById('closeWorkspacesBtn');
const closeWorkspacesBottomBtn = document.getElementById('closeWorkspacesBottomBtn');
const workspacesListContainer = document.getElementById('workspacesListContainer');
const workspacesListView = document.getElementById('workspacesListView');
const workspaceEditorView = document.getElementById('workspaceEditorView');
const createNewWorkspaceBtn = document.getElementById('createNewWorkspaceBtn');
const cancelWsEditorTopBtn = document.getElementById('cancelWsEditorTopBtn');
const wsEditorHeading = document.getElementById('wsEditorHeading');
const wsEditId = document.getElementById('wsEditId');
const wsEditName = document.getElementById('wsEditName');
const wsEditIcon = document.getElementById('wsEditIcon');
const wsEditDesc = document.getElementById('wsEditDesc');
const wsSelectedCount = document.getElementById('wsSelectedCount');
const wsSelectedChipsBar = document.getElementById('wsSelectedChipsBar');
const wsAppSearchInput = document.getElementById('wsAppSearchInput');
const wsAppsPickerList = document.getElementById('wsAppsPickerList');
const saveWorkspaceSubmitBtn = document.getElementById('saveWorkspaceSubmitBtn');
const cancelWorkspaceEditBtn = document.getElementById('cancelWorkspaceEditBtn');
let selectedWorkspaceAppIds = new Set();

const openInsightsBtn = document.getElementById('openInsightsBtn');
const insightsModal = document.getElementById('insightsModal');
const closeInsightsBtn = document.getElementById('closeInsightsBtn');
const closeInsightsBottomBtn = document.getElementById('closeInsightsBottomBtn');
const insightTotalTime = document.getElementById('insightTotalTime');
const insightTodayTime = document.getElementById('insightTodayTime');
const insightTotalLaunches = document.getElementById('insightTotalLaunches');
const insightTopApp = document.getElementById('insightTopApp');
const insightTopAppTime = document.getElementById('insightTopAppTime');
const insightCategoryBars = document.getElementById('insightCategoryBars');
const insightTopAppsList = document.getElementById('insightTopAppsList');

// System Monitor Elements
const sysMonitorPill = document.getElementById('sysMonitorPill');
const sysHeaderCpu = document.getElementById('sysHeaderCpu');
const sysHeaderRam = document.getElementById('sysHeaderRam');
const systemMonitorModal = document.getElementById('systemMonitorModal');
const closeSysMonitorBtn = document.getElementById('closeSysMonitorBtn');
const closeSysMonitorBottomBtn = document.getElementById('closeSysMonitorBottomBtn');
const refreshSysStatsBtn = document.getElementById('refreshSysStatsBtn');
const sysGaugeCpuVal = document.getElementById('sysGaugeCpuVal');
const sysGaugeCpuBar = document.getElementById('sysGaugeCpuBar');
const sysGaugeCpuSub = document.getElementById('sysGaugeCpuSub');
const sysGaugeRamVal = document.getElementById('sysGaugeRamVal');
const sysGaugeRamBar = document.getElementById('sysGaugeRamBar');
const sysGaugeRamSub = document.getElementById('sysGaugeRamSub');
const sysGaugeDiskVal = document.getElementById('sysGaugeDiskVal');
const sysGaugeDiskBar = document.getElementById('sysGaugeDiskBar');
const sysGaugeDiskSub = document.getElementById('sysGaugeDiskSub');
const sysTopRamList = document.getElementById('sysTopRamList');
const sysTopCpuList = document.getElementById('sysTopCpuList');
let sysStatsTimer = null;

// Clipboard & Snippets Elements
const openClipboardBtn = document.getElementById('openClipboardBtn');
const clipboardModal = document.getElementById('clipboardModal');
const closeClipboardBtn = document.getElementById('closeClipboardBtn');
const closeClipboardBottomBtn = document.getElementById('closeClipboardBottomBtn');
const tabClipHistoryBtn = document.getElementById('tabClipHistoryBtn');
const tabClipSnippetsBtn = document.getElementById('tabClipSnippetsBtn');
const clipHistoryCount = document.getElementById('clipHistoryCount');
const clipSnippetsCount = document.getElementById('clipSnippetsCount');
const clipHistoryView = document.getElementById('clipHistoryView');
const clipSnippetsView = document.getElementById('clipSnippetsView');
const snippetEditorView = document.getElementById('snippetEditorView');
const clipboardSearchInput = document.getElementById('clipboardSearchInput');
const clearClipboardBtn = document.getElementById('clearClipboardBtn');
const clipboardItemsContainer = document.getElementById('clipboardItemsContainer');
const snippetsSearchInput = document.getElementById('snippetsSearchInput');
const newSnippetBtn = document.getElementById('newSnippetBtn');
const snippetChipsBar = document.getElementById('snippetChipsBar');
const snippetsListContainer = document.getElementById('snippetsListContainer');
const cancelSnippetTopBtn = document.getElementById('cancelSnippetTopBtn');
const snippetEditorHeading = document.getElementById('snippetEditorHeading');
const snipEditId = document.getElementById('snipEditId');
const snipEditTitle = document.getElementById('snipEditTitle');
const snipEditCategory = document.getElementById('snipEditCategory');
const snipEditContent = document.getElementById('snipEditContent');
const saveSnippetSubmitBtn = document.getElementById('saveSnippetSubmitBtn');
const cancelSnippetBtn = document.getElementById('cancelSnippetBtn');
let allSnippets = [];
let activeSnippetCategory = 'all';

// View Mode (Compact / Full) Elements
const toggleViewModeBtn = document.getElementById('toggleViewModeBtn');
const viewModeSelect = document.getElementById('viewModeSelect');
let isCompactMode = false;

// Settings DOM Elements
const themeSelect = document.getElementById('themeSelect');
const enableNewBadgeToggle = document.getElementById('enableNewBadgeToggle');
const badgePeriodGroup = document.getElementById('badgePeriodGroup');
const badgePeriodSelect = document.getElementById('badgePeriodSelect');
const hotkeySelect = document.getElementById('hotkeySelect');
const enableTrayToggle = document.getElementById('enableTrayToggle');
const enablePlaytimeToggle = document.getElementById('enablePlaytimeToggle');
const enableLiveStatusToggle = document.getElementById('enableLiveStatusToggle');
const enableClipboardToggle = document.getElementById('enableClipboardToggle');
const hiddenAppsContainer = document.getElementById('hiddenAppsContainer');

// Context Menu DOM Elements
const cardContextMenu = document.getElementById('cardContextMenu');
const ctxRunAdmin = document.getElementById('ctxRunAdmin');
const ctxOpenFolder = document.getElementById('ctxOpenFolder');
const ctxToggleFavorite = document.getElementById('ctxToggleFavorite');
const ctxFavText = document.getElementById('ctxFavText');
const ctxCategorySubmenu = document.getElementById('ctxCategorySubmenu');
const ctxAddToWorkspaceWrap = document.getElementById('ctxAddToWorkspaceWrap');
const ctxWorkspaceSubmenu = document.getElementById('ctxWorkspaceSubmenu');
const ctxKillTask = document.getElementById('ctxKillTask');
const ctxHideApp = document.getElementById('ctxHideApp');

// SVG Icon Assets (vector Lucide stroke style)
const ICONS = {
  all: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>`,
  frequent: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
  favorites: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`,
  starFilled: `<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`,
  starEmpty: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`,
  folder: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`,
  flame: `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>`,

  // Category vector map
  "01": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
  "02": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,
  "03": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>`,
  "04": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1 4-10z"/></svg>`,
  "05": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  "06": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>`,
  "07": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>`,
  "08": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
  "09": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/><rect x="2" y="6" width="20" height="12" rx="4"/></svg>`,
  "10": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>`,
  "11": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  "12": `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`
};

function getCategorySvg(catName) {
  const match = catName.match(/^(\d{2})/);
  if (match && ICONS[match[1]]) {
    return ICONS[match[1]];
  }
  return ICONS.folder;
}

// Keyboard Layout Auto-Correction (EN <-> RU) & Acronyms
const EN_TO_RU = {
  'q':'й', 'w':'ц', 'e':'у', 'r':'к', 't':'е', 'y':'н', 'u':'г', 'i':'ш', 'o':'щ', 'p':'з', '[':'х', ']':'ъ',
  'a':'ф', 's':'ы', 'd':'в', 'f':'а', 'g':'п', 'h':'р', 'j':'о', 'k':'л', 'l':'д', ';':'ж', "'":'э',
  'z':'я', 'x':'ч', 'c':'с', 'v':'м', 'b':'и', 'n':'т', 'm':'ь', ',':'б', '.':'ю', '`':'ё'
};

const RU_TO_EN = {};
for (const [en, ru] of Object.entries(EN_TO_RU)) {
  RU_TO_EN[ru] = en;
}

function convertLayout(str) {
  const s = str.toLowerCase();
  let enRu = '';
  let hasEn = false;
  for (const ch of s) {
    if (EN_TO_RU[ch]) {
      enRu += EN_TO_RU[ch];
      hasEn = true;
    } else {
      enRu += ch;
    }
  }

  let ruEn = '';
  let hasRu = false;
  for (const ch of s) {
    if (RU_TO_EN[ch]) {
      ruEn += RU_TO_EN[ch];
      hasRu = true;
    } else {
      ruEn += ch;
    }
  }

  return {
    original: s,
    enRu: hasEn ? enRu : null,
    ruEn: hasRu ? ruEn : null
  };
}

const HARDCODED_ACRONYMS = {
  'дс': 'discord',
  'ds': 'discord',
  'вск': 'visual studio code',
  'vsc': 'visual studio code',
  'vs': 'visual studio',
  'вс': 'visual studio',
  'тг': 'telegram',
  'tg': 'telegram',
  'ям': 'яндекс музыка',
  'ym': 'яндекс музыка',
  'пс': 'powershell',
  'ps': 'powershell',
  'cmd': 'командная строка',
  'кмд': 'командная строка',
  'wsl': 'wsl',
  'всл': 'wsl',
  'тс': 'teamspeak',
  'тс3': 'teamspeak',
  'гх': 'github',
  'фш': 'photoshop',
  'ссд': 'samsung magician',
  'дрг': 'deep rock'
};

const SOUND_TRANSLIT = {
  'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo', 'ж':'zh',
  'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l', 'м':'m', 'н':'n', 'о':'o',
  'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'h', 'ц':'ts',
  'ч':'ch', 'ш':'sh', 'щ':'sh', 'ъ':'', 'ы':'y', 'ь':'', 'э':'e', 'ю':'yu', 'я':'ya'
};

const PHONETIC_MAP = {
  'докер': 'docker',
  'хром': 'chrome',
  'стим': 'steam',
  'дискорд': 'discord',
  'постман': 'postman',
  'яндекс': 'yandex',
  'гугл': 'google',
  'бивер': 'dbeaver',
  'дбивер': 'dbeaver',
  'вскод': 'visual studio code',
  'код': 'code',
  'линейка': 'lineage',
  'мультерия': 'multeria',
  'десторус': 'destorus',
  'геншин': 'genshin',
  'дота': 'dota',
  'акробат': 'acrobat',
  'ворд': 'word',
  'эксель': 'excel',
  'нотион': 'notion',
  'ноут': 'note',
  'обсидиан': 'obsidian',
  'пайтон': 'python',
  'питон': 'python',
  'телеграм': 'telegram',
  'телега': 'telegram',
  'ватсап': 'whatsapp',
  'зум': 'zoom',
  'термиус': 'termius',
  'спотифай': 'spotify',
  'аида': 'aida64',
  'самсунг': 'samsung',
  'всл': 'wsl',
  'гит': 'git',
  'моба': 'mobaxterm',
  'тимс': 'teams',
  'впн': 'vpn'
};

function transliterateSound(str) {
  let res = '';
  for (const ch of str.toLowerCase()) {
    res += SOUND_TRANSLIT[ch] || ch;
  }
  return res;
}

function getSearchVariants(rawQ) {
  const { original, enRu, ruEn } = convertLayout(rawQ);
  const variants = [original, enRu, ruEn].filter(Boolean);

  if (PHONETIC_MAP[original]) {
    variants.push(PHONETIC_MAP[original]);
  }
  const soundTrans = transliterateSound(original);
  if (soundTrans && soundTrans !== original) {
    variants.push(soundTrans);
  }

  return Array.from(new Set(variants));
}

function getAppInitials(name) {
  const clean = name.replace(/[\(\)\[\]\-_.]/g, ' ').trim();
  const words = clean.split(/\s+/).filter(Boolean);
  return words.map(w => w[0].toLowerCase()).join('');
}

function scoreAppMatch(app, variants) {
  const nameLower = app.name.toLowerCase();
  const descLower = (app.description || '').toLowerCase();
  const catLower = (app.category || '').toLowerCase();
  const initials = getAppInitials(app.name);
  const aliases = (app.aliases || []).map(a => a.toLowerCase());

  let best = 0;
  for (const q of variants) {
    if (!q) continue;

    // Direct Exact Name Match
    if (nameLower === q) return 1000;
    if (nameLower.startsWith(q)) {
      best = Math.max(best, 600 - (nameLower.length - q.length));
    }

    // Direct Russian / Phonetic Alias Match (e.g. "докер" for "Docker Desktop", "хром" for "Google Chrome")
    for (const al of aliases) {
      if (al === q) {
        best = Math.max(best, 850);
      } else if (al.startsWith(q)) {
        best = Math.max(best, 650 - (al.length - q.length));
      } else if (al.includes(q)) {
        best = Math.max(best, 450 - al.indexOf(q));
      }
    }

    // Initials & Acronyms
    if (initials === q) {
      best = Math.max(best, 520);
    } else if (initials.startsWith(q) && q.length >= 2) {
      best = Math.max(best, 440);
    }

    if (HARDCODED_ACRONYMS[q] && nameLower.includes(HARDCODED_ACRONYMS[q])) {
      best = Math.max(best, 480);
    }

    // Word start matching
    const words = nameLower.split(/\s+/);
    for (const w of words) {
      if (w.startsWith(q)) {
        best = Math.max(best, 380 - (w.length - q.length));
      }
    }

    if (nameLower.includes(q)) {
      best = Math.max(best, 250 - nameLower.indexOf(q));
    }

    if (catLower.includes(q)) {
      best = Math.max(best, 140);
    }

    if (descLower.includes(q)) {
      best = Math.max(best, 90);
    }
  }

  return best;
}

// Mouse Wheel Horizontal Scroll for Categories Bar
if (categoriesBar) {
  categoriesBar.addEventListener('wheel', (e) => {
    if (e.deltaY !== 0) {
      e.preventDefault();
      categoriesBar.scrollLeft += (e.deltaY > 0 ? 80 : -80);
    } else if (e.deltaX !== 0) {
      e.preventDefault();
      categoriesBar.scrollLeft += e.deltaX;
    }
  }, { passive: false });
}

// Segmented Control for Top 15 Sort
if (sortSelector) {
  sortSelector.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sortSelector.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      frequentSort = btn.dataset.sort;
      renderApps();
    });
  });
}

// Ensure launcher window is docked to bottom center (attached to taskbar)
async function ensureBottomCenterDock(mode = null) {
  try {
    const targetMode = mode || (isCompactMode ? 'compact' : 'full');
    await fetch('/api/position_window', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: targetMode })
    });
  } catch (e) {}
}

function setViewMode(mode) {
  const container = document.querySelector('.app-container');
  if (!container) return;
  isCompactMode = (mode === 'compact');
  container.classList.toggle('view-compact', isCompactMode);
  if (viewModeSelect) viewModeSelect.value = isCompactMode ? 'compact' : 'full';
  ensureBottomCenterDock(isCompactMode ? 'compact' : 'full');
  if (isCompactMode) {
    searchInput.focus();
  }
}

function toggleViewMode() {
  const newMode = isCompactMode ? 'full' : 'compact';
  setViewMode(newMode);
  saveSetting('view_mode', newMode);
  showToast(newMode === 'compact' ? 'Компактный поиск' : 'Полный каталог', newMode === 'compact' ? 'Включен режим Raycast Mini-Dock' : 'Возврат к стандартной сетке');
}

window.addEventListener('focus', () => {
  ensureBottomCenterDock();
});

document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    ensureBottomCenterDock();
  }
});

// Theme Management & Settings
function applyTheme(theme) {
  const validThemes = ['win11', 'obsidian', 'acrylic', 'mica', 'oled'];
  const chosen = validThemes.includes(theme) ? theme : 'win11';
  document.body.className = `theme-${chosen}`;
}

function getStartupTab() {
  return localStorage.getItem('smartcatalog_startup_tab') || userData.settings?.startup_tab || 'all';
}

async function saveSetting(key, val) {
  if (!userData.settings) userData.settings = {};
  userData.settings[key] = val;
  try {
    await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value: val })
    });
  } catch (e) {}
}

function isNewApp(app) {
  if (userData.settings?.enable_new_badge === false) return false;
  const period = parseInt(userData.settings?.new_badge_period || '172800', 10);
  if (!app.added_at) return false;
  const now = Date.now() / 1000;
  return (now - app.added_at) <= period;
}

// Settings Modal
function openSettings() {
  if (!settingsModal) return;
  populateSettings();
  renderHiddenApps();
  settingsModal.style.display = 'flex';
}

function closeSettings() {
  if (!settingsModal) return;
  settingsModal.style.display = 'none';
}

function populateSettings() {
  const currentTab = getStartupTab();
  if (startupTabSelect) {
    startupTabSelect.innerHTML = `
      <option value="all">Все программы</option>
      <option value="frequent">Часто используемые (Топ 15)</option>
      <option value="favorites">Избранное</option>
    `;
    allCategories.forEach(cat => {
      const opt = document.createElement('option');
      opt.value = cat.name;
      opt.textContent = cat.name.replace(/^\d+\.\s*/, '');
      startupTabSelect.appendChild(opt);
    });
    startupTabSelect.value = currentTab;
  }

  if (viewModeSelect) {
    viewModeSelect.value = userData.settings?.view_mode || 'full';
  }

  if (themeSelect) {
    themeSelect.value = userData.settings?.theme || 'win11';
  }

  if (enableNewBadgeToggle) {
    enableNewBadgeToggle.checked = (userData.settings?.enable_new_badge !== false);
    if (badgePeriodGroup) {
      badgePeriodGroup.style.display = enableNewBadgeToggle.checked ? 'flex' : 'none';
    }
  }

  if (badgePeriodSelect) {
    badgePeriodSelect.value = String(userData.settings?.new_badge_period || '172800');
  }

  if (hotkeySelect) {
    hotkeySelect.value = userData.settings?.global_hotkey || 'alt+space';
  }

  if (enableTrayToggle) {
    enableTrayToggle.checked = (userData.settings?.enable_tray !== false);
  }

  if (enablePlaytimeToggle) {
    enablePlaytimeToggle.checked = (userData.settings?.enable_playtime_tracking !== false);
  }

  if (enableLiveStatusToggle) {
    enableLiveStatusToggle.checked = (userData.settings?.enable_live_status !== false);
  }

  if (enableClipboardToggle) {
    enableClipboardToggle.checked = (userData.settings?.enable_clipboard_history !== false);
  }
}

async function renderHiddenApps() {
  if (!hiddenAppsContainer) return;
  try {
    const res = await fetch('/api/hidden_apps');
    const hidden = await res.json();
    if (!hidden || hidden.length === 0) {
      hiddenAppsContainer.innerHTML = '<div class="hidden-empty-text">Нет скрытых программ</div>';
      return;
    }
    hiddenAppsContainer.innerHTML = '';
    hidden.forEach(app => {
      const item = document.createElement('div');
      item.className = 'hidden-app-item';
      const iconUrl = app.icon ? `${app.icon}?v=20261029_v7` : '/static/icons/default.png';
      item.innerHTML = `
        <div class="app-name-wrap">
          <img src="${iconUrl}" alt="" onerror="this.src='/static/icons/default.png'">
          <span class="hidden-name" title="${app.name}">${app.name}</span>
        </div>
        <button class="restore-btn" data-id="${app.id}">Восстановить</button>
      `;
      item.querySelector('.restore-btn').onclick = async () => {
        await unhideApp(app.id, app.name);
      };
      hiddenAppsContainer.appendChild(item);
    });
  } catch (e) {
    hiddenAppsContainer.innerHTML = '<div class="hidden-empty-text">Ошибка загрузки скрытых программ</div>';
  }
}

async function safeFetchJson(url, fallback = {}) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2500);
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) return fallback;
    return await res.json();
  } catch (e) {
    return fallback;
  }
}

// Initial Data Fetch
async function initCatalog() {
  ensureBottomCenterDock();
  setTimeout(ensureBottomCenterDock, 250);
  setTimeout(ensureBottomCenterDock, 650);

  try {
    const [appsData, catsData, userD, verData, rData, pStats] = await Promise.all([
      safeFetchJson('/api/apps', []),
      safeFetchJson('/api/categories', []),
      safeFetchJson('/api/user_data', {}),
      safeFetchJson('/api/version', { version: 1 }),
      safeFetchJson('/api/running_apps', { running: {} }),
      safeFetchJson('/api/playtime', {})
    ]);
    if (Array.isArray(appsData) && appsData.length > 0) {
      allApps = appsData;
    }
    if (Array.isArray(catsData) && catsData.length > 0) {
      allCategories = catsData;
    }
    if (userD && typeof userD === 'object') {
      userData = userD;
    }
    catalogVersion = verData?.version || 1;
    runningApps = rData?.running || {};
    playtimeStats = pStats || {};

    // Apply active theme
    applyTheme(userData.settings?.theme || 'win11');

    // Apply configured view mode (compact or full)
    const configuredViewMode = userData.settings?.view_mode || 'full';
    setViewMode(configuredViewMode);

    // Apply configured startup tab
    activeCategory = getStartupTab();

    // Populate static icons
    const iconAll = document.getElementById('iconAll');
    if (iconAll) iconAll.innerHTML = ICONS.all;
    const iconFrequent = document.getElementById('iconFrequent');
    if (iconFrequent) iconFrequent.innerHTML = ICONS.frequent;
    const iconFavorites = document.getElementById('iconFavorites');
    if (iconFavorites) iconFavorites.innerHTML = ICONS.favorites;

    renderCategories();
    renderApps();
    updateStats();

    // Start background header system stats updates
    updateHeaderSystemStats();
    setInterval(updateHeaderSystemStats, 2000);

    // URL Query Parameter handling (e.g. ?q=докер, ?tab=frequent, ?filter=running, ?modal=workspaces, ?modal=workspaces_new)
    const params = new URLSearchParams(window.location.search);
    const modeParam = params.get('mode');
    if (modeParam === 'compact') {
      setViewMode('compact');
    }
    const tabParam = params.get('tab');
    if (tabParam) {
      activeCategory = tabParam;
      document.querySelectorAll('.cat-pill').forEach(b => b.classList.toggle('active', b.dataset.cat === tabParam));
      renderApps();
    }
    const filterParam = params.get('filter');
    if (filterParam === 'running') {
      isFilterRunningActive = true;
      if (filterRunningBtn) filterRunningBtn.classList.add('active');
      renderApps();
    }
    const queryParam = params.get('q');
    if (queryParam) {
      searchInput.value = queryParam;
      searchQuery = queryParam;
      clearSearchBtn.style.display = 'flex';
      renderApps();
    }
    const modalParam = params.get('modal');
    if (modalParam === 'insights') {
      openInsightsModal();
    } else if (modalParam === 'workspaces') {
      openWorkspacesModal();
    } else if (modalParam === 'workspaces_new') {
      openWorkspacesModal();
      openWorkspaceEditor(null);
    } else if (modalParam === 'clipboard') {
      openClipboardModal();
    } else if (modalParam === 'snippets') {
      openClipboardModal();
      switchClipboardTab('snippets');
    } else if (modalParam === 'snippets_new') {
      openClipboardModal();
      switchClipboardTab('snippets');
      openSnippetEditor(null);
    } else if (modalParam === 'sys_monitor') {
      openSystemMonitorModal();
    } else if (modalParam === 'settings') {
      openSettings();
    }
  } catch (err) {
    showToast('Ошибка загрузки', err.message);
  }
}

async function reloadCatalogData() {
  try {
    const [appsData, catsData, userD, rData, pStats] = await Promise.all([
      safeFetchJson('/api/apps', null),
      safeFetchJson('/api/categories', null),
      safeFetchJson('/api/user_data', null),
      safeFetchJson('/api/running_apps', { running: {} }),
      safeFetchJson('/api/playtime', {})
    ]);
    if (Array.isArray(appsData) && appsData.length > 0) {
      allApps = appsData;
    }
    if (Array.isArray(catsData) && catsData.length > 0) {
      allCategories = catsData;
    }
    if (userD && typeof userD === 'object') {
      userData = userD;
    }
    runningApps = rData?.running || {};
    playtimeStats = pStats || {};

    renderCategories();
    renderApps();
    updateStats();
  } catch (e) {}
}

// Periodic lightweight version polling
setInterval(async () => {
  try {
    const res = await fetch('/api/version');
    const data = await res.json();
    if (catalogVersion !== null && data.version !== catalogVersion) {
      catalogVersion = data.version;
      await reloadCatalogData();
      // Silently reload in background without spamming notification toast
    } else if (catalogVersion === null) {
      catalogVersion = data.version;
    }
  } catch (e) {}
}, 3000);

function updateStats() {
  const validAppIds = new Set(allApps.map(a => a.id));
  const activeFavorites = (userData.favorites || []).filter(id => validAppIds.has(id));
  const favCount = activeFavorites.length;
  const total = allApps.length;
  const freqCount = getFrequentAppsRaw().length;

  if (allCount) allCount.textContent = total;
  if (frequentCount) frequentCount.textContent = freqCount;
  if (favoritesCount) favoritesCount.textContent = favCount;

  const text = `${total} программ • ${favCount} в избранном`;
  if (statsSubtitle) statsSubtitle.textContent = text;
  if (footerStats) footerStats.textContent = text;
}

function renderCategories() {
  const staticPills = Array.from(categoriesBar.querySelectorAll('.cat-pill[data-cat="all"], .cat-pill[data-cat="frequent"], .cat-pill[data-cat="favorites"]'));
  categoriesBar.innerHTML = '';

  staticPills.forEach(p => {
    p.classList.toggle('active', activeCategory === p.dataset.cat);
    categoriesBar.appendChild(p);
    p.onclick = () => {
      document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
      p.classList.add('active');
      activeCategory = p.dataset.cat;
      if (activeCategory !== 'all') {
        isFilterRunningActive = false;
        if (filterRunningBtn) filterRunningBtn.classList.remove('active');
      }
      focusedIndex = -1;
      renderApps();
    };
    p.oncontextmenu = (e) => {
      e.preventDefault();
      localStorage.setItem('smartcatalog_startup_tab', p.dataset.cat);
      saveSetting('startup_tab', p.dataset.cat);
      const title = p.querySelector('.cat-title')?.textContent || p.dataset.cat;
      showToast('Стартовая вкладка сохранена', `Лаунчер будет открываться с раздела: ${title}`);
    };
  });

  allCategories.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = `cat-pill ${activeCategory === cat.name ? 'active' : ''}`;
    btn.dataset.cat = cat.name;

    const displayTitle = cat.name.replace(/^\d+\.\s*/, '');
    const svgIcon = getCategorySvg(cat.name);

    btn.innerHTML = `
      <span class="cat-icon">${svgIcon}</span>
      <span class="cat-title">${displayTitle}</span>
      <span class="cat-badge">${cat.count}</span>
    `;

    btn.addEventListener('click', () => {
      document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = cat.name;
      isFilterRunningActive = false;
      if (filterRunningBtn) filterRunningBtn.classList.remove('active');
      focusedIndex = -1;
      renderApps();
    });

    btn.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      localStorage.setItem('smartcatalog_startup_tab', cat.name);
      saveSetting('startup_tab', cat.name);
      showToast('Стартовая вкладка сохранена', `Лаунчер будет открываться с раздела: ${displayTitle}`);
    });

    categoriesBar.appendChild(btn);
  });
}

function getFrequentAppsRaw() {
  const stats = userData.launch_stats || {};
  const list = allApps
    .filter(app => (stats[app.id]?.count || 0) > 0)
    .map(app => {
      const st = stats[app.id] || { count: 0, last_launched: 0 };
      return { ...app, _launches: st.count || 0, _lastLaunched: st.last_launched || 0 };
    });
  list.sort((a, b) => (b._launches - a._launches) || a.name.localeCompare(b.name, 'ru'));
  return list.slice(0, 15);
}

function formatPlaytime(seconds) {
  if (!seconds || seconds < 60) return 'меньше 1 мин';
  const mins = Math.floor(seconds / 60);
  if (mins < 60) return `${mins} мин`;
  const hours = Math.floor(mins / 60);
  const remMins = mins % 60;
  return remMins > 0 ? `${hours} ч ${remMins} мин` : `${hours} ч`;
}

function getWebSearchFallback(q) {
  const trimmed = q.trim();
  if (!trimmed) return null;

  // 1. Google
  const gMatch = trimmed.match(/^(?:g|г)\s+(.+)$/i);
  if (gMatch) {
    return {
      type: 'google',
      icon: '🔍',
      title: `Искать в Google: "${gMatch[1]}"`,
      sub: 'Открыть результаты веб-поиска в браузере по умолчанию',
      url: `https://www.google.com/search?q=${encodeURIComponent(gMatch[1])}`
    };
  }

  // 2. YouTube
  const ytMatch = trimmed.match(/^(?:yt|ют|ютуб)\s+(.+)$/i);
  if (ytMatch) {
    return {
      type: 'youtube',
      icon: '▶️',
      title: `Искать на YouTube: "${ytMatch[1]}"`,
      sub: 'Открыть поиск видео на YouTube',
      url: `https://www.youtube.com/results?search_query=${encodeURIComponent(ytMatch[1])}`
    };
  }

  // 3. GitHub
  const ghMatch = trimmed.match(/^(?:gh|гх|гитхаб)\s+(.+)$/i);
  if (ghMatch) {
    return {
      type: 'github',
      icon: '🐙',
      title: `Искать на GitHub: "${ghMatch[1]}"`,
      sub: 'Найти репозитории, исходный код и разработчиков',
      url: `https://github.com/search?q=${encodeURIComponent(ghMatch[1])}`
    };
  }

  // 4. Wildberries
  const wbMatch = trimmed.match(/^(?:wb|вб)\s+(.+)$/i);
  if (wbMatch) {
    return {
      type: 'wb',
      icon: '🟣',
      title: `Искать на Wildberries: "${wbMatch[1]}"`,
      sub: 'Открыть поиск товаров на маркетплейсе Wildberries',
      url: `https://www.wildberries.ru/catalog/0/search.aspx?search=${encodeURIComponent(wbMatch[1])}`
    };
  }

  // 5. Ozon
  const ozMatch = trimmed.match(/^(?:oz|оз|озон)\s+(.+)$/i);
  if (ozMatch) {
    return {
      type: 'ozon',
      icon: '🔵',
      title: `Искать на Ozon: "${ozMatch[1]}"`,
      sub: 'Открыть поиск товаров на Ozon',
      url: `https://www.ozon.ru/search/?text=${encodeURIComponent(ozMatch[1])}`
    };
  }

  // 6. Direct URLs
  if (/^(https?:\/\/|[a-zA-Z0-9-]+\.(?:com|ru|org|net|io|dev|app|ai|me))(\/.*)?$/i.test(trimmed)) {
    return {
      type: 'url',
      icon: '🌐',
      title: `Перейти по ссылке: ${trimmed}`,
      sub: 'Открыть веб-сайт в браузере по умолчанию',
      url: trimmed.startsWith('http') ? trimmed : `https://${trimmed}`
    };
  }

  return null;
}

function getFilteredApps() {
  const rawQ = searchQuery.trim();
  let baseList = [];

  if (activeCategory === 'all') {
    baseList = [...allApps];
    if (isFilterRunningActive) {
      baseList = baseList.filter(app => !!runningApps[app.id] && runningApps[app.id].length > 0);
    }
  } else if (activeCategory === 'frequent') {
    baseList = getFrequentAppsRaw();
    if (frequentSort === 'launches') {
      baseList.sort((a, b) => (b._launches - a._launches) || a.name.localeCompare(b.name, 'ru'));
    } else if (frequentSort === 'playtime') {
      baseList.sort((a, b) => {
        const timeA = playtimeStats?.apps_playtime?.[a.id]?.total || 0;
        const timeB = playtimeStats?.apps_playtime?.[b.id]?.total || 0;
        return (timeB - timeA) || (b._launches - a._launches);
      });
    } else if (frequentSort === 'recent') {
      baseList.sort((a, b) => (b._lastLaunched - a._lastLaunched) || (b._launches - a._launches));
    } else if (frequentSort === 'name') {
      baseList.sort((a, b) => a.name.localeCompare(b.name, 'ru'));
    }
  } else if (activeCategory === 'favorites') {
    const favSet = new Set(userData.favorites || []);
    baseList = allApps.filter(a => favSet.has(a.id));
  } else {
    baseList = allApps.filter(app => app.category === activeCategory);
  }

  if (!rawQ) return baseList;

  // Smart Layout & Phonetic Russian Variants Scoring
  const variants = getSearchVariants(rawQ);

  const scored = [];
  for (const app of baseList) {
    const score = scoreAppMatch(app, variants);
    if (score > 0) {
      scored.push({ app, score });
    }
  }

  // Sort by highest score first, then alphabet
  scored.sort((a, b) => (b.score - a.score) || a.app.name.localeCompare(b.app.name, 'ru'));
  return scored.map(item => item.app);
}

function renderApps() {
  const catalogLoader = document.getElementById('catalogLoader');
  if (allApps.length === 0) {
    if (catalogLoader) catalogLoader.style.display = 'flex';
    if (appsGrid) appsGrid.style.display = 'none';
    if (emptyState) emptyState.style.display = 'none';
    if (currentCategoryTitle) currentCategoryTitle.textContent = 'Инициализация...';
    if (resultCount) resultCount.textContent = 'Сканирование системы';
    return;
  } else {
    if (catalogLoader) catalogLoader.style.display = 'none';
    if (appsGrid) appsGrid.style.display = '';
  }

  const filtered = getFilteredApps();
  appsGrid.innerHTML = '';

  const web = searchQuery ? getWebSearchFallback(searchQuery) : null;
  if (web) {
    const wcard = document.createElement('div');
    wcard.className = 'web-search-card';
    wcard.innerHTML = `
      <div class="web-left">
        <span class="web-icon">${web.icon}</span>
        <div>
          <div class="web-title">${web.title}</div>
          <div class="web-sub">${web.sub}</div>
        </div>
      </div>
      <span class="web-action-pill">Открыть ↵</span>
    `;
    wcard.onclick = async () => {
      try {
        await fetch('/api/open_url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: web.url })
        });
      } catch (e) {}
    };
    appsGrid.appendChild(wcard);
  }

  if (sortSelector) {
    sortSelector.style.display = (activeCategory === 'frequent') ? 'flex' : 'none';
  }

  if (filterRunningBtn) {
    filterRunningBtn.style.display = (activeCategory === 'all') ? 'inline-flex' : 'none';
    filterRunningBtn.classList.toggle('active', isFilterRunningActive);
    const runCount = allApps.filter(a => !!runningApps[a.id] && runningApps[a.id].length > 0).length;
    if (runningFilterBadge) runningFilterBadge.textContent = runCount;
  }

  if (activeCategory === 'all') {
    if (isFilterRunningActive) {
      currentCategoryTitle.textContent = searchQuery ? `Запущенные: "${searchQuery}"` : 'Запущенные программы';
      resultCount.textContent = `${filtered.length} из ${allApps.length} запущены`;
    } else {
      currentCategoryTitle.textContent = searchQuery ? `Результаты поиска: "${searchQuery}"` : 'Все программы';
      resultCount.textContent = `${filtered.length} программ`;
    }
  } else if (activeCategory === 'frequent') {
    currentCategoryTitle.textContent = 'Часто запускаемые (Топ 15)';
    resultCount.textContent = `${filtered.length} программ`;
  } else if (activeCategory === 'favorites') {
    currentCategoryTitle.textContent = 'Избранные программы';
    resultCount.textContent = `${filtered.length} программ`;
  } else {
    currentCategoryTitle.textContent = activeCategory.replace(/^\d+\.\s*/, '');
    resultCount.textContent = `${filtered.length} программ`;
  }

  if (filtered.length === 0 && !web) {
    emptyState.style.display = 'flex';
    if (activeCategory === 'all' && isFilterRunningActive && !searchQuery) {
      emptyState.querySelector('h3').textContent = 'Нет запущенных программ';
      emptyState.querySelector('p').textContent = 'В данный момент ни одна из программ каталога не запущена в системе.';
    } else if (activeCategory === 'favorites' && !searchQuery) {
      emptyState.querySelector('h3').textContent = 'В избранном пока пусто';
      emptyState.querySelector('p').textContent = 'Нажмите на звездочку на карточке любой программы, чтобы добавить её в быстрый доступ';
    } else if (activeCategory === 'frequent' && !searchQuery) {
      emptyState.querySelector('h3').textContent = 'Нет часто используемых программ';
      emptyState.querySelector('p').textContent = 'Запускайте приложения из каталога, и они автоматически появятся в этом списке.';
    } else {
      emptyState.querySelector('h3').textContent = 'Ничего не найдено';
      emptyState.querySelector('p').textContent = 'Попробуйте изменить поисковый запрос или переключить категорию';
    }
    return;
  }
  emptyState.style.display = 'none';

  const favSet = new Set(userData.favorites || []);

  filtered.forEach((app, idx) => {
    const card = document.createElement('div');
    const isFav = favSet.has(app.id);
    card.className = `app-card ${isFav ? 'is-favorite' : ''} ${focusedIndex === idx ? 'keyboard-focused' : ''}`;
    card.dataset.id = app.id;
    card.dataset.index = idx;

    const shortCat = app.category.replace(/^\d+\.\s*/, '');
    const iconUrl = app.icon ? `${app.icon}?v=20261029_v7` : '/static/icons/default.png';

    let launchBadgeHtml = '';
    if (activeCategory === 'frequent') {
      const cnt = app._launches || (userData.launch_stats?.[app.id]?.count || 0);
      launchBadgeHtml = `<span class="launch-count-badge" title="Запущено ${cnt} раз">${ICONS.flame} ${cnt}</span>`;
    }

    let playtimeBadgeHtml = '';
    if (userData.settings?.enable_playtime_tracking !== false && playtimeStats?.apps_playtime?.[app.id]) {
      const pTotal = playtimeStats.apps_playtime[app.id].total || 0;
      if (pTotal >= 60) {
        playtimeBadgeHtml = `<span class="playtime-badge" title="Экранное время: ${formatPlaytime(pTotal)}">⏱️ ${formatPlaytime(pTotal)}</span>`;
      }
    }

    let liveDotHtml = '';
    if (userData.settings?.enable_live_status !== false && runningApps[app.id]) {
      const pidsCount = (runningApps[app.id] || []).length;
      liveDotHtml = `<span class="live-running-dot" title="Программа запущена в системе (${pidsCount} процессов)"></span>`;
    }

    const newBadgeHtml = isNewApp(app) ? `<span class="app-badge-new" title="Недавно добавлено в систему">Новое</span>` : '';

    card.innerHTML = `
      <div class="card-actions">
        <button class="card-action-btn fav-btn ${isFav ? 'active' : ''}" title="${isFav ? 'Удалить из избранного (F)' : 'В избранное (F)'}">
          ${isFav ? ICONS.starFilled : ICONS.starEmpty}
        </button>
        <button class="card-action-btn folder-btn" title="Открыть папку (Alt+Enter)">
          ${ICONS.folder}
        </button>
      </div>
      <div class="app-icon-wrap">
        <img class="app-icon" src="${iconUrl}" alt="${app.name}" loading="lazy" onerror="this.src='/static/icons/default.png'">
        ${liveDotHtml}
      </div>
      <div class="app-details">
        <div class="app-title-row">
          <span class="app-name" title="${app.name}">${app.name}</span>
          ${newBadgeHtml}
        </div>
        <div class="app-badges-row">
          ${launchBadgeHtml}
          ${playtimeBadgeHtml}
          <span class="app-category-badge">${shortCat}</span>
        </div>
        <div class="app-description" title="${app.description || ''}">
          ${app.description || 'Приложение Windows'}
        </div>
      </div>
      <div class="compact-launch-hint">
        <kbd>↵</kbd> <span>Открыть</span>
      </div>
    `;

    // Star Favorite Toggle
    const favBtn = card.querySelector('.fav-btn');
    favBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      await toggleFavorite(app);
    });

    // Folder Button
    const folderBtn = card.querySelector('.folder-btn');
    folderBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openAppFolder(app);
    });

    // Left Click Launch
    card.addEventListener('click', () => {
      setFocusedCard(idx);
      launchApp(app);
    });

    // Right Click Custom Context Menu
    card.addEventListener('contextmenu', (e) => {
      showContextMenu(e, app);
    });

    appsGrid.appendChild(card);
  });
}

function setFocusedCard(index) {
  const cards = appsGrid.querySelectorAll('.app-card');
  if (cards.length === 0) return;

  if (index < 0) index = 0;
  if (index >= cards.length) index = cards.length - 1;

  focusedIndex = index;
  cards.forEach((c, idx) => {
    if (idx === focusedIndex) {
      c.classList.add('keyboard-focused');
      c.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    } else {
      c.classList.remove('keyboard-focused');
    }
  });
}

// App Actions & Context Menu Handling
function showContextMenu(e, app) {
  e.preventDefault();
  e.stopPropagation();
  activeContextApp = app;

  const favSet = new Set(userData.favorites || []);
  const isFav = favSet.has(app.id);
  if (ctxFavText) {
    ctxFavText.textContent = isFav ? 'Удалить из избранного' : 'Добавить в избранное';
  }

  // Populate categories submenu
  if (ctxCategorySubmenu) {
    ctxCategorySubmenu.innerHTML = '';
    allCategories.forEach(cat => {
      const item = document.createElement('div');
      item.className = `submenu-item ${cat.name === app.category ? 'current' : ''}`;
      item.textContent = cat.name.replace(/^\d+\.\s*/, '');
      item.onclick = async (evt) => {
        evt.stopPropagation();
        hideContextMenu();
        await moveCategory(app, cat.name);
      };
      ctxCategorySubmenu.appendChild(item);
    });
  }

  // Populate workspaces submenu
  if (ctxWorkspaceSubmenu) {
    ctxWorkspaceSubmenu.innerHTML = '';
    workspacesList.forEach(ws => {
      const item = document.createElement('div');
      const inWs = (ws.apps || []).includes(app.id);
      item.className = `submenu-item ${inWs ? 'current' : ''}`;
      item.innerHTML = `<span style="display:inline-block; width: 14px; color:#3b82f6; font-weight:700;">${inWs ? '✓' : ''}</span> <span>${ws.icon || '🚀'} ${ws.name}</span>`;
      item.onclick = async (evt) => {
        evt.stopPropagation();
        hideContextMenu();
        if (inWs) {
          ws.apps = (ws.apps || []).filter(aid => aid !== app.id);
        } else {
          if (!ws.apps) ws.apps = [];
          ws.apps.push(app.id);
        }
        await fetch('/api/workspaces/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(ws)
        });
        showToast('Стек обновлен', inWs ? `«${app.name}» удалена из стека «${ws.name}»` : `«${app.name}» добавлена в стек «${ws.name}»`);
        renderWorkspacesList();
      };
      ctxWorkspaceSubmenu.appendChild(item);
    });

    const createItem = document.createElement('div');
    createItem.className = 'submenu-item';
    createItem.style.borderTop = '1px solid rgba(255,255,255,0.06)';
    createItem.innerHTML = `<span style="display:inline-block; width: 14px; color: var(--accent); font-weight: 700;">+</span> <span>Новый стек с этой программой</span>`;
    createItem.onclick = (evt) => {
      evt.stopPropagation();
      hideContextMenu();
      openWorkspacesModal();
      openWorkspaceEditor(null, [app.id]);
    };
    ctxWorkspaceSubmenu.appendChild(createItem);
  }

  // Kill Task visibility: only for currently running apps
  if (ctxKillTask) {
    const isRunning = runningApps[app.id] && runningApps[app.id].length > 0;
    ctxKillTask.style.display = isRunning ? 'flex' : 'none';
  }

  cardContextMenu.style.display = 'flex';

  // Position clamped within window bounds
  const menuW = 230;
  const menuH = 220;
  let x = e.clientX;
  let y = e.clientY;

  if (x + menuW > window.innerWidth - 12) x = window.innerWidth - menuW - 12;
  if (y + menuH > window.innerHeight - 12) y = window.innerHeight - menuH - 12;
  if (x < 12) x = 12;
  if (y < 12) y = 12;

  cardContextMenu.style.left = `${x}px`;
  cardContextMenu.style.top = `${y}px`;
}

function hideContextMenu() {
  if (cardContextMenu) cardContextMenu.style.display = 'none';
  activeContextApp = null;
}

window.addEventListener('click', (e) => {
  if (cardContextMenu && !cardContextMenu.contains(e.target)) {
    hideContextMenu();
  }
});

// Context Menu Action Listeners
if (ctxRunAdmin) {
  ctxRunAdmin.addEventListener('click', () => {
    if (activeContextApp) {
      launchAdmin(activeContextApp);
      hideContextMenu();
    }
  });
}

if (ctxOpenFolder) {
  ctxOpenFolder.addEventListener('click', () => {
    if (activeContextApp) {
      openTargetFolder(activeContextApp);
      hideContextMenu();
    }
  });
}

if (ctxToggleFavorite) {
  ctxToggleFavorite.addEventListener('click', () => {
    if (activeContextApp) {
      toggleFavorite(activeContextApp);
      hideContextMenu();
    }
  });
}

if (ctxHideApp) {
  ctxHideApp.addEventListener('click', () => {
    if (activeContextApp) {
      hideApp(activeContextApp);
      hideContextMenu();
    }
  });
}

if (ctxKillTask) {
  ctxKillTask.addEventListener('click', async () => {
    if (activeContextApp) {
      const app = activeContextApp;
      hideContextMenu();
      showToast('Завершение задачи...', `Останавливаем процессы ${app.name}`);
      try {
        const res = await fetch('/api/kill_app', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: app.id })
        });
        const d = await res.json();
        if (d.success) {
          showToast('Процесс завершен', `Программа «${app.name}» остановлена`);
          delete runningApps[app.id];
          renderApps();
        } else {
          showToast('Ошибка', d.message || 'Не удалось завершить процесс');
        }
      } catch (err) {
        showToast('Ошибка', err.message);
      }
    }
  });
}

async function launchAdmin(app) {
  showToast('Запуск от имени администратора', `Запрос прав для ${app.name}...`);
  try {
    const res = await fetch('/api/launch_admin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: app.id })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast('UAC отклонен', data.message || 'Запуск отменен пользователем');
    }
  } catch (e) {
    showToast('Ошибка запуска', e.message);
  }
}

async function openTargetFolder(app) {
  try {
    const res = await fetch('/api/open_target_folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: app.id })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('Проводник', `Папка открыта: ${app.name}`);
    } else {
      openAppFolder(app);
    }
  } catch (e) {
    openAppFolder(app);
  }
}

async function moveCategory(app, newCategory) {
  try {
    const res = await fetch('/api/move_category', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: app.id, category: newCategory })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('Категория изменена', `${app.name} перемещена в ${newCategory.replace(/^\d+\.\s*/, '')}`);
      await reloadCatalogData();
    } else {
      showToast('Ошибка перемещения', data.message || 'Не удалось переместить ярлык');
    }
  } catch (e) {
    showToast('Ошибка перемещения', e.message);
  }
}

async function hideApp(app) {
  try {
    const res = await fetch('/api/hide_app', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: app.id })
    });
    if (res.ok) {
      showToast('Программа скрыта', `${app.name} скрыта из каталога (можно вернуть в Настройках)`);
      await reloadCatalogData();
      renderHiddenApps();
    }
  } catch (e) {
    showToast('Ошибка', e.message);
  }
}

async function unhideApp(appId, appName) {
  try {
    const res = await fetch('/api/unhide_app', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: appId })
    });
    if (res.ok) {
      showToast('Программа восстановлена', `${appName} возвращена в каталог`);
      await reloadCatalogData();
      renderHiddenApps();
    }
  } catch (e) {
    showToast('Ошибка', e.message);
  }
}

async function toggleFavorite(app) {
  const favSet = new Set(userData.favorites || []);
  const willAdd = !favSet.has(app.id);

  if (willAdd) {
    favSet.add(app.id);
  } else {
    favSet.delete(app.id);
  }
  userData.favorites = Array.from(favSet);
  updateStats();
  renderApps();

  showToast(willAdd ? 'Добавлено в Избранное' : 'Удалено из Избранного', app.name);

  try {
    await fetch('/api/favorites/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: app.id })
    });
  } catch (e) {}
}

async function launchApp(app) {
  if (!userData.launch_stats) userData.launch_stats = {};
  if (!userData.launch_stats[app.id]) userData.launch_stats[app.id] = { count: 0, last_launched: 0 };
  userData.launch_stats[app.id].count = (userData.launch_stats[app.id].count || 0) + 1;
  userData.launch_stats[app.id].last_launched = Date.now() / 1000;
  updateStats();

  if (statusText) statusText.textContent = `Запуск ${app.name}...`;

  try {
    const res = await fetch('/api/launch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: app.id })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('Запуск программы', `Запуск ${app.name}...`);
      if (statusText) statusText.textContent = `Запущено: ${app.name}`;
    } else {
      showToast('Ошибка запуска', data.detail || data.message || 'Не удалось открыть приложение');
      if (statusText) statusText.textContent = `Ошибка: ${app.name}`;
    }
  } catch (err) {
    showToast('Ошибка запуска', err.message);
  } finally {
    setTimeout(() => {
      if (statusText) statusText.textContent = 'Каталог готов';
    }, 3000);
  }
}

async function openAppFolder(app) {
  try {
    await fetch('/api/open_folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: app.target || app.lnk_path })
    });
  } catch (e) {}
}

// Search Inputs
searchInput.addEventListener('input', (e) => {
  searchQuery = e.target.value;
  clearSearchBtn.style.display = searchQuery ? 'flex' : 'none';
  focusedIndex = -1;
  renderApps();
});

clearSearchBtn.addEventListener('click', () => {
  searchInput.value = '';
  searchQuery = '';
  clearSearchBtn.style.display = 'none';
  searchInput.focus();
  focusedIndex = -1;
  renderApps();
});

// Top bar buttons
openPlayniteBtn.addEventListener('click', async () => {
  try {
    const res = await fetch('/api/open_playnite', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('Playnite', 'Библиотека игр запущена');
    } else {
      showToast('Playnite не найден', 'Установите Playnite или проверьте путь');
    }
  } catch (e) {
    showToast('Ошибка', e.message);
  }
});

openFolderBtn.addEventListener('click', async () => {
  try {
    await fetch('/api/open_folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: activeCategory !== 'all' && activeCategory !== 'frequent' && activeCategory !== 'favorites' ? activeCategory : '' })
    });
  } catch (e) {}
});

rescanBtn.addEventListener('click', async () => {
  rescanBtn.style.transform = 'rotate(360deg)';
  try {
    showToast('Синхронизация...', 'Сканирование системы и проверка каталогов...');
    await fetch('/api/rescan', { method: 'POST' });
    await reloadCatalogData();
    showToast('Синхронизация завершена', `Проверена система и каталоги (всего программ: ${allApps.length})`);
  } catch (e) {
    showToast('Ошибка обновления', e.message);
  } finally {
    setTimeout(() => { rescanBtn.style.transform = ''; }, 450);
  }
});

// Toast Notifications
function showToast(title, msg) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <div class="toast-title">${title}</div>
    <div class="toast-msg">${msg}</div>
  `;
  toastHub.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    setTimeout(() => toast.remove(), 200);
  }, 2600);
}

// Settings Event Listeners
if (settingsBtn) {
  settingsBtn.addEventListener('click', openSettings);
}
if (closeSettingsBtn) {
  closeSettingsBtn.addEventListener('click', closeSettings);
}
if (saveSettingsBtn) {
  saveSettingsBtn.addEventListener('click', () => {
    closeSettings();
  });
}

if (startupTabSelect) {
  startupTabSelect.addEventListener('change', (e) => {
    const chosen = e.target.value;
    localStorage.setItem('smartcatalog_startup_tab', chosen);
    saveSetting('startup_tab', chosen);
    const selectedText = startupTabSelect.options[startupTabSelect.selectedIndex]?.textContent || chosen;
    showToast('Стартовая вкладка изменена', selectedText);
  });
}

if (viewModeSelect) {
  viewModeSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    setViewMode(val);
    saveSetting('view_mode', val);
    showToast('Режим лаунчера', val === 'compact' ? 'Компактный поиск (Raycast)' : 'Стандартный каталог (3 колонки)');
  });
}

if (themeSelect) {
  themeSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    applyTheme(val);
    saveSetting('theme', val);
    showToast('Тема оформления', themeSelect.options[themeSelect.selectedIndex]?.textContent || val);
  });
}

if (enableNewBadgeToggle) {
  enableNewBadgeToggle.addEventListener('change', (e) => {
    const checked = e.target.checked;
    if (badgePeriodGroup) {
      badgePeriodGroup.style.display = checked ? 'flex' : 'none';
    }
    saveSetting('enable_new_badge', checked);
    renderApps();
    showToast('Индикатор «Новое»', checked ? 'Включен' : 'Отключен');
  });
}

if (badgePeriodSelect) {
  badgePeriodSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    saveSetting('new_badge_period', val);
    renderApps();
    showToast('Период индикатора «Новое»', badgePeriodSelect.options[badgePeriodSelect.selectedIndex]?.textContent || val);
  });
}

if (hotkeySelect) {
  hotkeySelect.addEventListener('change', (e) => {
    const val = e.target.value;
    saveSetting('global_hotkey', val);
    showToast('Горячая клавиша', hotkeySelect.options[hotkeySelect.selectedIndex]?.textContent || val);
  });
}

if (enableTrayToggle) {
  enableTrayToggle.addEventListener('change', (e) => {
    const checked = e.target.checked;
    saveSetting('enable_tray', checked);
    showToast('Значок в трее', checked ? 'Включен' : 'Отключен');
  });
}

if (enablePlaytimeToggle) {
  enablePlaytimeToggle.addEventListener('change', (e) => {
    const checked = e.target.checked;
    saveSetting('enable_playtime_tracking', checked);
    renderApps();
    showToast('Учет экранного времени', checked ? 'Включен' : 'Отключен');
  });
}

if (enableLiveStatusToggle) {
  enableLiveStatusToggle.addEventListener('change', (e) => {
    const checked = e.target.checked;
    saveSetting('enable_live_status', checked);
    renderApps();
    showToast('Индикатор запущенных программ', checked ? 'Включен' : 'Отключен');
  });
}

if (enableClipboardToggle) {
  enableClipboardToggle.addEventListener('change', (e) => {
    const checked = e.target.checked;
    saveSetting('enable_clipboard_history', checked);
    showToast('История буфера обмена', checked ? 'Включена' : 'Отключена');
  });
}

if (settingsModal) {
  settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) closeSettings();
  });
}

// Classification Log Handlers
const openLogsFolderBtn = document.getElementById('openLogsFolderBtn');
if (openLogsFolderBtn) {
  openLogsFolderBtn.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/open_logs_folder', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast('Папка с логами', 'Папка открыта в Проводнике Windows');
      } else {
        showToast('Ошибка', data.error || 'Не удалось открыть папку');
      }
    } catch (e) {
      showToast('Ошибка', e.message);
    }
  });
}

const viewClassificationLogBtn = document.getElementById('viewClassificationLogBtn');
const logViewerModal = document.getElementById('logViewerModal');
const closeLogViewerBtn = document.getElementById('closeLogViewerBtn');
const closeLogViewerFooterBtn = document.getElementById('closeLogViewerFooterBtn');
const logViewerContent = document.getElementById('logViewerContent');
const copyLogBtn = document.getElementById('copyLogBtn');

if (viewClassificationLogBtn) {
  viewClassificationLogBtn.addEventListener('click', async () => {
    if (logViewerModal) logViewerModal.style.display = 'flex';
    if (logViewerContent) logViewerContent.value = 'Загрузка журнала классификации...';
    try {
      const res = await fetch('/api/classification_log');
      const data = await res.json();
      if (data.success && logViewerContent) {
        logViewerContent.value = data.log || '(Журнал пуст)';
        logViewerContent.scrollTop = logViewerContent.scrollHeight;
      }
    } catch (e) {
      if (logViewerContent) logViewerContent.value = 'Ошибка загрузки лога: ' + e.message;
    }
  });
}

function hideLogViewer() {
  if (logViewerModal) logViewerModal.style.display = 'none';
}
if (closeLogViewerBtn) closeLogViewerBtn.addEventListener('click', hideLogViewer);
if (closeLogViewerFooterBtn) closeLogViewerFooterBtn.addEventListener('click', hideLogViewer);
if (logViewerModal) {
  logViewerModal.addEventListener('click', (e) => {
    if (e.target === logViewerModal) hideLogViewer();
  });
}
if (copyLogBtn) {
  copyLogBtn.addEventListener('click', () => {
    if (logViewerContent && logViewerContent.value) {
      navigator.clipboard.writeText(logViewerContent.value);
      showToast('Лог скопирован', 'Содержимое лога классификации скопировано в буфер обмена');
    }
  });
}

function escapeHtml(str) {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Workspaces (Рабочие пространства и Стеки ПО)
function openWorkspacesModal() {
  if (!workspacesModal) return;
  closeWorkspaceEditor();
  renderWorkspacesList();
  workspacesModal.style.display = 'flex';
}

function closeWorkspacesModal() {
  if (!workspacesModal) return;
  workspacesModal.style.display = 'none';
  closeWorkspaceEditor();
}

function openWorkspaceEditor(ws = null, preselectedAppIds = []) {
  if (!workspaceEditorView || !workspacesListView) return;
  workspacesListView.style.display = 'none';
  workspaceEditorView.style.display = 'block';
  const wsModalFooter = document.getElementById('workspacesModalFooter');
  if (wsModalFooter) wsModalFooter.style.display = 'none';

  if (ws) {
    if (wsEditorHeading) wsEditorHeading.textContent = `Редактировать стек: ${ws.name}`;
    if (wsEditId) wsEditId.value = ws.id || '';
    if (wsEditName) wsEditName.value = ws.name || '';
    if (wsEditIcon) wsEditIcon.value = ws.icon || '🚀';
    if (wsEditDesc) wsEditDesc.value = ws.description || '';
    selectedWorkspaceAppIds = new Set(ws.apps || []);
  } else {
    if (wsEditorHeading) wsEditorHeading.textContent = 'Создать новый стек ПО';
    if (wsEditId) wsEditId.value = '';
    if (wsEditName) wsEditName.value = '';
    if (wsEditIcon) wsEditIcon.value = '🚀';
    if (wsEditDesc) wsEditDesc.value = '';
    selectedWorkspaceAppIds = new Set(preselectedAppIds || []);
  }

  if (wsAppSearchInput) wsAppSearchInput.value = '';
  renderWorkspaceSelectedChips();
  renderWorkspaceAppsPicker('');
}

function closeWorkspaceEditor() {
  if (!workspaceEditorView || !workspacesListView) return;
  workspaceEditorView.style.display = 'none';
  workspacesListView.style.display = 'block';
  const wsModalFooter = document.getElementById('workspacesModalFooter');
  if (wsModalFooter) wsModalFooter.style.display = 'flex';
}

function renderWorkspaceSelectedChips() {
  if (!wsSelectedChipsBar) return;
  wsSelectedChipsBar.innerHTML = '';
  if (wsSelectedCount) wsSelectedCount.textContent = selectedWorkspaceAppIds.size;

  if (selectedWorkspaceAppIds.size === 0) {
    wsSelectedChipsBar.innerHTML = '<span class="ws-empty-chips-text">Пока не выбрано ни одной программы</span>';
    return;
  }

  const appMap = {};
  allApps.forEach(a => { appMap[a.id] = a; });

  selectedWorkspaceAppIds.forEach(aid => {
    const app = appMap[aid];
    if (!app) return;
    const chip = document.createElement('span');
    chip.className = 'ws-selected-chip';
    const iconSrc = app.icon ? `${app.icon}?v=20261029_v7` : '/static/icons/default.png';
    chip.innerHTML = `
      <img class="ws-chip-icon" src="${iconSrc}" onerror="this.src='/static/icons/default.png'">
      <span>${escapeHtml(app.name)}</span>
      <span class="ws-chip-remove" title="Удалить из стека">✕</span>
    `;
    chip.querySelector('.ws-chip-remove').onclick = (e) => {
      e.stopPropagation();
      selectedWorkspaceAppIds.delete(aid);
      renderWorkspaceSelectedChips();
      updateWorkspacePickerChecks();
    };
    wsSelectedChipsBar.appendChild(chip);
  });
}

function updateWorkspacePickerChecks() {
  if (!wsAppsPickerList) return;
  wsAppsPickerList.querySelectorAll('.ws-app-pick-item').forEach(item => {
    const aid = item.dataset.id;
    item.classList.toggle('selected', selectedWorkspaceAppIds.has(aid));
  });
}

function renderWorkspaceAppsPicker(filterText = '') {
  if (!wsAppsPickerList) return;
  wsAppsPickerList.innerHTML = '';
  const q = (filterText || '').trim().toLowerCase();

  const matched = allApps.filter(a => {
    if (!q) return true;
    return a.name.toLowerCase().includes(q) || (a.description && a.description.toLowerCase().includes(q)) || a.category.toLowerCase().includes(q);
  });

  if (matched.length === 0) {
    wsAppsPickerList.innerHTML = '<div style="grid-column: 1/-1; padding: 12px; text-align: center; color: var(--text-tertiary); font-size: 12px;">Программы не найдены</div>';
    return;
  }

  matched.forEach(app => {
    const item = document.createElement('div');
    const isSel = selectedWorkspaceAppIds.has(app.id);
    item.className = `ws-app-pick-item ${isSel ? 'selected' : ''}`;
    item.dataset.id = app.id;
    const iconSrc = app.icon ? `${app.icon}?v=20261029_v7` : '/static/icons/default.png';
    item.innerHTML = `
      <img class="ws-app-pick-icon" src="${iconSrc}" onerror="this.src='/static/icons/default.png'">
      <span class="ws-app-pick-name" title="${app.name}">${escapeHtml(app.name)}</span>
      <span class="ws-app-pick-check">✓</span>
    `;
    item.onclick = () => {
      if (selectedWorkspaceAppIds.has(app.id)) {
        selectedWorkspaceAppIds.delete(app.id);
      } else {
        selectedWorkspaceAppIds.add(app.id);
      }
      item.classList.toggle('selected', selectedWorkspaceAppIds.has(app.id));
      renderWorkspaceSelectedChips();
    };
    wsAppsPickerList.appendChild(item);
  });
}

async function renderWorkspacesList() {
  try {
    const res = await fetch('/api/workspaces');
    workspacesList = await res.json();
    if (!workspacesListContainer) return;
    workspacesListContainer.innerHTML = '';

    const appMap = {};
    allApps.forEach(a => { appMap[a.id] = a; });

    if (!workspacesList || workspacesList.length === 0) {
      workspacesListContainer.innerHTML = `
        <div style="grid-column: 1/-1; padding: 32px 16px; text-align: center;">
          <div style="font-size: 28px; margin-bottom: 8px;">🚀</div>
          <div style="font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">Стеков пока нет</div>
          <div style="font-size: 12px; color: var(--text-tertiary); margin-bottom: 12px;">Создайте свой первый стек программ для быстрого запуска в 1 клик</div>
        </div>
      `;
      return;
    }

    workspacesList.forEach(ws => {
      const card = document.createElement('div');
      card.className = 'workspace-card';

      let iconsHtml = '';
      let tagsHtml = '';
      const appIds = ws.apps || [];
      appIds.forEach(aid => {
        const a = appMap[aid];
        if (a) {
          const iconSrc = a.icon ? `${a.icon}?v=20261029_v7` : '/static/icons/default.png';
          iconsHtml += `<img src="${iconSrc}" title="${a.name}" onerror="this.src='/static/icons/default.png'">`;
          tagsHtml += `<span class="ws-app-tag" title="${a.name}">${escapeHtml(a.name)}</span>`;
        }
      });

      card.innerHTML = `
        <div class="ws-header">
          <span class="ws-icon">${ws.icon || '🚀'}</span>
          <div class="ws-title-wrap">
            <div class="ws-name">${escapeHtml(ws.name)}</div>
            <div class="ws-desc">${escapeHtml(ws.description || `${appIds.length} программ в стеке`)}</div>
          </div>
          <div class="ws-card-actions">
            <button class="ws-icon-btn edit-ws-btn" title="Редактировать стек">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            </button>
            <button class="ws-icon-btn del-ws-btn danger" title="Удалить стек">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </div>
        </div>
        <div class="ws-apps-preview">
          <div class="ws-icons-row">${iconsHtml || '<span style="font-size:11px;color:var(--text-tertiary);">Нет программ</span>'}</div>
          <div class="ws-apps-names-tags">${tagsHtml}</div>
        </div>
        <div class="ws-footer-row">
          <button class="ws-launch-btn" data-id="${ws.id}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            <span>Запустить всё (${appIds.length})</span>
          </button>
        </div>
      `;

      // Launch
      card.querySelector('.ws-launch-btn').onclick = async () => {
        showToast('Запуск пространства...', `Запускаем набор «${ws.name}» (${appIds.length} программ)`);
        try {
          const lres = await fetch('/api/workspaces/launch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: ws.id })
          });
          const ld = await lres.json();
          if (ld.success) {
            showToast('Стек запущен', ld.message);
            closeWorkspacesModal();
          }
        } catch (e) {
          showToast('Ошибка запуска', e.message);
        }
      };

      // Edit
      card.querySelector('.edit-ws-btn').onclick = (e) => {
        e.stopPropagation();
        openWorkspaceEditor(ws);
      };

      // Delete
      card.querySelector('.del-ws-btn').onclick = async (e) => {
        e.stopPropagation();
        if (!confirm(`Удалить стек «${ws.name}»?`)) return;
        try {
          const dres = await fetch('/api/workspaces/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: ws.id })
          });
          const dd = await dres.json();
          if (dd.success) {
            showToast('Стек удалён', `Стек «${ws.name}» удалён`);
            await renderWorkspacesList();
          }
        } catch (err) {
          showToast('Ошибка удаления', err.message);
        }
      };

      workspacesListContainer.appendChild(card);
    });
  } catch (e) {}
}

// Workspaces Event Listeners
if (openWorkspacesBtn) openWorkspacesBtn.addEventListener('click', openWorkspacesModal);
if (closeWorkspacesBtn) closeWorkspacesBtn.addEventListener('click', closeWorkspacesModal);
if (closeWorkspacesBottomBtn) closeWorkspacesBottomBtn.addEventListener('click', closeWorkspacesModal);
if (createNewWorkspaceBtn) createNewWorkspaceBtn.addEventListener('click', () => openWorkspaceEditor(null));
if (cancelWsEditorTopBtn) cancelWsEditorTopBtn.addEventListener('click', closeWorkspaceEditor);
if (cancelWorkspaceEditBtn) cancelWorkspaceEditBtn.addEventListener('click', closeWorkspaceEditor);

if (wsAppSearchInput) {
  wsAppSearchInput.addEventListener('input', (e) => {
    renderWorkspaceAppsPicker(e.target.value);
  });
}

document.querySelectorAll('.emoji-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    if (wsEditIcon) wsEditIcon.value = chip.dataset.emoji || chip.textContent;
  });
});

if (saveWorkspaceSubmitBtn) {
  saveWorkspaceSubmitBtn.addEventListener('click', async () => {
    const name = wsEditName ? wsEditName.value.trim() : '';
    if (!name) {
      showToast('Ошибка', 'Введите название для стека ПО');
      if (wsEditName) wsEditName.focus();
      return;
    }
    const icon = wsEditIcon ? wsEditIcon.value.trim() || '🚀' : '🚀';
    const desc = wsEditDesc ? wsEditDesc.value.trim() : '';
    const id = wsEditId ? wsEditId.value || undefined : undefined;
    const apps = Array.from(selectedWorkspaceAppIds);

    try {
      const sres = await fetch('/api/workspaces/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, name, icon, description: desc, apps })
      });
      const sd = await sres.json();
      if (sd.success) {
        showToast('Стек сохранён', `Стек «${name}» успешно сохранён (${apps.length} программ)`);
        closeWorkspaceEditor();
        await renderWorkspacesList();
      } else {
        showToast('Ошибка сохранения', sd.message || 'Не удалось сохранить стек');
      }
    } catch (e) {
      showToast('Ошибка сохранения', e.message);
    }
  });
}

if (workspacesModal) {
  workspacesModal.addEventListener('click', (e) => {
    if (e.target === workspacesModal) closeWorkspacesModal();
  });
}

if (filterRunningBtn) {
  filterRunningBtn.addEventListener('click', () => {
    isFilterRunningActive = !isFilterRunningActive;
    filterRunningBtn.classList.toggle('active', isFilterRunningActive);
    renderApps();
  });
}

// Insights Dashboard (Аналитика и экранное время)
async function openInsightsModal() {
  if (!insightsModal) return;
  await populateInsightsData();
  insightsModal.style.display = 'flex';
}

function closeInsightsModal() {
  if (!insightsModal) return;
  insightsModal.style.display = 'none';
}

async function populateInsightsData() {
  try {
    const res = await fetch('/api/playtime');
    playtimeStats = await res.json();
    if (!playtimeStats) return;

    if (insightTotalTime) {
      insightTotalTime.textContent = formatPlaytime(playtimeStats.total_screen_time);
    }
    if (insightTodayTime) {
      insightTodayTime.textContent = formatPlaytime(playtimeStats.today_screen_time);
    }
    if (insightTotalLaunches) {
      let sumLaunches = 0;
      Object.values(userData.launch_stats || {}).forEach(s => { sumLaunches += (s.count || 0); });
      insightTotalLaunches.textContent = sumLaunches || '120+';
    }
    if (insightTopApp && playtimeStats.top_apps?.[0]) {
      const top = playtimeStats.top_apps[0];
      insightTopApp.textContent = top.name;
      if (insightTopAppTime) insightTopAppTime.textContent = `${formatPlaytime(top.total)} всего`;
    }

    // Category percentage bars
    if (insightCategoryBars) {
      insightCategoryBars.innerHTML = '';
      const totalTime = Math.max(1, playtimeStats.total_screen_time);
      const sortedCats = Object.entries(playtimeStats.categories || {}).sort((a, b) => b[1] - a[1]);
      sortedCats.forEach(([catName, catSecs]) => {
        const pct = Math.round((catSecs / totalTime) * 100);
        const cleanName = catName.replace(/^\d+\.\s*/, '');
        const item = document.createElement('div');
        item.className = 'cat-bar-item';
        item.innerHTML = `
          <div class="cat-bar-header">
            <span class="cat-bar-name">${cleanName}</span>
            <span>${pct}% • ${formatPlaytime(catSecs)}</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${pct}%;"></div>
          </div>
        `;
        insightCategoryBars.appendChild(item);
      });
    }

    // Top 5 apps
    if (insightTopAppsList) {
      insightTopAppsList.innerHTML = '';
      (playtimeStats.top_apps || []).slice(0, 5).forEach(top => {
        const row = document.createElement('div');
        row.className = 'top-app-row';
        const iconSrc = top.icon ? `${top.icon}?v=20261029_v7` : '/static/icons/default.png';
        row.innerHTML = `
          <div class="app-meta">
            <img src="${iconSrc}" alt="" onerror="this.src='/static/icons/default.png'">
            <span class="top-app-name" title="${top.name}">${top.name}</span>
          </div>
          <span class="top-app-time">${formatPlaytime(top.total)}</span>
        `;
        insightTopAppsList.appendChild(row);
      });
    }
  } catch (e) {}
}

if (openInsightsBtn) openInsightsBtn.addEventListener('click', openInsightsModal);
if (closeInsightsBtn) closeInsightsBtn.addEventListener('click', closeInsightsModal);
if (closeInsightsBottomBtn) closeInsightsBottomBtn.addEventListener('click', closeInsightsModal);
if (insightsModal) {
  insightsModal.addEventListener('click', (e) => {
    if (e.target === insightsModal) closeInsightsModal();
  });
}

// System Resource Monitor & Process Manager
let sysStatsPollTimer = null;

async function updateHeaderSystemStats() {
  if (!sysHeaderCpu || !sysHeaderRam) return;
  try {
    const res = await fetch('/api/system_stats');
    const d = await res.json();
    if (d && d.cpu_percent !== undefined) {
      sysHeaderCpu.textContent = `CPU ${Math.round(d.cpu_percent)}%`;
      sysHeaderRam.textContent = `RAM ${Math.round(d.ram_percent)}%`;
    }
  } catch (e) {}
}

async function renderSystemMonitorModal() {
  if (!systemMonitorModal || systemMonitorModal.style.display === 'none') return;
  try {
    const res = await fetch('/api/system_stats');
    const d = await res.json();
    if (!d || d.cpu_percent === undefined) return;

    // CPU
    if (sysGaugeCpuVal) sysGaugeCpuVal.textContent = `${Math.round(d.cpu_percent)}%`;
    if (sysGaugeCpuBar) sysGaugeCpuBar.style.width = `${Math.min(100, Math.max(0, d.cpu_percent))}%`;
    if (sysGaugeCpuSub) sysGaugeCpuSub.textContent = `${d.cpu_count || 16} ядер (потоков)`;

    // RAM
    if (sysGaugeRamVal) sysGaugeRamVal.textContent = `${Math.round(d.ram_percent)}%`;
    if (sysGaugeRamBar) sysGaugeRamBar.style.width = `${Math.min(100, Math.max(0, d.ram_percent))}%`;
    if (sysGaugeRamSub) sysGaugeRamSub.textContent = `${d.ram_used_gb} / ${d.ram_total_gb} ГБ`;

    // Disk C:
    if (sysGaugeDiskVal) sysGaugeDiskVal.textContent = `${Math.round(d.disk_percent)}%`;
    if (sysGaugeDiskBar) sysGaugeDiskBar.style.width = `${Math.min(100, Math.max(0, d.disk_percent))}%`;
    const freeGb = Math.max(0, Math.round(d.disk_total_gb - d.disk_used_gb));
    if (sysGaugeDiskSub) sysGaugeDiskSub.textContent = `${freeGb} ГБ свободно из ${d.disk_total_gb} ГБ`;

    // Top RAM Processes
    if (sysTopRamList) {
      sysTopRamList.innerHTML = '';
      if (!d.top_ram || d.top_ram.length === 0) {
        sysTopRamList.innerHTML = '<div class="hidden-empty-text">Нет данных о процессах</div>';
      } else {
        d.top_ram.forEach(p => {
          const row = document.createElement('div');
          row.className = 'sys-proc-row';
          row.innerHTML = `
            <div class="sys-proc-info">
              <div class="sys-proc-name" title="${escapeHtml(p.name)}">${escapeHtml(p.name)}</div>
              <div class="sys-proc-meta">PID: ${p.pid}</div>
            </div>
            <div class="sys-proc-actions">
              <span class="sys-proc-metric-val">${p.mem_mb} МБ</span>
              <button class="sys-kill-btn" data-pid="${p.pid}" data-name="${escapeHtml(p.name)}">Снять задачу</button>
            </div>
          `;
          row.querySelector('.sys-kill-btn').onclick = () => killProcessAction(p.pid, p.name);
          sysTopRamList.appendChild(row);
        });
      }
    }

    // Top CPU Processes
    if (sysTopCpuList) {
      sysTopCpuList.innerHTML = '';
      if (!d.top_cpu || d.top_cpu.length === 0) {
        sysTopCpuList.innerHTML = '<div class="hidden-empty-text">Нет данных о процессах</div>';
      } else {
        d.top_cpu.forEach(p => {
          const row = document.createElement('div');
          row.className = 'sys-proc-row';
          row.innerHTML = `
            <div class="sys-proc-info">
              <div class="sys-proc-name" title="${escapeHtml(p.name)}">${escapeHtml(p.name)}</div>
              <div class="sys-proc-meta">PID: ${p.pid}</div>
            </div>
            <div class="sys-proc-actions">
              <span class="sys-proc-metric-val">${p.cpu_percent.toFixed(1)}%</span>
              <button class="sys-kill-btn" data-pid="${p.pid}" data-name="${escapeHtml(p.name)}">Снять задачу</button>
            </div>
          `;
          row.querySelector('.sys-kill-btn').onclick = () => killProcessAction(p.pid, p.name);
          sysTopCpuList.appendChild(row);
        });
      }
    }
  } catch (e) {}
}

async function killProcessAction(pid, name) {
  try {
    const res = await fetch('/api/kill_process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pid })
    });
    const d = await res.json();
    if (d.success) {
      showToast('Задача снята', `Процесс ${name} (PID: ${pid}) успешно завершен`);
      renderSystemMonitorModal();
      updateRunningApps();
    } else {
      showToast('Ошибка', d.error || 'Не удалось завершить процесс');
    }
  } catch (err) {
    showToast('Ошибка', err.message);
  }
}

function openSystemMonitorModal() {
  if (!systemMonitorModal) return;
  systemMonitorModal.style.display = 'flex';
  renderSystemMonitorModal();
  if (sysStatsPollTimer) clearInterval(sysStatsPollTimer);
  sysStatsPollTimer = setInterval(renderSystemMonitorModal, 1500);
}

function closeSystemMonitorModal() {
  if (!systemMonitorModal) return;
  systemMonitorModal.style.display = 'none';
  if (sysStatsPollTimer) {
    clearInterval(sysStatsPollTimer);
    sysStatsPollTimer = null;
  }
}

if (sysMonitorPill) sysMonitorPill.addEventListener('click', openSystemMonitorModal);
if (closeSysMonitorBtn) closeSysMonitorBtn.addEventListener('click', closeSystemMonitorModal);
if (closeSysMonitorBottomBtn) closeSysMonitorBottomBtn.addEventListener('click', closeSystemMonitorModal);
if (refreshSysStatsBtn) refreshSysStatsBtn.addEventListener('click', renderSystemMonitorModal);
if (systemMonitorModal) {
  systemMonitorModal.addEventListener('click', (e) => {
    if (e.target === systemMonitorModal) closeSystemMonitorModal();
  });
}

// Clipboard & Pinned Snippets Manager
function openClipboardModal() {
  if (!clipboardModal) return;
  switchClipboardTab('history');
  clipboardModal.style.display = 'flex';
  if (clipboardSearchInput) {
    clipboardSearchInput.value = '';
    clipboardSearchInput.focus();
  }
}

function closeClipboardModal() {
  if (!clipboardModal) return;
  clipboardModal.style.display = 'none';
}

function switchClipboardTab(tab) {
  if (tab === 'history') {
    tabClipHistoryBtn?.classList.add('active');
    tabClipSnippetsBtn?.classList.remove('active');
    if (clipHistoryView) clipHistoryView.style.display = 'block';
    if (clipSnippetsView) clipSnippetsView.style.display = 'none';
    if (snippetEditorView) snippetEditorView.style.display = 'none';
    renderClipboardHistory();
  } else {
    tabClipSnippetsBtn?.classList.add('active');
    tabClipHistoryBtn?.classList.remove('active');
    if (clipHistoryView) clipHistoryView.style.display = 'none';
    if (clipSnippetsView) clipSnippetsView.style.display = 'block';
    if (snippetEditorView) snippetEditorView.style.display = 'none';
    loadAndRenderSnippets();
  }
}

if (tabClipHistoryBtn) tabClipHistoryBtn.addEventListener('click', () => switchClipboardTab('history'));
if (tabClipSnippetsBtn) tabClipSnippetsBtn.addEventListener('click', () => switchClipboardTab('snippets'));

async function renderClipboardHistory() {
  try {
    const res = await fetch('/api/clipboard');
    clipboardHistory = await res.json();
    if (clipHistoryCount) clipHistoryCount.textContent = clipboardHistory.length;
    populateClipboardItems(clipboardHistory);
  } catch (e) {}
}

function populateClipboardItems(items) {
  if (!clipboardItemsContainer) return;
  clipboardItemsContainer.innerHTML = '';

  if (!items || items.length === 0) {
    clipboardItemsContainer.innerHTML = '<div class="hidden-empty-text">История буфера обмена пуста</div>';
    return;
  }

  items.forEach(item => {
    const el = document.createElement('div');
    el.className = 'clipboard-item';
    const dateStr = item.time ? new Date(item.time * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
    el.innerHTML = `
      <div class="clip-content">
        <div class="clip-text">${escapeHtml(item.text)}</div>
        <div class="clip-meta">${item.length} символов • ${dateStr}</div>
      </div>
      <div class="clip-actions">
        <button class="clip-pin-btn" title="Сохранить как постоянный сниппет">📌 В сниппеты</button>
        <button class="clip-copy-btn">Копировать</button>
      </div>
    `;

    const copyAction = async (evt) => {
      evt.stopPropagation();
      try {
        const cres = await fetch('/api/clipboard/copy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: item.text })
        });
        const cd = await cres.json();
        if (cd.success) {
          showToast('Скопировано!', `Фрагмент помещен в буфер обмена`);
          closeClipboardModal();
        }
      } catch (err) {
        showToast('Ошибка', err.message);
      }
    };

    el.onclick = copyAction;
    el.querySelector('.clip-copy-btn').onclick = copyAction;
    el.querySelector('.clip-pin-btn').onclick = (evt) => {
      evt.stopPropagation();
      pinClipboardItemToSnippet(item.text);
    };
    clipboardItemsContainer.appendChild(el);
  });
}

function pinClipboardItemToSnippet(text) {
  switchClipboardTab('snippets');
  openSnippetEditor({
    id: '',
    title: text.length > 28 ? text.slice(0, 28).trim() + '...' : text.trim(),
    category: 'Заметки',
    content: text
  });
}

async function loadAndRenderSnippets() {
  try {
    const res = await fetch('/api/snippets');
    allSnippets = await res.json();
    if (clipSnippetsCount) clipSnippetsCount.textContent = allSnippets.length;
    renderSnippetsList();
  } catch (e) {}
}

function renderSnippetsList() {
  if (!snippetsListContainer) return;
  snippetsListContainer.innerHTML = '';

  const q = (snippetsSearchInput?.value || '').toLowerCase().trim();
  const filtered = allSnippets.filter(s => {
    if (activeSnippetCategory !== 'all' && s.category !== activeSnippetCategory) return false;
    const sText = s.content || s.text || '';
    if (q) {
      return (s.title || '').toLowerCase().includes(q) || 
             sText.toLowerCase().includes(q) || 
             (s.category || '').toLowerCase().includes(q);
    }
    return true;
  });

  if (filtered.length === 0) {
    snippetsListContainer.innerHTML = '<div class="hidden-empty-text" style="grid-column: 1 / -1;">Нет подходящих сниппетов</div>';
    return;
  }

  filtered.forEach(snip => {
    const snipContent = snip.content || snip.text || '';
    const card = document.createElement('div');
    card.className = 'snippet-card';
    card.innerHTML = `
      <div class="snippet-header">
        <span class="snippet-title" title="${escapeHtml(snip.title)}">${escapeHtml(snip.title)}</span>
        <span class="snippet-cat-badge">${escapeHtml(snip.category || 'Заметки')}</span>
      </div>
      <div class="snippet-content-preview" title="Кликните для быстрого копирования">${escapeHtml(snipContent)}</div>
      <div class="snippet-footer">
        <span class="snippet-meta-info">${snipContent.length} симв.</span>
        <div class="snippet-btn-group">
          <button class="snippet-action-btn copy-btn" title="Скопировать в буфер">Копировать</button>
          <button class="snippet-action-btn edit-btn" title="Редактировать">✏️</button>
          <button class="snippet-action-btn danger-btn delete-btn" title="Удалить">🗑️</button>
        </div>
      </div>
    `;

    const copyFn = async (e) => {
      e.stopPropagation();
      try {
        await fetch('/api/clipboard/copy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: snipContent })
        });
        showToast('Скопировано!', `Сниппет «${snip.title}» в буфере обмена`);
      } catch (err) {
        showToast('Ошибка копирования', err.message);
      }
    };

    card.querySelector('.snippet-content-preview').onclick = copyFn;
    card.querySelector('.copy-btn').onclick = copyFn;

    card.querySelector('.edit-btn').onclick = (e) => {
      e.stopPropagation();
      openSnippetEditor(snip);
    };

    card.querySelector('.delete-btn').onclick = async (e) => {
      e.stopPropagation();
      try {
        const dres = await fetch('/api/snippets/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: snip.id })
        });
        const dd = await dres.json();
        if (dd.success) {
          showToast('Сниппет удален', snip.title);
          loadAndRenderSnippets();
        }
      } catch (err) {}
    };

    snippetsListContainer.appendChild(card);
  });
}

function openSnippetEditor(snip = null) {
  if (!snippetEditorView || !clipSnippetsView) return;
  clipSnippetsView.style.display = 'none';
  snippetEditorView.style.display = 'block';

  if (snip) {
    if (snippetEditorHeading) snippetEditorHeading.textContent = 'Редактировать сниппет';
    if (snipEditId) snipEditId.value = snip.id || '';
    if (snipEditTitle) snipEditTitle.value = snip.title || '';
    if (snipEditCategory) snipEditCategory.value = snip.category || 'Заметки';
    if (snipEditContent) snipEditContent.value = snip.content || snip.text || '';
  } else {
    if (snippetEditorHeading) snippetEditorHeading.textContent = 'Новый сниппет';
    if (snipEditId) snipEditId.value = '';
    if (snipEditTitle) snipEditTitle.value = '';
    if (snipEditCategory) snipEditCategory.value = 'Команды';
    if (snipEditContent) snipEditContent.value = '';
  }
  if (snipEditTitle) snipEditTitle.focus();
}

function closeSnippetEditor() {
  if (!snippetEditorView || !clipSnippetsView) return;
  snippetEditorView.style.display = 'none';
  clipSnippetsView.style.display = 'block';
  renderSnippetsList();
}

if (newSnippetBtn) newSnippetBtn.addEventListener('click', () => openSnippetEditor(null));
if (cancelSnippetTopBtn) cancelSnippetTopBtn.addEventListener('click', closeSnippetEditor);
if (cancelSnippetBtn) cancelSnippetBtn.addEventListener('click', closeSnippetEditor);

if (saveSnippetSubmitBtn) {
  saveSnippetSubmitBtn.addEventListener('click', async () => {
    const title = (snipEditTitle?.value || '').trim();
    const category = (snipEditCategory?.value || '').trim() || 'Заметки';
    const content = (snipEditContent?.value || '').trim();
    const id = (snipEditId?.value || '').trim();

    if (!title) {
      showToast('Ошибка', 'Введите название сниппета');
      snipEditTitle?.focus();
      return;
    }
    if (!content) {
      showToast('Ошибка', 'Введите содержимое сниппета');
      snipEditContent?.focus();
      return;
    }

    try {
      const res = await fetch('/api/snippets/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, title, category, content })
      });
      const d = await res.json();
      if (d.success) {
        showToast('Сниппет сохранен', title);
        closeSnippetEditor();
        loadAndRenderSnippets();
      } else {
        showToast('Ошибка', d.error || 'Не удалось сохранить');
      }
    } catch (err) {
      showToast('Ошибка', err.message);
    }
  });
}

// Snippet category chips filtering
if (snippetChipsBar) {
  snippetChipsBar.addEventListener('click', (e) => {
    const chip = e.target.closest('.snip-chip');
    if (!chip) return;
    snippetChipsBar.querySelectorAll('.snip-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeSnippetCategory = chip.dataset.snipCat || 'all';
    renderSnippetsList();
  });
}

if (snippetsSearchInput) {
  snippetsSearchInput.addEventListener('input', () => {
    renderSnippetsList();
  });
}

if (openClipboardBtn) openClipboardBtn.addEventListener('click', openClipboardModal);
if (closeClipboardBtn) closeClipboardBtn.addEventListener('click', closeClipboardModal);
if (closeClipboardBottomBtn) closeClipboardBottomBtn.addEventListener('click', closeClipboardModal);
if (clipboardModal) {
  clipboardModal.addEventListener('click', (e) => {
    if (e.target === clipboardModal) closeClipboardModal();
  });
}

if (clipboardSearchInput) {
  clipboardSearchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      populateClipboardItems(clipboardHistory);
    } else {
      const filtered = clipboardHistory.filter(item => (item.text || '').toLowerCase().includes(q));
      populateClipboardItems(filtered);
    }
  });
}

if (clearClipboardBtn) {
  clearClipboardBtn.addEventListener('click', async () => {
    try {
      await fetch('/api/clipboard/clear', { method: 'POST' });
      clipboardHistory = [];
      populateClipboardItems([]);
      if (clipHistoryCount) clipHistoryCount.textContent = '0';
      showToast('Буфер очищен', 'История буфера обмена успешно удалена');
    } catch (e) {}
  });
}

// Compact mode button listener
if (toggleViewModeBtn) {
  toggleViewModeBtn.addEventListener('click', toggleViewMode);
}

// Periodic lightweight live running process polling
async function updateRunningApps() {
  try {
    const res = await fetch('/api/running_apps');
    const d = await res.json();
    runningApps = d.running || {};
    
    if (runningFilterBadge) {
      const runCount = allApps.filter(a => !!runningApps[a.id] && runningApps[a.id].length > 0).length;
      runningFilterBadge.textContent = runCount;
    }

    if (isFilterRunningActive && activeCategory === 'all') {
      renderApps();
      return;
    }

    document.querySelectorAll('.app-card').forEach(card => {
      const aid = card.dataset.id;
      const iconWrap = card.querySelector('.app-icon-wrap');
      const existingDot = iconWrap?.querySelector('.live-running-dot');
      if (runningApps[aid] && userData.settings?.enable_live_status !== false) {
        if (!existingDot && iconWrap) {
          const dot = document.createElement('span');
          dot.className = 'live-running-dot';
          dot.title = `Программа запущена в системе (${runningApps[aid].length} процессов)`;
          iconWrap.appendChild(dot);
        }
      } else {
        if (existingDot) existingDot.remove();
      }
    });
  } catch (e) {}
}

setInterval(updateRunningApps, 3500);

// Power User Grid Keyboard Navigation (Arrow Keys, Enter, F, Alt+Enter, Ctrl+K)
window.addEventListener('keydown', (e) => {
  const filtered = getFilteredApps();
  const isInputFocused = document.activeElement === searchInput;

  // Settings shortcut: ,
  if (!isInputFocused && (e.key === ',' || e.key === '<' || e.key === 'б' || e.key === 'Б')) {
    e.preventDefault();
    openSettings();
    return;
  }

  // Command palette focus: Ctrl+K or /
  if (((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) || (!isInputFocused && e.key === '/')) {
    e.preventDefault();
    searchInput.focus();
    searchInput.select();
    return;
  }

  // Toggle View Mode shortcut: Ctrl+M or Alt+M
  if ((e.ctrlKey || e.altKey) && (e.key === 'm' || e.key === 'M' || e.key === 'ь' || e.key === 'Ь')) {
    e.preventDefault();
    toggleViewMode();
    return;
  }

  // Escape handling
  if (e.key === 'Escape') {
    hideContextMenu();
    if (systemMonitorModal && systemMonitorModal.style.display !== 'none') {
      closeSystemMonitorModal();
      return;
    }
    if (settingsModal && settingsModal.style.display !== 'none') {
      closeSettings();
      return;
    }
    if (workspacesModal && workspacesModal.style.display !== 'none') {
      closeWorkspacesModal();
      return;
    }
    if (insightsModal && insightsModal.style.display !== 'none') {
      closeInsightsModal();
      return;
    }
    if (clipboardModal && clipboardModal.style.display !== 'none') {
      closeClipboardModal();
      return;
    }
    if (isInputFocused) {
      if (searchInput.value) {
        searchInput.value = '';
        searchQuery = '';
        clearSearchBtn.style.display = 'none';
        renderApps();
      } else {
        searchInput.blur();
      }
    } else if (focusedIndex !== -1) {
      focusedIndex = -1;
      appsGrid.querySelectorAll('.app-card').forEach(c => c.classList.remove('keyboard-focused'));
    }
    return;
  }

  // When search input is focused and user presses Enter
  if (isInputFocused && e.key === 'Enter') {
    const web = getWebSearchFallback(searchQuery);
    if (web && (filtered.length === 0 || focusedIndex === -1)) {
      fetch('/api/open_url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: web.url })
      });
      searchInput.blur();
      return;
    }
    if (filtered.length > 0) {
      const targetApp = (focusedIndex >= 0 && focusedIndex < filtered.length) ? filtered[focusedIndex] : filtered[0];
      launchApp(targetApp);
      searchInput.blur();
    }
    return;
  }

  // Arrow Navigation (when in search input, ArrowDown enters the grid)
  if (isInputFocused && e.key === 'ArrowDown') {
    e.preventDefault();
    searchInput.blur();
    setFocusedCard(0);
    return;
  }

  // Grid keys when search input is not active
  if (!isInputFocused && filtered.length > 0) {
    const cards = appsGrid.querySelectorAll('.app-card');
    let cols = 1;
    if (cards.length > 1) {
      const top0 = cards[0].offsetTop;
      for (let i = 1; i < cards.length; i++) {
        if (cards[i].offsetTop === top0) cols++;
        else break;
      }
    }

    if (e.key === 'ArrowRight') {
      e.preventDefault();
      setFocusedCard(focusedIndex + 1);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setFocusedCard(focusedIndex - 1);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setFocusedCard(focusedIndex === -1 ? 0 : focusedIndex + cols);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (focusedIndex - cols < 0) {
        searchInput.focus();
        searchInput.select();
      } else {
        setFocusedCard(focusedIndex - cols);
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (focusedIndex >= 0 && focusedIndex < filtered.length) {
        const app = filtered[focusedIndex];
        if (e.altKey) {
          openAppFolder(app);
        } else {
          launchApp(app);
        }
      }
    } else if (e.key === 'f' || e.key === 'F') {
      if (focusedIndex >= 0 && focusedIndex < filtered.length) {
        e.preventDefault();
        toggleFavorite(filtered[focusedIndex]);
      }
    }
  }
});

// Start client
initCatalog();
