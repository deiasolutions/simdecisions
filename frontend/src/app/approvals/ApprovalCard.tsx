// frontend/src/app/approvals/ApprovalCard.tsx
"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface Approval {
  id: string;
  created_at: string;
  status: string;
  original_input: string;
  llm_hypothesis: string;
  proposed_hive_code: string;
}

interface ApprovalCardProps {
  approval: Approval;
}

export default function ApprovalCard({ approval }: ApprovalCardProps) {
  const router = useRouter();
  const [isResolving, setIsResolving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResolve = async (decision: 'approved' | 'denied') => {
    setIsResolving(true);
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/approvals/${approval.id}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: decision,
          resolved_by: "human:dave" // Hardcoded for now
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      // Refresh the page to show the updated list of pending approvals
      router.refresh();

    } catch (e: any) {
      setError(e.message || "Failed to resolve approval.");
    } finally {
      setIsResolving(false);
    }
  };

  return (
    <li className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-black dark:text-zinc-50">Original Command:</h3>
        <pre className="bg-gray-100 dark:bg-gray-900 p-2 rounded mt-1 text-sm text-zinc-800 dark:text-zinc-200"><code>{approval.original_input}</code></pre>
      </div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-black dark:text-zinc-50">LLM Hypothesis / Question:</h3>
        <p className="mt-1 text-zinc-700 dark:text-zinc-300">{approval.llm_hypothesis}</p>
      </div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-black dark:text-zinc-50">Proposed Hive Code:</h3>
        <pre className="bg-gray-100 dark:bg-gray-900 p-2 rounded mt-1 text-sm text-zinc-800 dark:text-zinc-200"><code>{approval.proposed_hive_code}</code></pre>
      </div>
      {error && <p className="text-red-500 text-sm mt-4">{error}</p>}
      <div className="flex items-center justify-end space-x-4 mt-6">
        <button
          onClick={() => handleResolve('denied')}
          disabled={isResolving}
          className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
        >
          {isResolving ? 'Resolving...' : 'Deny'}
        </button>
        <button
          onClick={() => handleResolve('approved')}
          disabled={isResolving}
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        >
          {isResolving ? 'Resolving...' : 'Approve'}
        </button>
      </div>
    </li>
  );
}
