import { useEffect, useRef, useState } from 'react';

interface WorkflowRunViewerProps {
  workflow: any;
  input: any;
}

interface RunEvent {
  type?: string;
  node?: string;
  timestamp?: string;
  [key: string]: any;
}

export function WorkflowRunViewer({ workflow, input }: WorkflowRunViewerProps) {
  const [events, setEvents] = useState<RunEvent[]>([]);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!workflow || !input) return;
    const url = `/api/workflows/stream?workflow_json=${encodeURIComponent(JSON.stringify(workflow))}&input_json=${encodeURIComponent(JSON.stringify(input))}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        setEvents((prev) => [...prev, payload]);
      } catch {}
    };

    es.onerror = () => {
      es.close();
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [workflow, input]);

  return (
    <div className="border rounded p-3 bg-white space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Live Execution</h3>
        <span className="text-xs text-gray-500">{events.length} events</span>
      </div>
      <div className="max-h-64 overflow-auto text-xs space-y-1">
        {events.map((ev, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <span className="px-1.5 py-0.5 rounded bg-gray-100">{ev.type || 'event'}</span>
            {ev.node && <span className="text-gray-700">{ev.node}</span>}
            {ev.timestamp && <span className="text-gray-400">{new Date(ev.timestamp).toLocaleTimeString()}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}