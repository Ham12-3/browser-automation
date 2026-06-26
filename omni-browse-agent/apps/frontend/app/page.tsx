"use client";

import {
  Bot,
  CheckCircle2,
  Download,
  Eye,
  FileJson,
  Globe2,
  Play,
  RefreshCw,
  Shield,
  Square,
  Terminal,
  Wifi
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { BrowserInfo, api } from "../lib/api";

type Task = {
  id: number;
  title: string;
  user_prompt: string;
  status: string;
};

type ResultItem = {
  title?: string;
  url?: string;
  rank?: number;
  score?: string | null;
  comments?: string | null;
};

type ResultRow = {
  id: number;
  data: ResultItem[];
  created_at: string;
};

type LogEntry = {
  id: number;
  level: string;
  message: string;
  created_at: string;
};

type Screenshot = {
  id: number;
  file_path: string;
  url?: string | null;
  created_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_OMNI_API_BASE ?? "http://127.0.0.1:8765";
const DEMO_PROMPT = "Use my currently open browser to go to Hacker News and extract the top 10 story titles and links.";

export default function Dashboard() {
  const [browsers, setBrowsers] = useState<BrowserInfo[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [prompt, setPrompt] = useState(DEMO_PROMPT);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [results, setResults] = useState<ResultRow[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const latestData = results[0]?.data ?? [];
  const latestScreenshot = screenshots.at(-1) ?? null;
  const cdpBrowser = browsers.find((browser) => browser.cdp_available);
  const selectedStatus = selectedTask?.status ?? "idle";

  const loadTaskDetails = useCallback(async (taskId: number) => {
    const [taskData, resultData, logData, screenshotData] = await Promise.all([
      api<Task>(`/tasks/${taskId}`),
      api<ResultRow[]>(`/tasks/${taskId}/results`),
      api<LogEntry[]>(`/tasks/${taskId}/logs`),
      api<Screenshot[]>(`/tasks/${taskId}/screenshots`)
    ]);
    setSelectedTask(taskData);
    setResults(resultData);
    setLogs(logData);
    setScreenshots(screenshotData);
    return taskData;
  }, []);

  const refresh = useCallback(async () => {
    setIsRefreshing(true);
    setError(null);
    try {
      const [browserData, taskData] = await Promise.all([
        api<BrowserInfo[]>("/system/browsers"),
        api<Task[]>("/tasks")
      ]);
      setBrowsers(browserData);
      setTasks(taskData);
      const selectedId = selectedTask?.id ?? taskData[0]?.id;
      if (selectedId) {
        await loadTaskDetails(selectedId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setIsRefreshing(false);
    }
  }, [loadTaskDetails, selectedTask?.id]);

  async function createAndRun() {
    setError(null);
    setIsRunning(true);
    try {
      const task = await api<Task>("/tasks", {
        method: "POST",
        body: JSON.stringify({ user_prompt: prompt })
      });
      setSelectedTask(task);
      setResults([]);
      setLogs([]);
      setScreenshots([]);
      await api(`/tasks/${task.id}/run`, { method: "POST" });
      await loadTaskDetails(task.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setIsRunning(false);
      await refresh();
    }
  }

  async function stopTask() {
    if (!selectedTask) return;
    setError(null);
    await api(`/tasks/${selectedTask.id}/stop`, { method: "POST" });
    await loadTaskDetails(selectedTask.id);
    await refresh();
  }

  function exportJson() {
    downloadFile("omnibrowse-results.json", JSON.stringify(latestData, null, 2), "application/json");
  }

  function exportCsv() {
    const rows = [["rank", "title", "url", "score", "comments"], ...latestData.map((row, index) => [
      String(row.rank ?? index + 1),
      row.title ?? "",
      row.url ?? "",
      row.score ?? "",
      row.comments ?? ""
    ])];
    const csv = rows.map((row) => row.map(csvCell).join(",")).join("\n");
    downloadFile("omnibrowse-results.csv", csv, "text/csv");
  }

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!selectedTask || !["pending", "running", "queued"].includes(selectedTask.status)) return;
    const timer = window.setInterval(() => {
      loadTaskDetails(selectedTask.id)
        .then((task) => {
          if (!["pending", "running", "queued"].includes(task.status)) {
            refresh();
          }
        })
        .catch((err) => setError(err instanceof Error ? err.message : "Polling failed"));
    }, 1500);
    return () => window.clearInterval(timer);
  }, [loadTaskDetails, refresh, selectedTask]);

  const browserSummary = useMemo(() => {
    if (cdpBrowser) return `${cdpBrowser.browser_name} via CDP`;
    if (browsers.length > 0) return `${browsers[0].browser_name} detected, CDP unavailable`;
    return "No browser detected";
  }, [browsers, cdpBrowser]);

  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-4 px-4 py-4 text-ink sm:px-6">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-semibold tracking-normal">OmniBrowse Agent</h1>
            <StatusPill status={selectedStatus} />
          </div>
          <p className="mt-1 text-sm text-muted">Local browser automation with visible controls, CDP status, logs, screenshots, and exports.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={refresh}
            className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-panel px-3 text-sm shadow-sm"
            title="Refresh"
          >
            <RefreshCw size={16} className={isRefreshing ? "animate-spin" : ""} /> Refresh
          </button>
          <a
            href="http://127.0.0.1:9222/json/version"
            target="_blank"
            className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-panel px-3 text-sm shadow-sm"
          >
            <Wifi size={16} /> CDP
          </a>
        </div>
      </header>

      {error && <div className="rounded-md border border-rust bg-panel px-4 py-3 text-sm text-rust">{error}</div>}

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)]">
        <div className="space-y-4">
          <Panel title="Command" icon={<Bot size={18} />}>
            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              className="min-h-28 w-full resize-y rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-ink"
            />
            <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
              <div className="text-xs text-muted">
                Current control path: <span className="font-medium text-ink">{browserSummary}</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={createAndRun}
                  disabled={isRunning || prompt.trim().length === 0}
                  className="inline-flex h-10 items-center gap-2 rounded-md bg-ink px-4 text-sm text-white"
                >
                  <Play size={16} /> Run
                </button>
                <button
                  onClick={stopTask}
                  disabled={!selectedTask}
                  className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-4 text-sm"
                >
                  <Square size={16} /> Stop
                </button>
              </div>
            </div>
          </Panel>

          <Panel title="Active Session" icon={<Eye size={18} />}>
            <div className="grid gap-3 sm:grid-cols-3">
              <Metric label="Task" value={selectedTask ? `#${selectedTask.id}` : "None"} />
              <Metric label="Browser" value={cdpBrowser?.browser_name ?? "Waiting"} />
              <Metric label="Mode" value={cdpBrowser ? "CDP native" : "Unavailable"} />
            </div>
            <div className="mt-4 overflow-hidden rounded-md border border-line bg-paper">
              {latestScreenshot ? (
                <img
                  src={`${API_BASE}/tasks/${selectedTask?.id}/screenshots/${latestScreenshot.id}`}
                  alt="Latest browser screenshot"
                  className="max-h-[360px] w-full object-contain"
                />
              ) : (
                <div className="flex h-48 items-center justify-center px-4 text-center text-sm text-muted">
                  The latest screenshot will appear here after a run starts.
                </div>
              )}
            </div>
            <div className="mt-3 truncate text-xs text-muted">
              Current URL: <span className="text-ink">{latestScreenshot?.url ?? cdpBrowser?.tabs?.[0]?.url ?? "Not available yet"}</span>
            </div>
          </Panel>
        </div>

        <div className="space-y-4">
          <Panel title="Detected Browsers" icon={<Shield size={18} />}>
            <div className="space-y-2">
              {browsers.length === 0 && <p className="text-sm text-muted">No browser detected yet. Launch Chrome, Edge, or Brave with CDP enabled.</p>}
              {browsers.map((browser, index) => (
                <div key={`${browser.browser_name}-${browser.endpoint_url ?? browser.process_name}-${index}`} className="rounded-md border border-line bg-white p-3 text-sm">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-medium">{browser.browser_name}</div>
                      <div className="mt-1 max-w-sm truncate text-muted">{browser.endpoint_url ?? browser.process_name ?? "visible browser mode"}</div>
                    </div>
                    {browser.cdp_available && <span className="rounded bg-mint px-2 py-1 text-xs font-medium">Selected</span>}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    <Capability label="CDP" enabled={browser.cdp_available} />
                    <Capability label="Extension" enabled={browser.extension_available} />
                    <Capability label="Accessibility" enabled={browser.accessibility_available} />
                    <Capability label="Visual" enabled={browser.visual_fallback_available} />
                  </div>
                  {browser.tabs?.[0] && <div className="mt-2 truncate text-xs text-muted">{browser.tabs[0].title || browser.tabs[0].url}</div>}
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Run Logs" icon={<Terminal size={18} />}>
            <div className="max-h-72 space-y-2 overflow-y-auto pr-1">
              {logs.length === 0 && <p className="text-sm text-muted">Logs will stream into this area after a task is selected or run.</p>}
              {logs.map((log) => (
                <div key={log.id} className="rounded-md border border-line bg-white px-3 py-2 text-xs">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium uppercase text-muted">{log.level}</span>
                    <span className="text-muted">{formatTime(log.created_at)}</span>
                  </div>
                  <div className="mt-1 text-sm">{log.message}</div>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[0.55fr_1.45fr]">
        <Panel title="Tasks" icon={<CheckCircle2 size={18} />}>
          <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
            {tasks.length === 0 && <p className="text-sm text-muted">No tasks yet.</p>}
            {tasks.map((task) => (
              <button
                key={task.id}
                onClick={() => loadTaskDetails(task.id).catch((err) => setError(err instanceof Error ? err.message : "Could not load task"))}
                className={`block w-full rounded-md border p-3 text-left text-sm ${
                  selectedTask?.id === task.id ? "border-ink bg-blue" : "border-line bg-white hover:bg-paper"
                }`}
              >
                <div className="line-clamp-2 font-medium">{task.title}</div>
                <div className="mt-2 flex items-center justify-between gap-2 text-xs text-muted">
                  <span>#{task.id}</span>
                  <StatusPill status={task.status} compact />
                </div>
              </button>
            ))}
          </div>
        </Panel>

        <Panel title="Results" icon={<Globe2 size={18} />}>
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div className="text-sm text-muted">{latestData.length} rows extracted</div>
            <div className="flex gap-2">
              <button onClick={exportCsv} disabled={latestData.length === 0} className="inline-flex h-9 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm">
                <Download size={16} /> CSV
              </button>
              <button onClick={exportJson} disabled={latestData.length === 0} className="inline-flex h-9 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm">
                <FileJson size={16} /> JSON
              </button>
            </div>
          </div>
          <div className="overflow-x-auto rounded-md border border-line">
            <table className="w-full border-collapse bg-white text-left text-sm">
              <thead className="bg-paper">
                <tr className="border-b border-line">
                  <th className="w-16 px-3 py-2">Rank</th>
                  <th className="min-w-80 px-3 py-2">Title</th>
                  <th className="min-w-80 px-3 py-2">URL</th>
                  <th className="w-32 px-3 py-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {latestData.map((row, index) => (
                  <tr key={`${row.url}-${index}`} className="border-b border-line last:border-0">
                    <td className="px-3 py-2">{row.rank ?? index + 1}</td>
                    <td className="px-3 py-2 font-medium">{row.title}</td>
                    <td className="max-w-md truncate px-3 py-2 text-muted">{row.url}</td>
                    <td className="px-3 py-2 text-muted">{row.score ?? "-"}</td>
                  </tr>
                ))}
                {latestData.length === 0 && (
                  <tr>
                    <td className="px-3 py-6 text-muted" colSpan={4}>
                      Run the Hacker News demo to populate this table.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </section>
    </main>
  );
}

function Panel({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="rounded-md border border-line bg-panel p-4 shadow-sm">
      <div className="mb-3 flex items-center gap-2">
        {icon}
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-white p-3">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 truncate text-sm font-medium">{value}</div>
    </div>
  );
}

function Capability({ label, enabled }: { label: string; enabled: boolean }) {
  return <span className={`rounded px-2 py-1 ${enabled ? "bg-mint text-ink" : "bg-paper text-muted"}`}>{label} {enabled ? "on" : "off"}</span>;
}

function StatusPill({ status, compact = false }: { status: string; compact?: boolean }) {
  const tone = status === "completed" ? "bg-mint text-ink" : status === "running" || status === "pending" ? "bg-amber text-ink" : status === "failed" || status === "blocked" ? "bg-red-100 text-rust" : "bg-paper text-muted";
  return <span className={`rounded px-2 py-1 ${compact ? "text-[11px]" : "text-xs"} font-medium ${tone}`}>{status}</span>;
}

function downloadFile(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function csvCell(value: string) {
  return `"${value.replaceAll('"', '""')}"`;
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  }).format(new Date(value));
}
