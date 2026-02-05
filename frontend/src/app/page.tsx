// frontend/src/app/page.tsx
import Image from "next/image";

interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  task_ref: string;
  created_by: string;
  // Add other fields as needed
}

export default async function Home() {
  let tasks: Task[] = [];
  let error: string | null = null;

  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/tasks/', { cache: 'no-store' }); // Disable caching for fresh data
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    tasks = await response.json();
  } catch (e: any) {
    error = e.message || "Failed to fetch tasks";
    console.error("Error fetching tasks:", e);
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 font-sans dark:bg-black p-4">
      <main className="flex w-full max-w-3xl flex-col items-center justify-between py-8 px-4 bg-white dark:bg-black rounded-lg shadow-md">
        <h1 className="text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50 mb-6">
          SimDecisions Hive Dashboard
        </h1>

        <div className="w-full mb-8">
          <h2 className="text-xl font-bold mb-4 text-black dark:text-zinc-50">Tasks</h2>
          {error && <p className="text-red-500 mb-4">Error: {error}</p>}
          {!error && tasks.length === 0 && (
            <p className="text-zinc-600 dark:text-zinc-400">No tasks found. Create one using the API or CLI!</p>
          )}
          {!error && tasks.length > 0 && (
            <ul className="space-y-4">
              {tasks.map((task) => (
                <li key={task.id} className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg shadow-sm">
                  <h3 className="text-lg font-semibold text-black dark:text-zinc-50">{task.title}</h3>
                  <p className="text-sm text-zinc-700 dark:text-zinc-300">ID: {task.id}</p>
                  <p className="text-sm text-zinc-700 dark:text-zinc-300">Status: <span className={`font-medium ${task.status === 'completed' ? 'text-green-600' : task.status === 'in_progress' ? 'text-blue-600' : 'text-yellow-600'}`}>{task.status}</span></p>
                  <p className="text-sm text-zinc-700 dark:text-zinc-300">Created By: {task.created_by}</p>
                  {task.description && <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-2">{task.description}</p>}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-8 text-center text-sm text-zinc-600 dark:text-zinc-400">
          <p>Powered by SimDecisions Hive Control Plane</p>
          <p>Backend: <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">API Docs</a></p>
        </div>
      </main>
    </div>
  );
}