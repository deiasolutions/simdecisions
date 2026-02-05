// frontend/src/app/approvals/page.tsx
import ApprovalCard from './ApprovalCard';

interface Approval {
  id: string;
  created_at: string;
  status: string;
  original_input: string;
  llm_hypothesis: string;
  proposed_hive_code: string;
}

export default async function ApprovalsPage() {
  let approvals: Approval[] = [];
  let error: string | null = null;

  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/approvals/pending', { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    approvals = await response.json();
  } catch (e: any) {
    error = e.message || "Failed to fetch approvals";
    console.error("Error fetching approvals:", e);
  }

  return (
    <div className="flex min-h-screen flex-col items-center bg-zinc-50 font-sans dark:bg-black p-4">
      <main className="flex w-full max-w-4xl flex-col items-center py-8 px-4">
        <h1 className="text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50 mb-6">
          Pending Approvals
        </h1>

        <div className="w-full">
          {error && <p className="text-red-500 mb-4">Error: {error}</p>}
          {!error && approvals.length === 0 && (
            <div className="text-center p-8 bg-white dark:bg-gray-800 rounded-lg shadow-md">
              <p className="text-zinc-600 dark:text-zinc-400">No pending approvals found.</p>
            </div>
          )}
          {!error && approvals.length > 0 && (
            <ul className="space-y-6">
              {approvals.map((approval) => (
                <ApprovalCard key={approval.id} approval={approval} />
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}
