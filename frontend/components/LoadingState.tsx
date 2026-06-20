export function LoadingState() {
  return <div className="panel grid min-h-64 place-items-center"><div className="text-sm text-[#777d80]">Loading signal data…</div></div>;
}

export function ErrorState({message = "Start the FastAPI backend on port 8000 to load demo data."}: {message?: string}) {
  return <div className="panel border-dashed p-8 text-center"><div className="text-sm font-semibold">The radar API is offline</div><p className="muted mt-2">{message}</p></div>;
}
